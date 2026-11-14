"""Publish posts/<slug> as an Instagram carousel via the official "Instagram API with Instagram Login".
No Facebook Page is needed; the token comes straight from the Instagram account.

Needs env vars: IG_ACCESS_TOKEN, GITHUB_REPOSITORY (owner/repo). Optional: IG_USER_ID (looked up if missing),
IMAGE_BRANCH (default main).
Images are served from the public GitHub repo (raw.githubusercontent.com), which Instagram downloads.
Usage: python agent/publish.py posts/<slug>
"""
import json
import os
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
import config  # noqa: E402

API = f"https://graph.instagram.com/{config.GRAPH_VERSION}"


def call(method: str, path: str, **params) -> dict:
    params["access_token"] = os.environ["IG_ACCESS_TOKEN"]
    r = requests.request(method, f"{API}/{path}", data=params if method == "POST" else None,
                         params=params if method == "GET" else None, timeout=60)
    body = r.json()
    if r.status_code >= 400 or "error" in body:
        raise RuntimeError(f"Instagram API error on {path}: {body.get('error', body)}")
    return body


def wait_ready(container_id: str, timeout: int = 300) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        status = call("GET", container_id, fields="status_code").get("status_code")
        if status in ("FINISHED", "PUBLISHED"):
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Container {container_id} failed: {status}")
        time.sleep(5)
    raise TimeoutError(f"Container {container_id} not ready after {timeout}s")


def publish(post_dir: Path) -> dict:
    if (post_dir / "published.json").exists():
        print("Already published, skipping.")
        return json.loads((post_dir / "published.json").read_text())

    me = call("GET", "me", fields="user_id,username")
    ig_user = os.environ.get("IG_USER_ID") or me["user_id"]
    print(f"Posting as @{me.get('username')}")
    repo = os.environ["GITHUB_REPOSITORY"]
    branch = os.environ.get("IMAGE_BRANCH", "main")
    images = sorted(post_dir.glob("slide*.jpg"))[: config.MAX_SLIDES]
    if len(images) < 2:
        raise SystemExit("A carousel needs at least 2 slides.")
    caption = (post_dir / "caption.txt").read_text(encoding="utf-8")[:2200]

    children = []
    for img in images:
        rel = img.relative_to(post_dir.parent.parent).as_posix()
        url = f"https://raw.githubusercontent.com/{repo}/{branch}/{rel}"
        cid = call("POST", f"{ig_user}/media", image_url=url, is_carousel_item="true")["id"]
        children.append(cid)
        print(f"Uploaded {img.name}")
    for cid in children:
        wait_ready(cid)

    carousel = call("POST", f"{ig_user}/media", media_type="CAROUSEL",
                    children=",".join(children), caption=caption)["id"]
    wait_ready(carousel)
    media_id = call("POST", f"{ig_user}/media_publish", creation_id=carousel)["id"]
    permalink = call("GET", media_id, fields="permalink").get("permalink", "")

    result = {"media_id": media_id, "permalink": permalink, "published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    (post_dir / "published.json").write_text(json.dumps(result, indent=2))
    print(f"Published: {permalink}")
    return result


if __name__ == "__main__":
    publish(Path(sys.argv[1]))
