"""Post the next queued Reel (a finished .mp4 made in the Video Editor) to Instagram.

Queue layout:
  main branch:       reels/<id>/reel.json   {"slot": "reel_morning" | "reel_evening", "thumb_ms": 2000}
                     reels/<id>/caption.txt
                     reels/<id>/published.json   (written after posting)
  reel-files branch: <id>.mp4                (only Reels still waiting; removed after posting so the repo stays small)

Reels are posted oldest id first, one per slot per day. The video is sent with Instagram's resumable upload
(the bytes go straight from the GitHub runner); if that fails, Instagram downloads it from the public repo.

Usage:
  python agent/publish_reel.py <slot> <files_dir>             post the next Reel for this slot, print its id
  python agent/publish_reel.py <slot> <files_dir> --dry-run   upload and let Instagram process it, but DON'T post
  python agent/publish_reel.py --pending <slot>               print the id of the next Reel (or nothing)
  python agent/publish_reel.py --failed <id>                  note a failed try (2 failures in a day = skip till tomorrow)
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
REELS = ROOT / "reels"
SLOTS = ("reel_morning", "reel_evening")


def pending(slot: str) -> Path | None:
    """First queued Reel for this slot that is not posted yet. Standard library only."""
    if not REELS.exists():
        return None
    for d in sorted(p for p in REELS.iterdir() if p.is_dir() and not p.name.startswith("_")):
        meta = d / "reel.json"
        if not meta.exists() or (d / "published.json").exists():
            continue
        try:
            if json.loads(meta.read_text(encoding="utf-8")).get("slot") == slot:
                return d
        except Exception:
            continue
    return None


def failures_today(reel_dir: Path, today: str) -> int:
    f = reel_dir / "failures.json"
    try:
        return json.loads(f.read_text(encoding="utf-8")).count(today) if f.exists() else 0
    except Exception:
        return 0


def note_failure(reel_dir: Path, today: str) -> None:
    f = reel_dir / "failures.json"
    try:
        days = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
    except Exception:
        days = []
    f.write_text(json.dumps(days + [today]), encoding="utf-8")


def posted_today(slot: str, today: str) -> bool:
    if not REELS.exists():
        return False
    for f in REELS.glob("*/published.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("slot") == slot and data.get("ist_date") == today and not data.get("dry_run"):
            return True
    return False


def publish_reel(reel_dir: Path, video: Path, slot: str, dry_run: bool = False) -> dict:
    import requests

    sys.path.insert(0, str(Path(__file__).parent))
    import config
    import publish as ig
    from due import ist_today

    if not video.exists():
        raise SystemExit(f"Video file not found: {video} (was it pushed to the reel-files branch?)")
    meta = json.loads((reel_dir / "reel.json").read_text(encoding="utf-8"))
    caption = (reel_dir / "caption.txt").read_text(encoding="utf-8").strip()[:2200]
    me = ig.connect()
    user = ig.ig_user_id()
    token = os.environ["IG_ACCESS_TOKEN"].strip()
    print(f"Reel {reel_dir.name} as @{me.get('username')} via {ig.API}{' (DRY RUN: will not post)' if dry_run else ''}")

    params = dict(media_type="REELS", caption=caption, share_to_feed="true",
                  thumb_offset=str(int(meta.get("thumb_ms", 0))))
    container, method, first_error = None, "resumable", ""
    try:  # 1) resumable upload: send the file bytes directly
        container = ig.call("POST", f"{user}/media", upload_type="resumable", **params)["id"]
        size = video.stat().st_size
        with open(video, "rb") as fh:
            r = requests.post(f"https://rupload.facebook.com/ig-api-upload/{config.GRAPH_VERSION}/{container}",
                              headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size)},
                              data=fh, timeout=600)
        if r.status_code >= 400:
            raise RuntimeError(f"upload failed {r.status_code}: {r.text[:300]}")
        print(f"Uploaded {size / 1e6:.1f} MB (resumable)")
        ig.wait_ready(container, timeout=900)
    except Exception as e:  # 2) fallback: Instagram downloads it from the public repo
        print(f"Resumable upload did not work ({e}); trying video_url instead")
        method, first_error = "video_url", str(e)[:500]
        repo = os.environ["GITHUB_REPOSITORY"]
        url = f"https://raw.githubusercontent.com/{repo}/reel-files/{video.name}"
        container = ig.call("POST", f"{user}/media", video_url=url, **params)["id"]
        ig.wait_ready(container, timeout=900)

    result = {"slot": slot, "ist_date": ist_today(), "method": method, "resumable_error": first_error,
              "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if dry_run:
        result.update(dry_run=True, container=container,
                      note="Instagram processed the video OK. Nothing was posted; the upload expires in 24 h.")
        print(result["note"])
        return result
    media_id = ig.call("POST", f"{user}/media_publish", creation_id=container)["id"]
    permalink = ig.call("GET", media_id, fields="permalink").get("permalink", "")
    result.update(media_id=media_id, permalink=permalink)
    (reel_dir / "published.json").write_text(json.dumps(result, indent=2))
    print(f"Published: {permalink}")
    return result


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--failed"]:
        from due import ist_today
        note_failure(REELS / args[1], ist_today())
        sys.exit(0)
    if args[:1] == ["--pending"]:
        d = pending(args[1])
        print(d.name if d else "")
        sys.exit(0)
    slot, files_dir = args[0], Path(args[1])
    dry = "--dry-run" in args
    reel = pending(slot)
    if dry and reel is None:  # a dry run may also test an already-posted Reel or a test folder
        tests = sorted((REELS / "_test").glob("*/reel.json")) if (REELS / "_test").exists() else []
        reel = tests[-1].parent if tests else None
    if reel is None:
        print("No Reel queued for this slot.", file=sys.stderr)
        sys.exit(0)
    if dry:
        try:
            out = publish_reel(reel, files_dir / f"{reel.name}.mp4", slot, dry_run=True)
            out["result"] = "ok"
        except BaseException as e:  # keep the reason in the repo, so it can be read without the Actions log
            out = {"result": "failed", "error": str(e)[:1500]}
        (reel / "dry_run_result.json").write_text(json.dumps(out, indent=2))
        print(json.dumps(out, indent=2), file=sys.stderr)
        sys.exit(0 if out["result"] == "ok" else 1)
    publish_reel(reel, files_dir / f"{reel.name}.mp4", slot)
    print(reel.name)
