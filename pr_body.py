"""Build the review page (pull request text) for a post: slide previews, caption, things to double-check."""
import json
import os
import sys
from pathlib import Path

post = Path(sys.argv[1])
branch = sys.argv[2]
repo = os.environ["GITHUB_REPOSITORY"]
data = json.loads((post / "slides.json").read_text(encoding="utf-8"))
caption = (post / "caption.txt").read_text(encoding="utf-8")

lines = [
    f"## 🩺 New carousel: {data['topic']}",
    "",
    "**To post it:** check the slides and the list below, then tap **Merge**. It goes live on Instagram within ~2 minutes.",
    f"**To fix text:** edit `{post.as_posix()}/slides.json` (slides) or `caption.txt` (caption) in this PR; slides re-render automatically.",
    "**To skip it:** close this PR without merging.",
    "",
    "### ⚠️ Please double-check before posting",
    *[f"- [ ] {c}" for c in data.get("doctor_check", [])],
    "",
    "### Slides",
]
for img in sorted(post.glob("slide*.jpg")):
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{img.as_posix()}"
    lines.append(f'<img src="{url}" width="270">')
lines += ["", "### Caption", "```", caption, "```", "", "### References",
          *[f"- {r}" for r in data.get("references", [])]]
print("\n".join(lines))
