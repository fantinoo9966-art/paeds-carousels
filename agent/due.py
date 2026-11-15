"""Decide which post (if any) is due right now. Prints morning / drug / evening, or nothing.

GitHub's scheduler can start runs late or skip them, so the workflow runs every 30 minutes and
this script picks the earliest slot whose time has passed (India time) and that has not been
posted today. Each slot has a window, so a missed morning post is not sent late at night.
Standard library only, so it runs before anything is installed.
"""
import datetime
import json
from pathlib import Path

POSTS = Path(__file__).resolve().parent.parent / "posts"
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

# slot: (start, end) in IST, 24-hour clock
WINDOWS = {
    "morning": ((8, 0), (12, 0)),
    "drug": ((12, 0), (17, 0)),
    "evening": ((19, 30), (23, 30)),
}


def posted_today(slot: str, today: str) -> bool:
    for f in POSTS.glob("*/slides.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("slot") == slot and data.get("ist_date") == today:
            return True
    return False


def due(now: datetime.datetime | None = None) -> str:
    now = now or datetime.datetime.now(IST)
    today = now.date().isoformat()
    minutes = now.hour * 60 + now.minute
    for slot, ((sh, sm), (eh, em)) in WINDOWS.items():
        if sh * 60 + sm <= minutes < eh * 60 + em and not posted_today(slot, today):
            return slot
    return ""


def ist_today() -> str:
    return datetime.datetime.now(IST).date().isoformat()


if __name__ == "__main__":
    print(due())
