"""Pick the next topic and ask Gemini (free tier) to write a 6-10 slide carousel.

Writes posts/<slug>/slides.json and posts/<slug>/caption.txt, and prints the slug.
Usage:  python agent/generate.py            (next topic from topics.txt)
        python agent/generate.py "Kawasaki disease"   (force a topic)
"""
import datetime
import json
import os
import re
import sys
import time
from pathlib import Path

from google import genai
from google.genai import types

sys.path.insert(0, str(Path(__file__).parent))
import config  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "posts"
TOPICS_FILE = ROOT / "topics.txt"          # morning: MBBS / NEET-PG
PG_TOPICS_FILE = ROOT / "topics_pg.txt"    # evening: PG (biostatistics, ventilation, social paeds, programmes)

SLIDE_KINDS = ["cover", "points", "compare", "mnemonic", "takeaway", "cta"]

SCHEMA = {
    "type": "object",
    "properties": {
        "topic": {"type": "string"},
        "slides": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "kind": {"type": "string", "enum": SLIDE_KINDS},
                    "emoji": {"type": "string"},
                    "title": {"type": "string"},
                    "subtitle": {"type": "string"},
                    "points": {"type": "array", "items": {"type": "string"}},
                    "highlight": {"type": "string"},
                },
                "required": ["kind", "emoji", "title", "subtitle", "points", "highlight"],
                "additionalProperties": False,
            },
        },
        "caption": {"type": "string"},
        "hashtags": {"type": "array", "items": {"type": "string"}},
        "references": {"type": "array", "items": {"type": "string"}},
        "doctor_check": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["topic", "slides", "caption", "hashtags", "references", "doctor_check"],
    "additionalProperties": False,
}

def build_system(slot: str, fmt: str) -> str:
    s = config.SLOTS[slot]
    return f"""You write Instagram carousels for {config.HANDLE} ("{config.BRAND_NAME}"), run by a paediatrics PG resident in India.
Audience for this post: {s['audience']}.
Depth: {s['level']}.
Format for this post: {fmt}. Shape the slides around this format.

Goal: carousels people SAVE and SHARE with batchmates. Clinically accurate, high-yield, visually scannable.
""" + RULES


RULES = f"""

Accuracy rules (most important):
- Follow current standard sources: Nelson Textbook of Pediatrics, IAP guidelines, WHO, AAP. Use Indian context where relevant (IAP schedules, drug availability).
- Drug doses must include units, route and frequency, and be standard textbook doses. If a fact is uncertain or varies between guidelines, leave it out or say "per IAP" / "per AAP".
- In doctor_check, list every dose, cut-off and number used, plus anything the doctor should double-check before posting.
- In references, list the sources the content is based on (book/guideline name, edition/year if known).

Slide rules:
- {config.MIN_SLIDES} to {config.MAX_SLIDES} slides total. Slide 1 kind="cover", last slide kind="cta".
- Cover: a scroll-stopping hook as the title (max 45 chars, e.g. "5 red flags you must not miss in a febrile child"), subtitle max 70 chars, points empty.
- "points" slides: title max 40 chars, 3-6 points, each point max 95 characters. Use **double asterisks** around the 1-3 key words per point to bold them.
- "compare" slides: title, then 3-6 points in the form "Left side || Right side". subtitle holds the two column headers as "Header A || Header B".
- "mnemonic" slide: title is the mnemonic word, points are "LETTER - meaning".
- "takeaway": one-line exam pearl in highlight, 2-4 points.
- highlight: an optional one-line "Exam pearl" or "Red flag" (max 90 chars) shown in a coloured box; empty string if none.
- cta slide: title like "Save this for your exams 🔖", subtitle "Follow {config.HANDLE} for more", points 2-3 short lines (e.g. "Share with your PG batch", "Comment the next topic you want"), highlight empty.
- emoji: one relevant emoji per slide.
- No patient-identifying information. Educational content only, not individual medical advice.

Caption: a hook line, 3-5 short lines summarising value, a question to drive comments, "Save 🔖 & share with a batchmate", then a short disclaimer line "For education only; follow local protocols." Max 1500 characters, no hashtags inside the caption.
Hashtags: 15-25 relevant ones (mix big like #pediatrics #neetpg and niche like the topic), each starting with #.
"""


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50]


def used_topics() -> set[str]:
    used = set()
    for f in POSTS.glob("*/slides.json"):
        try:
            used.add(json.loads(f.read_text(encoding="utf-8"))["topic"].strip().lower())
        except Exception:
            pass
    return used


def next_topic(path: Path = TOPICS_FILE) -> str | None:
    used = used_topics()
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        t = line.strip()
        if t and not t.startswith("#") and t.lower() not in used:
            return t
    return None


