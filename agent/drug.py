"""Drug of the Day: one-slide post (name, class, mechanism, uses, paediatric dose).

Doses come ONLY from the encrypted PedDose source (data/drugs.enc, key in DRUGS_KEY).
Writes posts/<date>-drug-<name>/slides.json + caption.txt and prints the slug.
Usage: python agent/drug.py            (next drug in order)
       python agent/drug.py "AMOXICILLIN"   (force a drug)
"""
import datetime
import json
import os
import sys
from pathlib import Path

from cryptography.fernet import Fernet

sys.path.insert(0, str(Path(__file__).parent))
import config  # noqa: E402
from due import ist_today  # noqa: E402
from generate import POSTS, ask_gemini, slugify  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

SCHEMA = {
    "type": "object",
    "properties": {
        "drug_name": {"type": "string"},
        "aka": {"type": "string"},
        "drug_class": {"type": "string"},
        "moa": {"type": "string"},
        "uses": {"type": "array", "items": {"type": "string"}},
        "doses": {"type": "array", "items": {"type": "string"}},
        "caution": {"type": "string"},
        "caption": {"type": "string"},
        "hashtags": {"type": "array", "items": {"type": "string"}},
        "doctor_check": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["drug_name", "aka", "drug_class", "moa", "uses", "doses", "caution", "caption", "hashtags", "doctor_check"],
    "additionalProperties": False,
}

SYSTEM = f"""You make a single-slide "Drug of the Day" Instagram post for {config.HANDLE}, a paediatrics education page
for MBBS students, NEET-PG aspirants and paediatric PGs in India.

You are given the SOURCE TEXT for one drug from a paediatric drug handbook. Rules:
- DOSES: take them ONLY from the source text. Never add a dose, frequency, route or maximum that is not in it.
  Rewrite them briefly in your own words (do not copy sentences), e.g. "Child: 25-50 mg/kg/day PO ÷ 8-12 hrly; max 3 g/day".
  Include route and frequency. 2-4 dose lines, choosing the most common paediatric indications/ages. Use "mg/kg/day" style.
- drug_name: the name used in India (INN), e.g. Paracetamol not Acetaminophen, Salbutamol not Albuterol.
  aka: the other common name if different (else empty).
- drug_class: short (max 50 chars). moa: mechanism of action in one plain sentence (max 140 chars).
- uses: 3-4 short common paediatric indications (max 45 chars each).
- caution: one key side effect / caution / monitoring point (max 90 chars).
- caption: hook line, 2-3 lines of exam/ward relevance, a question for comments, "Save 🔖 for your ward rounds",
  and "Doses for education only; always verify with your unit protocol." Max 900 characters, no hashtags in it.
- hashtags: 12-18, including #DrugOfTheDay #pediatrics #neetpg and the drug name.
- doctor_check: list the doses you used, each with the source line it came from.
"""

CHECK = """Strictly verify this Drug of the Day draft against the SOURCE TEXT below.
Every dose, unit, route, frequency and maximum in "doses" must match the source exactly in meaning; fix or delete any
that do not. Check that drug_class, moa, uses and caution are correct standard pharmacology. Keep the same JSON fields and
length limits. Replace doctor_check with what you changed (or "No changes needed"). Return the full corrected JSON.
"""


def load_drugs() -> list[dict]:
    blob = (ROOT / "data" / "drugs.enc").read_bytes()
    return json.loads(Fernet(os.environ["DRUGS_KEY"].strip().encode()).decrypt(blob))


def source_text(d: dict) -> str:
    remarks = "\n".join(d.get("remarks") or [])
    return (f"NAME: {d['name']}\nCLASS: {d['class']}\nHOW SUPPLIED: {d['supplied']}\n"
            f"DOSING:\n{d['dosing']}\nREMARKS:\n{remarks}")


def ask(prompt: str) -> dict:
    data = ask_gemini(prompt, SYSTEM, schema=SCHEMA, validate=validate)
    return data


def validate(data: dict) -> dict:
    for k in SCHEMA["required"]:
        if k not in data:
            raise ValueError(f"missing {k}")
    if not data["doses"]:
        raise ValueError("no doses")
    data["uses"] = [str(u) for u in data["uses"]][:4]
    data["doses"] = [str(u) for u in data["doses"]][:4]
    data["hashtags"] = [str(h) for h in data["hashtags"]]
    data["doctor_check"] = [str(h) for h in data["doctor_check"]]
    return data


def main() -> None:
    drugs = load_drugs()
    done = [p for p in POSTS.glob("*/slides.json")
            if json.loads(p.read_text(encoding="utf-8")).get("slot") == "drug"]
    forced = " ".join(sys.argv[1:]).strip().upper() or os.environ.get("TOPIC", "").strip().upper()
    if forced:
        drug = next((d for d in drugs if d["name"].upper().startswith(forced)), None)
        if not drug:
            sys.exit(f"Drug not in source file: {forced}")
    else:
        drug = drugs[len(done) % len(drugs)]
    src = source_text(drug)
    print(f"Drug: {drug['name']}", file=sys.stderr)

    data = ask(f"SOURCE TEXT:\n{src}\n\nWrite the Drug of the Day post.")
    try:
        data = ask(CHECK + f"\nSOURCE TEXT:\n{src}\n\nDRAFT:\n{json.dumps(data, ensure_ascii=False)}")
        print("Fact-check pass applied", file=sys.stderr)
    except SystemExit:
        print("Fact-check pass failed; using first draft", file=sys.stderr)

    theme = config.THEME_ORDER[len(done) % len(config.THEME_ORDER)]
    slide = {
        "kind": "drug", "emoji": "💊", "title": data["drug_name"], "subtitle": data["aka"],
        "points": [], "highlight": data["caution"],
        "drug_class": data["drug_class"], "moa": data["moa"], "uses": data["uses"], "doses": data["doses"],
    }
    post = {
        "topic": f"Drug of the Day: {data['drug_name']}", "slot": "drug", "theme": theme, "ist_date": ist_today(),
        "slides": [slide], "caption": data["caption"], "hashtags": data["hashtags"],
        "references": [f"PedDose / paediatric drug handbook, p.{drug.get('source_page')}"],
        "doctor_check": data["doctor_check"], "source_drug": drug["name"],
    }

    slug = f"{ist_today()}-drug-{slugify(data['drug_name'])}"
    out = POSTS / slug
    out.mkdir(parents=True, exist_ok=True)
    (out / "slides.json").write_text(json.dumps(post, indent=2, ensure_ascii=False), encoding="utf-8")
    tags = " ".join(h if h.startswith("#") else f"#{h}" for h in data["hashtags"][:20])
    (out / "caption.txt").write_text(f"{data['caption'].strip()}\n.\n.\n{tags}"[:2200], encoding="utf-8")
    print(slug)


if __name__ == "__main__":
    main()
