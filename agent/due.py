"""Decide which post (if any) is due right now. Prints reel_morning / morning / drug / reel_evening / evening,
or nothing.

Daily times (IST): 08:00 Parents Reel + MBBS carousel, 12:00 Drug of the Day, 20:00 PG Reel + PG carousel.
A Reel slot is only due when a Reel is waiting in the queue (reels/, see agent/publish_reel.py).

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

# ---------------- Safety settings (added 17 Nov 2026 after Meta's "automated activity" flag) ----------------
# QUIET_MODE = True  -> at most 3 posts a day: one in the morning (the Parents Reel, or the MBBS carousel
#                       if no Reel is waiting), Drug of the Day at noon, one in the evening (the PG Reel,
#                       or the PG carousel if no Reel is waiting).
# QUIET_MODE = False -> all 5 posts, spread out so no two are less than 2 hours apart.
QUIET_MODE = True
MIN_GAP_MINUTES = 120   # never post within 2 hours of the last post
LATE_LIMIT_MINUTES = 90  # a slot missed by more than this is SKIPPED, never posted late in a bunch
NO_POST_BEFORE = (7, 0)  # nothing goes out between 11 PM and 7 AM
NO_POST_AFTER = (23, 0)

# slot: start time (IST, 24-hour). Order matters: a Reel is tried before the carousel that shares its time.
if QUIET_MODE:
    TIMES = {"reel_morning": (8, 0), "morning": (8, 0), "drug": (12, 0),
             "reel_evening": (20, 0), "evening": (20, 0)}
else:
    TIMES = {"reel_morning": (8, 0), "morning": (10, 0), "drug": (12, 30),
             "evening": (17, 30), "reel_evening": (20, 0)}
# In quiet mode the Reel and carousel of the same time share one turn: only one of them is posted.
SHARED_TURN = {"morning": "reel_morning", "evening": "reel_evening"}

WINDOWS = {slot: ((h, m), divmod(h * 60 + m + LATE_LIMIT_MINUTES, 60)) for slot, (h, m) in TIMES.items()}


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


def due(now: datetime.datetime | None = None) -> str:
    now = now or datetime.datetime.now(IST)
    today = now.date().isoformat()
    minutes = now.hour * 60 + now.minute
    if not (NO_POST_BEFORE[0] * 60 + NO_POST_BEFORE[1] <= minutes < NO_POST_AFTER[0] * 60 + NO_POST_AFTER[1]):
        return ""  # night time: never post
    if minutes_since_last_post(now) < MIN_GAP_MINUTES:
        return ""  # too soon after the last post
    for slot, ((sh, sm), (eh, em)) in WINDOWS.items():
        if not (sh * 60 + sm <= minutes < eh * 60 + em):
            continue  # not this slot's time, or missed by too long (skipped, not posted late)
        if QUIET_MODE and slot in SHARED_TURN and slot_done(SHARED_TURN[slot], today):
            continue  # the Reel already used this turn
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
