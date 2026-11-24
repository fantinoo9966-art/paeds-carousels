"""Write the next Reel script with Gemini (used only when no hand-written script is waiting).

python agent/reel_script.py parents|pg      -> writes reels/scripts/<aud>/auto-<date>-<slug>.json, prints its path
Two passes like the carousels: draft, then a strict fact-check. The script format is reelkit/src/types.ts.
"""
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import config  # noqa: E402
from due import ist_today  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "reels" / "scripts"
ICONS = ("newborn lungs sleep bottle rash bolt calendar shirt water syrup ice pill siren eye packet drop lips tear urine "
         "sunken zinc breast bowl soda blood noglass clock cal lamp tube bulb warn stool camera liver dna shield nosedrop "
         "honey cup kettle rubjar heart germ").split()
MOODS = ["hot", "sleepy", "happy", "think", "doctor", "ouch", "sneeze", "queasy"]


def used_topics(aud: str) -> set[str]:
    out = set()
    for f in (SCRIPTS / aud).glob("*.json"):
        try:
            out.add(json.loads(f.read_text(encoding="utf-8"))["topic"].strip().lower())
        except Exception:
            pass
    return out


def next_topic(aud: str) -> tuple[str, str] | None:
    used = used_topics(aud)
    for line in (ROOT / "reels" / f"topics_{aud}.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        system, topic = (line.split("|", 1) + [""])[:2] if "|" in line else ("", line)
        system, topic = system.strip(), topic.strip()
        short = topic.split(":")[0].strip().lower()
        if topic.lower() not in used and short not in used and not any(short in u or u in short for u in used):
            return system, topic
    return None


def system_prompt(aud: str) -> str:
    who = ("PARENTS in India: simple English (class 6 reading level), warm, practical; home care, what not to do, "
           "red flags for when to see a doctor. No drug doses except 'as your doctor advises'."
           if aud == "parents" else
           "PAEDIATRIC PG RESIDENTS / NEET-PG aspirants: exam- and ward-focused; definitions, criteria, classification, "
           "investigations, management with doses (units, route, frequency), mnemonics, high-yield pearls, guideline names.")
    return f"""You write short animated Instagram Reels (no voice, text on screen) for {config.HANDLE} ("{config.BRAND_NAME}"),
run by a paediatrics PG resident in India. Audience: {who}

Output ONE JSON object (the Reel script):
{{"audience": "{aud}", "topic": str, "title": str, "scenes": [scene...], "caption": str}}
Scene types (use 6 to 9 scenes; first "hook", last "cta"):
- {{"type":"hook","title":str<=40 chars,"sub":str<=60 (optional),"mood":one of {MOODS},"icon":icon name,"hand":short handwritten line<=24}}
- {{"type":"big","text":str<=60,"sub":str<=80,"visual":{{"kind":"number","value":"60%","label":str}} or {{"kind":"calendar","from":1,"to":14,"label":"DAY"}} or {{"kind":"icon","name":icon}} or {{"kind":"drop"}} or {{"kind":"clock"}}}}
- {{"type":"split","title":str<=30,"left":{{"title":str<=16,"icon":icon,"lines":[2-3 strs<=40],"verdict":str<=20}},"right":{{same}}}}
- {{"type":"list","title":str<=36,"style":"rows"|"notes"|"chat"|"wheel"|"flags"|"steps"|"chips","tone":"good"|"bad"|"alert"|"neutral","items":[{{"text":str<=60,"sub":str<=40 optional,"icon":icon optional}}]}}
   rows: 3-7 items · notes: exactly 4 short "don'ts" (tone bad) · wheel: 3-5 items each with an icon (tone good) ·
   flags: 4-7 red flags (tone alert) · chat: 4-6 "see a doctor if" items · steps: 3-6 ordered steps · chips: 5-9 very short items (<=28)
- {{"type":"cards","title":str<=30,"cards":[2-4 cards {{"title":str<=30,"lines":[1-3 strs<=60]}}]}}   (best for PG)
- {{"type":"pearls","title":str<=24,"items":[2-4 strs<=90]}}
- {{"type":"cta","line":str with one *highlight*,"sub":str<=40}}
Allowed icon names ONLY: {", ".join(ICONS)}.
Markup: in titles wrap 1-2 key words in *single stars* (highlight). In body text wrap key numbers/terms in **double stars**.
Variety: use at least 4 different scene types and at least 2 different list styles. Parents Reels: about 6-7 scenes, include
"Please don't" (notes) and red flags (flags or chat). PG Reels: 7-9 scenes, mostly cards/rows/chips/split + pearls.
Caption: hook line with emoji, the key content as short emoji bullet sections (all facts shown in the Reel), "📌 Save this",
"Follow {config.HANDLE}", a disclaimer line ({"For information only. Always consult your doctor." if aud == "parents" else "For medical education. Verify with current guidelines and your unit protocol."}),
then 6-8 hashtags at the end. Max 1900 characters in total.

Accuracy (most important): follow Nelson, IAP, WHO, AAP, NICE and the latest named guideline. Indian context. If a fact
varies between guidelines or is uncertain, leave it out. Never invent numbers or references."""


FACT_CHECK = """You are a strict professor of paediatrics checking this Reel script before it is posted publicly under a
doctor's name with NO human review. Check every fact, cut-off, dose, unit and number against Nelson and current
IAP/WHO/AAP/NICE guidance. Correct anything wrong; remove anything doubtful. Keep the same JSON structure, scene types,
length limits, icon names and markup. Return the full corrected JSON only.

Script:
"""


def validate(d: dict) -> dict:
    if not isinstance(d, dict) or not isinstance(d.get("scenes"), list) or len(d["scenes"]) < 5:
        raise ValueError("too few scenes")
    scenes = []
    for s in d["scenes"]:
        t = s.get("type")
        if t == "hook" and s.get("title"):
            s["mood"] = s.get("mood") if s.get("mood") in MOODS else "think"
            if s.get("icon") not in ICONS:
                s.pop("icon", None)
        elif t == "big" and s.get("text"):
            v = s.get("visual") or {}
            if v.get("kind") == "icon" and v.get("name") not in ICONS:
                s["visual"] = {"kind": "drop"}
        elif t == "split" and s.get("left", {}).get("lines") and s.get("right", {}).get("lines"):
            for side in ("left", "right"):
                s[side]["lines"] = s[side]["lines"][:3]
                if s[side].get("icon") not in ICONS:
                    s[side].pop("icon", None)
        elif t == "list" and s.get("items"):
            s["items"] = [i for i in s["items"] if isinstance(i, dict) and i.get("text")][:7]
            for i in s["items"]:
                if i.get("icon") not in ICONS:
                    i.pop("icon", None)
            if s.get("style") == "wheel" and not all(i.get("icon") for i in s["items"]):
                s["style"] = "rows"
            if len(s["items"]) < 2:
                continue
        elif t == "cards" and s.get("cards"):
            s["cards"] = [{"title": k["title"], "lines": k["lines"][:3]} for k in s["cards"][:4] if k.get("title") and k.get("lines")]
        elif t == "pearls" and s.get("items"):
            s["items"] = [str(x) for x in s["items"][:4]]
        elif t == "cta":
            pass
        else:
            continue
        scenes.append(s)
    if not scenes or scenes[0]["type"] != "hook":
        raise ValueError("first scene must be the hook")
    if scenes[-1]["type"] != "cta":
        scenes.append({"type": "cta"})
    d["scenes"] = scenes[:10]
    cap = str(d.get("caption", "")).strip()
    if len(cap.encode("utf-16-le")) // 2 > 2100 or len(cap) < 200:
        raise ValueError(f"caption length {len(cap)} not in 200..2100")
    if cap.count("#") > 10:
        raise ValueError("too many hashtags")
    return d


def write(aud: str) -> Path:
    from generate import ask_gemini  # needs google-genai

    nt = next_topic(aud)
    if not nt:
        sys.exit(f"No unused {aud} topic left in reels/topics_{aud}.txt")
    system, topic = nt
    sysmsg = system_prompt(aud)
    data = ask_gemini(f"Write the Reel script on: {topic}", sysmsg, schema={"type": "object"}, validate=validate)
    try:
        data = ask_gemini(FACT_CHECK + json.dumps(data, ensure_ascii=False), sysmsg, schema={"type": "object"}, validate=validate)
        print("Fact-check pass applied", file=sys.stderr)
    except SystemExit:
        print("Fact-check pass failed; using first draft", file=sys.stderr)
    data["audience"] = aud
    data["topic"] = topic
    data["seed"] = random.randint(0, 59)
    data["cover_s"] = 2 if aud == "parents" else 3
    data["auto"] = True
    styles = ["lofi", "jazzhop", "arp", "studypiano"] if aud == "pg" else ["bright", "marimba", "piano", "funk"]
    data["music"] = styles[len(list((SCRIPTS / aud).glob("*.json"))) % len(styles)]  # rotate music styles
    if aud == "pg":
        n = sum(1 for f in (SCRIPTS / "pg").glob("*.json")
                if json.loads(f.read_text(encoding="utf-8")).get("system", "").upper() == system.upper()) + 1
        data["system"] = system
        data.setdefault("tab", f"PG NOTES · {system.upper()} {n:02d}")
        data["tab"] = f"PG NOTES · {system.upper()} {n:02d}"
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:40]
    data.setdefault("title", f"{topic.split(':')[0]} Reel - {'Parents' if aud == 'parents' else 'PG'}")
    out = SCRIPTS / aud / f"auto-{ist_today()}-{slug}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


if __name__ == "__main__":
    print(write(sys.argv[1]).relative_to(ROOT).as_posix())
