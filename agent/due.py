"""Decide which post (if any) is due right now. Prints reel_morning / morning / drug / reel_evening / evening,
or nothing.

Daily times (IST): 08:00 Parents Reel + MBBS carousel, 12:00 Drug of the Day, 20:00 PG Reel + PG carousel.
A Reel slot is only due when a Reel is waiting in the queue (reels/, see agent/publish_reel.py).

GitHub's scheduler can start runs late or skip them, so the workflow runs every 30 minutes and
this script picks the earliest slot whose time has passed (India time) and that has not been
posted today. Each slot has a window, so a missed morning post is not sent late at night.
Standard library only, so it runs before anything is installed.
"""
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

POSTS = Path(__file__).resolve().parent.parent / "posts"
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

# slot: (start, end) in IST, 24-hour clock. A missed slot is still posted later the same day.
# Order matters: at 8:00 and 20:00 the Reel goes first (quick), then the carousel.
WINDOWS = {
    "reel_morning": ((8, 0), (24, 0)),
    "morning": ((8, 0), (24, 0)),
    "drug": ((12, 0), (24, 0)),
    "reel_evening": ((20, 0), (24, 0)),
    "evening": ((20, 0), (24, 0)),
}


def posted_today(slot: str, today: str) -> bool:
    for f in POSTS.glob("*/slides.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        # Only counts once it is actually live on Instagram (published.json written).
        if (data.get("slot") == slot and data.get("ist_date") == today
                and (f.parent / "published.json").exists()):
            return True
    return False


def reel_due(slot: str, today: str) -> bool:
    import publish_reel  # standard library only at import time
    reel = publish_reel.pending(slot)
    return (reel is not None and not publish_reel.posted_today(slot, today)
            and publish_reel.failures_today(reel, today) < 2)


def due(now: datetime.datetime | None = None) -> str:
    now = now or datetime.datetime.now(IST)
    today = now.date().isoformat()
    minutes = now.hour * 60 + now.minute
    for slot, ((sh, sm), (eh, em)) in WINDOWS.items():
        if not (sh * 60 + sm <= minutes < eh * 60 + em):
            continue
        if slot.startswith("reel_"):
            if reel_due(slot, today):
                return slot
        elif not posted_today(slot, today):
            return slot
    return ""


def ist_today() -> str:
    return datetime.datetime.now(IST).date().isoformat()


if __name__ == "__main__":
    print(due())
