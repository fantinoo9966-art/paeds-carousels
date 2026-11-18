"""Scene timing for a Reel script (mirrors src/kit.tsx). Used for preview stills and the cover frame.
python reelkit/timeline.py script.json  -> prints total seconds and, per scene, a frame where it is fully built."""
import json
import math
import re
import sys

T = 14


def read_s(t: str = "") -> float:
    return 0.6 + len((t or "").replace("*", "")) / 16


def sec(s: float, pace: float) -> int:
    return round(s * 30 * pace)


def item_text(it: dict) -> str:
    return f"{it.get('text', '')} {it.get('sub', '') or ''}"


def delays(texts, pace, first=1.0):
    out, t = [], sec(first, pace)
    for s in texts:
        out.append(t)
        t += sec(0.35 + read_s(s) * 0.45, pace)
    return out


def texts(s: dict):
    k = s["type"]
    if k == "list":
        return [item_text(i) for i in s["items"]]
    if k == "cards":
        return [f"{c['title']} {' '.join(c['lines'])}" for c in s["cards"]]
    if k == "pearls":
        return s["items"]
    if k == "split":
        return s["left"]["lines"] + s["right"]["lines"]
    return []


def scene_len(s: dict, pace: float) -> int:
    k = s["type"]
    if k == "hook":
        return sec(4.0, pace)
    if k == "cta":
        return sec(3.8, pace)
    if k == "big":
        return max(sec(3.4, pace), sec(1.2 + read_s(s["text"]) * 0.8 + read_s(s.get("sub", "")) * 0.7, pace))
    if k == "split":
        return sec(3.0 + sum(read_s(t) * 0.4 for t in texts(s)), pace)
    tx = texts(s)
    d = delays(tx, pace)
    return d[-1] + sec(read_s(tx[-1]) * 0.4 + 1.5, pace)


def timeline(script: dict):
    pace = script.get("pace", 1.0)
    starts, t = [], 0
    for s in script["scenes"]:
        n = scene_len(s, pace)
        starts.append((t, n))
        t += n - T
    return starts, t + T


if __name__ == "__main__":
    sc = json.load(open(sys.argv[1], encoding="utf-8"))
    starts, total = timeline(sc)
    print(f"total {total / 30:.1f}s")
    print(" ".join(str(st + n - 24) for st, n in starts))
