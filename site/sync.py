"""Copy everything generated in this project into the website's own content folder.

Usage:  python site/sync.py      (then python site/build.py, check, push)

The website does NOT look at Instagram. It shows whatever we generate here:
  - carousels in  paeds-carousels/posts/<slug>/       (slides.json + slide*.jpg)
  - carousels in  Manual posts/<slug>/                (slides.json + slide*.jpg)
  - long videos in youtube-videos/<name>/             (final *-video-*.mp4 + YOUTUBE-UPLOAD.md)
Everything lands in site/content/. To keep something off the site, add its
folder name to "hide" in site/site.json.
"""
import json
import re
import shutil
import subprocess
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PROJECT = REPO.parent
CONTENT = HERE / "content"
CFG = json.loads((HERE / "site.json").read_text(encoding="utf-8"))
HIDE = set(CFG.get("hide") or [])


def note_date(folder: Path, data: dict) -> str:
    if data.get("ist_date"):
        return data["ist_date"][:10]
    m = re.match(r"(\d{4}-\d{2}-\d{2})", folder.name)
    if m:
        return m.group(1)
    return date.fromtimestamp((folder / "slides.json").stat().st_mtime).isoformat()


def sync_notes():
    out = CONTENT / "notes"
    out.mkdir(parents=True, exist_ok=True)
    sources = [REPO / "posts", PROJECT / "Manual posts"]
    seen = []
    for src in sources:
        if not src.exists():
            continue
        for d in sorted(src.iterdir()):
            sj = d / "slides.json"
            if not (d.is_dir() and sj.exists()) or d.name in HIDE:
                continue
            data = json.loads(sj.read_text(encoding="utf-8"))
            o = out / d.name
            o.mkdir(exist_ok=True)
            for old in o.glob("slide*.jpg"):
                old.unlink()
            shutil.copy(sj, o / "slides.json")
            for im in sorted(d.glob("slide*.jpg")):
                shutil.copy(im, o / im.name)
            (o / "meta.json").write_text(json.dumps({"date": note_date(d, data)}, indent=2), encoding="utf-8")
            seen.append(d.name)
    # anything hidden since the last sync comes off the site
    for o in out.iterdir():
        if o.name in HIDE:
            shutil.rmtree(o)
    return seen


def parse_upload_md(md: str):
    title = re.search(r"^## Title\s*\n+(.+)$", md, re.M)
    desc = re.search(r"## Description.*?```\s*\n(.*?)```", md, re.S)
    body = desc.group(1) if desc else ""
    chapters = re.findall(r"^(\d+:\d{2})\s+(.+)$", body, re.M)
    intro = []
    for para in body.split("\n\n"):
        p = para.strip()
        if not p or p.startswith(("Chapters", "In this video", "📸", "🔔", "#", "This video is for")):
            continue
        if re.match(r"^\d+:\d{2}", p):
            continue
        intro.append(p)
        if len(intro) == 2:
            break
    points = re.findall(r"^•\s*(.+)$", body, re.M)
    return (title.group(1).strip() if title else ""), intro, chapters, points


def sync_videos():
    out = CONTENT / "videos"
    out.mkdir(parents=True, exist_ok=True)
    done = []
    vroot = PROJECT / "youtube-videos"
    if not vroot.exists():
        return done
    for d in sorted(vroot.iterdir()):
        up = d / "YOUTUBE-UPLOAD.md"
        finals = [p for p in d.glob("*-video-*.mp4") if "preview" not in p.name.lower()]
        if not (d.is_dir() and up.exists() and finals) or d.name in HIDE:
            continue  # only finished videos (final file + upload notes)
        title, intro, chapters, points = parse_upload_md(up.read_text(encoding="utf-8"))
        o = out / d.name
        o.mkdir(exist_ok=True)
        src = finals[0]
        if not (o / "video.mp4").exists() or (o / "video.mp4").stat().st_mtime < src.stat().st_mtime:
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf", "scale=1280:-2",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "27", "-c:a", "aac", "-b:a", "96k",
                            "-movflags", "+faststart", str(o / "video.mp4")], check=True)
        thumbs = sorted(d.glob("*thumbnail*.png")) + sorted(d.glob("*thumbnail*.jpg"))
        if thumbs and not (o / "thumb.jpg").exists():
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(thumbs[0]), "-vf", "scale=960:-2",
                            "-q:v", "4", str(o / "thumb.jpg")], check=True)
        old = json.loads((o / "meta.json").read_text(encoding="utf-8")) if (o / "meta.json").exists() else {}
        meta = {
            "title": title or d.name,
            "date": old.get("date") or datetime.fromtimestamp(src.stat().st_mtime).date().isoformat(),
            "audience": old.get("audience", "parents"),
            "intro": intro, "chapters": chapters, "points": points,
            "youtube": old.get("youtube", ""),  # set this by hand once it is on YouTube
        }
        (o / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        done.append(d.name)
    return done


def strip_instagram_from_reels():
    for mj in (CONTENT / "reels").glob("*/meta.json"):
        m = json.loads(mj.read_text(encoding="utf-8"))
        if m.pop("instagram", None) is not None:
            mj.write_text(json.dumps(m, indent=2), encoding="utf-8")


if __name__ == "__main__":
    n = sync_notes()
    v = sync_videos()
    strip_instagram_from_reels()
    print(f"Synced {len(n)} notes and {len(v)} videos into {CONTENT}")
    for name in n + v:
        print("  ", name)