def clean(data: dict) -> dict:
    """Check the model's JSON has everything the renderer needs; fill safe defaults."""
    if not isinstance(data, dict) or not isinstance(data.get("slides"), list):
        raise ValueError("no slides in response")
    slides = []
    for s in data["slides"]:
        if not isinstance(s, dict) or not s.get("title"):
            continue
        kind = s.get("kind") if s.get("kind") in SLIDE_KINDS else "points"
        slides.append({
            "kind": kind,
            "emoji": str(s.get("emoji", "")),
            "title": str(s["title"]),
            "subtitle": str(s.get("subtitle", "") or ""),
            "points": [str(p) for p in (s.get("points") or [])][:7],
            "highlight": str(s.get("highlight", "") or ""),
        })
    if len(slides) < 3:
        raise ValueError("too few valid slides")
    slides[0]["kind"] = "cover"
    data["slides"] = slides
    data["topic"] = str(data.get("topic") or slides[0]["title"])
    for key in ("hashtags", "references", "doctor_check"):
        data[key] = [str(x) for x in (data.get(key) or [])]
    data["caption"] = str(data.get("caption") or slides[0]["title"])
    return data


FACT_CHECK = """You are a strict professor of paediatrics checking a draft Instagram carousel before it is posted publicly
under a doctor's name, with NO human review. Check every fact, age cut-off, dose, unit, frequency and number against
Nelson Textbook of Pediatrics and current IAP / WHO / AAP guidance.
- Correct anything wrong. If something is doubtful or varies between sources and cannot be stated safely, remove it or
  qualify it ("per IAP"). Never invent references.
- Remove made-up mnemonics that are confusing; keep good ones.
- Keep the same JSON structure, style, slide count range and length limits.
- Replace doctor_check with a short list of what you changed (or "No changes needed").
Return the full corrected carousel JSON.

Draft:
"""


def ask_gemini(request: str, system: str, schema: dict | None = None, validate=None) -> dict:
    client = genai.Client()  # reads GEMINI_API_KEY
    schema = schema or SCHEMA
    validate = validate or clean
    prompt = (
        f"{request}\n\nReply with ONLY a JSON object matching this JSON schema:\n"
        f"{json.dumps(schema)}"
    )
    errors = []
    for model in config.GEMINI_MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system,
                        response_mime_type="application/json",
                        temperature=0.6,
                    ),
                )
                data = validate(json.loads(response.text))
                print(f"Written by {model}", file=sys.stderr)
                return data
            except Exception as e:  # model not available, quota, bad JSON: try again / next model
                errors.append(f"{model}: {e}")
                if "not found" in str(e).lower() or "404" in str(e):
                    break
                time.sleep(10)
    sys.exit("All Gemini models failed:\n" + "\n".join(errors))


def main() -> None:
    slot = os.environ.get("SLOT", "").strip() or "morning"
    if slot not in config.SLOTS:
        slot = "morning"
    count = len([p for p in POSTS.glob("*/slides.json")
                 if json.loads(p.read_text(encoding="utf-8")).get("slot") != "drug"])
    formats = config.SLOTS[slot]["formats"]
    fmt = formats[(count // 2) % len(formats)]
    theme = config.THEME_ORDER[count % len(config.THEME_ORDER)]
    system = build_system(slot, fmt)

    forced = " ".join(sys.argv[1:]).strip() or os.environ.get("TOPIC", "").strip()
    topic = forced or next_topic(TOPICS_FILE if slot == "morning" else PG_TOPICS_FILE)
    if topic:
        request = f"Write the carousel on this topic: {topic}"
    else:
        done = "; ".join(sorted(used_topics())) or "none"
        request = (
            f"Pick a new paediatrics topic that suits this audience and format and has NOT been covered yet, "
            f"and write the carousel. Already covered: {done}"
        )
    print(f"Slot: {slot} | format: {fmt} | theme: {theme} | topic: {topic or 'model picks'}", file=sys.stderr)

    data = ask_gemini(request, system)
    # Second pass: strict fact-check, since posts go out without human review.
    try:
        checked = ask_gemini(FACT_CHECK + json.dumps(data, ensure_ascii=False), system)
        if len(checked["slides"]) >= 3:
            data = checked
            print("Fact-check pass applied", file=sys.stderr)
    except SystemExit:
        print("Fact-check pass failed; using first draft", file=sys.stderr)
    data.update({"slot": slot, "format": fmt, "theme": theme})
    if topic:
        data["topic"] = topic  # keep the exact list wording so it is never repeated

    slides = data["slides"][: config.MAX_SLIDES]
    if len(slides) < 2:
        sys.exit("Too few slides were generated.")
    data["slides"] = slides

    slug = f"{datetime.date.today():%Y-%m-%d}-{slugify(data['topic'])}"
    out = POSTS / slug
    out.mkdir(parents=True, exist_ok=True)
    (out / "slides.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    tags = " ".join(h if h.startswith("#") else f"#{h}" for h in data["hashtags"][:25])
    caption = f"{data['caption'].strip()}\n.\n.\n{tags}"
    (out / "caption.txt").write_text(caption[:2200], encoding="utf-8")

    print(slug)


if __name__ == "__main__":
    main()
