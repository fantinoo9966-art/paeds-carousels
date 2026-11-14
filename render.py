"""Turn posts/<slug>/slides.json into 1080x1350 JPEG slides (slide01.jpg, slide02.jpg, ...).

Usage: python agent/render.py posts/<slug>
"""
import html
import json
import re
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
import config  # noqa: E402

HERE = Path(__file__).parent


def rich(text: str) -> str:
    """Escape HTML, then turn **bold** into <strong>."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html.escape(text))


def split2(text: str) -> list[str]:
    parts = [p.strip() for p in text.split("||", 1)]
    return parts + [""] * (2 - len(parts))


def build_context(slide: dict, index: int, total: int) -> dict:
    ctx = {
        "slide": slide, "index": index, "total": total,
        "accent": config.ACCENTS[(index - 1) % len(config.ACCENTS)],
        "brand": config.BRAND_NAME, "handle": config.HANDLE,
        "points": [rich(p) for p in slide.get("points", [])],
    }
    if slide["kind"] == "compare":
        ctx["headers"] = split2(slide.get("subtitle") or "||")
        ctx["rows"] = [[rich(c) for c in split2(p)] for p in slide.get("points", [])]
    if slide["kind"] == "mnemonic":
        mn = []
        for p in slide.get("points", []):
            m = re.match(r"\s*(\S{1,3})\s*[-–:]\s*(.+)", p)
            mn.append((m.group(1), rich(m.group(2))) if m else (p[:1], rich(p[1:])))
        ctx["mn"] = mn
    return ctx


def render(post_dir: Path) -> list[Path]:
    data = json.loads((post_dir / "slides.json").read_text(encoding="utf-8"))
    slides = data["slides"][: config.MAX_SLIDES]
    template = Environment(loader=FileSystemLoader(HERE), autoescape=True).get_template("template.html")

    for old in post_dir.glob("slide*.jpg"):
        old.unlink()

    out = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for i, slide in enumerate(slides, start=1):
            page.set_content(template.render(**build_context(slide, i, len(slides))), wait_until="networkidle")
            page.wait_for_function("window.fitDone === true", timeout=20000)
            path = post_dir / f"slide{i:02d}.jpg"
            page.screenshot(path=str(path), type="jpeg", quality=92)
            out.append(path)
        browser.close()
    return out


if __name__ == "__main__":
    files = render(Path(sys.argv[1]))
    print(f"Rendered {len(files)} slides")
