"""Decide which post (if any) is due right now. Prints reel_morning / morning / drug / reel_evening / evening,
or nothing.

Daily (IST): 10:30 one carousel (MBBS and PG on alternate days), 18:30 one Reel (if one is waiting).
No Drug of the Day. A Reel slot is only due when a Reel is waiting in the queue (reels/, see agent/publish_reel.py).

GitHub's scheduler can start runs late or skip them, so the workflow runs every 30 minutes and
this script picks the slot whose time it is now (India time) and that has not been posted yet.
Safety rules (see settings below): a missed slot is skipped rather than posted late, posts are always
at least 2 hours apart, nothing is posted at night, and QUIET_MODE limits it to 3 posts a day.
Standard library only, so it runs before anything is installed.
"""
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

POSTS = Path(__file__).resolve().parent.parent / "posts"
REELS = Path(__file__).resolve().parent.parent / "reels"
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

# ---------------- Schedule (24 Nov 2026, user: "1 carousel and one reel per day", no Drug of the Day) ----------------
# One carousel a day at CAROUSEL_TIME: MBBS ("morning" slot, notebook style) and PG ("evening" slot) on alternate days.
# One Reel a day at REEL_TIME: Parents and PG Reels on alternate days (falls back to the other if none is waiting).
CAROUSEL_TIME = (10, 30)
REEL_TIME = (18, 30)
MIN_GAP_MINUTES = 240    # never post within 4 hours of the last post
LATE_LIMIT_MINUTES = 90  # a slot missed by more than this is SKIPPED, never posted late in a bunch
NO_POST_BEFORE = (7, 0)  # nothing goes out between 11 PM and 7 AM
NO_POST_AFTER = (23, 0)


def carousel_slot(day: datetime.date) -> str:
    return "morning" if day.toordinal() % 2 == 0 else "evening"


def reel_slots(day: datetime.date) -> list[str]:
    first = "reel_morning" if day.toordinal() % 2 == 1 else "reel_evening"
    return [first, "reel_evening" if first == "reel_morning" else "reel_morning"]


def _in_window(minutes: int, hm: tuple[int, int]) -> bool:
    start = hm[0] * 60 + hm[1]
    return start <= minutes < start + LATE_LIMIT_MINUTES


def _published_times() -> list[datetime.datetime]:
    """When every post and Reel actually went live (UTC)."""
    out = []
    for f in list(POSTS.glob("*/published.json")) + list(REELS.glob("*/published.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("dry_run"):
            continue
        stamp = data.get("published_at") or data.get("checked_at")
        if not stamp:
            continue
        try:
            out.append(datetime.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc))
        except ValueError:
            continue
    return out


def minutes_since_last_post(now: datetime.datetime) -> float:
    times = _published_times()
    if not times:
        return float("inf")
    return (now - max(times)).total_seconds() / 60


def slot_done(slot: str, today: str) -> bool:
    if slot.startswith("reel_"):
        import publish_reel
        return publish_reel.posted_today(slot, today)
    return posted_today(slot, today)


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


PAUSED = True  # 24 Nov 2026: user said "stop everything", will decide in 3 days. Set False to resume.


def due(now: datetime.datetime | None = None) -> str:
    if PAUSED:
        return ""
    now = now or datetime.datetime.now(IST)
    today = now.date().isoformat()
    minutes = now.hour * 60 + now.minute
    if not (NO_POST_BEFORE[0] * 60 + NO_POST_BEFORE[1] <= minutes < NO_POST_AFTER[0] * 60 + NO_POST_AFTER[1]):
        return ""  # night time: never post
    if minutes_since_last_post(now) < MIN_GAP_MINUTES:
        return ""  # too soon after the last post
    if _in_window(minutes, CAROUSEL_TIME):
        if not (posted_today("morning", today) or posted_today("evening", today)):
            return carousel_slot(now.date())
    if _in_window(minutes, REEL_TIME):
        if not (slot_done("reel_morning", today) or slot_done("reel_evening", today)):
            for slot in reel_slots(now.date()):
                if reel_due(slot, today):
                    return slot
    return ""


def ist_today() -> str:
    return datetime.datetime.now(IST).date().isoformat()


if __name__ == "__main__":
    print(due())
