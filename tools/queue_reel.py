"""Add a finished Reel to the auto-post queue (run on the PC after a Reel is made).

  python tools/queue_reel.py "<video.mp4>" "<CAPTION.txt>" parents|pg [--cover 2.0] [--test]

parents -> posted at the next free 8:00 AM, pg -> at the next free 8:00 PM (one per slot per day, oldest first).
The caption file may be the Desktop "<video> - CAPTION.txt": only the text below the "COPY EVERYTHING BELOW" line is used.
--test puts it in reels/_test/ instead: GitHub uploads it to Instagram to check it works, but posts nothing.

The video goes to the "reel-files" branch (kept to a single small commit, so videos don't pile up);
the caption and settings go to reels/<id>/ on main.
"""
import argparse
import datetime
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BRANCH = "reel-files"


def git(*args, cwd=REPO, check=True) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed:\n{r.stdout}{r.stderr}")
    return r


def caption_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"COPY EVERYTHING BELOW[^\n]*\n", text)
    return (text[m.end():] if m else text).strip() + "\n"


def push_video(video: Path, reel_id: str) -> None:
    url = git("remote", "get-url", "origin").stdout.strip()
    for attempt in range(3):
        tmp = Path(tempfile.mkdtemp(prefix="reelfiles-"))
        try:
            r = git("clone", "-q", "--depth", "1", "--branch", BRANCH, "--single-branch", url, str(tmp / "r"), check=False)
            work = tmp / "r"
            if r.returncode != 0:  # first Reel ever: create the branch
                work.mkdir(parents=True, exist_ok=True)
                git("init", "-q", cwd=work)
                git("remote", "add", "origin", url, cwd=work)
                git("checkout", "-q", "--orphan", BRANCH, cwd=work)
            shutil.copy2(video, work / f"{reel_id}.mp4")
            git("add", f"{reel_id}.mp4", cwd=work)
            git("-c", "user.name=reel-queue", "-c", "user.email=reel-queue@users.noreply.github.com",
                "commit", "-q", "-m", f"Queue {reel_id}", cwd=work)
            if git("push", "-q", "origin", f"HEAD:{BRANCH}", cwd=work, check=False).returncode == 0:
                return
            print("reel-files changed meanwhile, retrying...")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    raise SystemExit("Could not push the video to the reel-files branch.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=Path)
    ap.add_argument("caption", type=Path)
    ap.add_argument("audience", choices=["parents", "pg"])
    ap.add_argument("--cover", type=float, default=0.0, help="cover frame, in seconds")
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    if not a.video.exists() or not a.caption.exists():
        raise SystemExit("Video or caption file not found.")
    if a.video.stat().st_size > 95e6:
        raise SystemExit("Video is over 95 MB; GitHub won't take it. Re-encode it smaller first.")
    cap = caption_text(a.caption).strip()
    if not cap:
        raise SystemExit("Caption is empty: the Reel would be posted without a caption.")
    if len(cap.encode("utf-16-le")) // 2 > 2150:  # Instagram's limit is 2200; keep a margin
        raise SystemExit(f"Caption is too long for Instagram ({len(cap)} characters, max ~2150). Shorten it first.")
    if cap.count("#") > 30:
        raise SystemExit("Caption has more than 30 hashtags; Instagram would reject it.")

    slug = re.sub(r"[^a-z0-9]+", "-", a.video.stem.lower()).strip("-")[:50]
    reel_id = f"{datetime.datetime.now():%Y-%m-%d-%H%M%S}-{slug}"
    slot = "reel_morning" if a.audience == "parents" else "reel_evening"

    git("pull", "-q", "--ff-only", "origin", "main")
    push_video(a.video, reel_id)

    folder = REPO / "reels" / ("_test" if a.test else "") / reel_id
    folder.mkdir(parents=True)
    (folder / "reel.json").write_text(json.dumps({
        "slot": slot, "thumb_ms": int(a.cover * 1000), "source": a.video.name,
        "queued_at": datetime.datetime.now().isoformat(timespec="seconds")}, indent=2), encoding="utf-8")
    (folder / "caption.txt").write_text(caption_text(a.caption), encoding="utf-8")
    git("add", str(folder.relative_to(REPO)))
    git("commit", "-q", "-m", f"{'Test' if a.test else 'Queue'} reel {reel_id}")
    git("pull", "-q", "--rebase", "origin", "main")
    git("push", "-q", "origin", "main")
    when = "test upload (posts nothing)" if a.test else ("next free 8:00 AM" if slot == "reel_morning" else "next free 8:00 PM")
    print(f"Queued {reel_id} -> {when}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
