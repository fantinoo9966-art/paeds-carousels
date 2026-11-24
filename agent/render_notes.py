"""Render a carousel in the 'notes' look (notebook paper, handwritten accents, taped cards).

python agent/render_notes.py <post_dir>      (reads <post_dir>/slides.json with "style": "notes")

Markup in any text field:  **bold**   ==marker highlight== (==y:yellow== ==t:teal==)   ~~wavy red underline~~   {red}handwritten red{/red}
Slide kinds: cover, card, number, table, mnemonic, points (see template_notes.html).
"""
import json
import re
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent


def rich(t):
    if isinstance(t, list):
        return [rich(x) for x in t]
    if isinstance(t, dict):
        return {k: rich(v) for k, v in t.items()}
    if not isinstance(t, str):
        return t
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    hl = {"y": "#F7DB72", "t": "#A8E3D8", "c": "#F4ADA2"}
    t = re.sub(r"==([ytc]):(.+?)==", lambda m: f'<mark style="--hl:{hl[m.group(1)]}">{m.group(2)}</mark>', t)
    t = re.sub(r"==(.+?)==", r"<mark>\1</mark>", t)
    t = re.sub(r"~~(.+?)~~", r'<span class="u">\1</span>', t)
    t = re.sub(r"\{red\}(.+?)\{/red\}", r'<span style="font:700 1.25em Caveat;color:var(--red)">\1</span>', t)
    return t


NOTES_KINDS = {"card", "number", "table", "mnemonic"}
TINTS = ["#A8E3D8", "#F4ADA2", "#F7DB72"]


def from_classic(slides: list[dict]) -> list[dict]:
    """Turn Gemini's classic slides (cover/points/compare/takeaway/cta) into notebook slides."""
    out = []
    for s in slides:
        k, pts = s.get("kind"), s.get("points") or []
        if k == "cover":
            out.append({"kind": "cover", "kicker": "MBBS · NEET-PG high-yield", "title": s.get("title", ""),
                        "sub": s.get("subtitle", "")})
        elif k == "compare":
            heads = [h.strip() for h in (s.get("subtitle") or "").split("||")]
            rows = []
            for p in pts:
                cells = [c.strip() for c in p.split("||")]
                rows.append([""] + (cells + [""])[:2])
            cols = [{"text": (heads + ["", ""])[i] if len(heads) == 2 else "", "color": TINTS[i]} for i in range(2)]
            out.append({"kind": "table", "title": s.get("title", ""), "cols": cols, "rows": rows,
                        "hand": s.get("highlight", "")})
        elif k == "cta":
            out.append({"kind": "mnemonic", "kicker": "before you swipe away…", "lines": [s.get("title", "")],
                        "actions": pts, "sign": "— Pediatrics Made Simple"})
        else:  # points, takeaway, anything else
            out.append({"kind": "points", "title": s.get("title", ""), "tagline": (s.get("subtitle") or "").lower(),
                        "bullets": pts, "hand": s.get("highlight", "")})
    return out


def render(post_dir: Path) -> list[Path]:
    data = json.loads((post_dir / "slides.json").read_text(encoding="utf-8"))
    slides = data["slides"]
    if not any(s.get("kind") in NOTES_KINDS for s in slides):
        slides = from_classic(slides)
    tpl = Environment(loader=FileSystemLoader(HERE), autoescape=False).get_template("template_notes.html")
    for old in post_dir.glob("slide*.jpg"):
        old.unlink()
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(slides):
            page.set_content(tpl.render(s=rich(s), i=i, n=len(slides)), wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(300)
            path = post_dir / f"slide{i + 1:02d}.jpg"
            page.screenshot(path=str(path), type="jpeg", quality=92)
            out.append(path)
        b.close()
    cap = data.get("caption", "").strip()
    if cap and not (post_dir / "caption.txt").exists():  # generate.py writes its own caption.txt
        refs = data.get("references") or []
        tail = ("\n\n📚 Refs: " + " · ".join(refs)) if refs else ""
        tags = " ".join(data.get("hashtags", []))
        (post_dir / "caption.txt").write_text(f"{cap}{tail}\n\n{tags}\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    print(f"Rendered {len(render(Path(sys.argv[1])))} slides")
