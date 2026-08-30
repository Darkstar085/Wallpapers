#!/usr/bin/env python3

from pathlib import Path
from PIL import Image
import hashlib, json, mimetypes, re

ROOT = Path("Mobile")
OUT = Path("api/wallpapers.json")
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}

def slug(s):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s or "wallpaper"

def stable_id(rel):
    return hashlib.sha1(str(rel).encode("utf-8")).hexdigest()[:12]

items = []
for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
        continue
    try:
        with Image.open(path) as im:
            width, height = im.size
    except Exception:
        continue

    rel = path.as_posix()
    category = path.parent.name if path.parent != ROOT else "Miscellaneous"
    items.append({
        "id": stable_id(rel),
        "title": path.stem.replace("-", " ").replace("_", " ").strip().title(),
        "category": category,
        "width": width,
        "height": height,
        "format": path.suffix.lower().lstrip("."),
        "path": rel,
        "url": f"https://raw.githubusercontent.com/${{GITHUB_REPOSITORY}}/${{GITHUB_SHA}}/{rel}"
    })

# Replace GitHub expression placeholder at generation time.
import os
repo = os.getenv("GITHUB_REPOSITORY", "")
sha = os.getenv("GITHUB_SHA", "")
for item in items:
    item["url"] = f"https://raw.githubusercontent.com/{repo}/{sha}/{item['path']}" if repo and sha else item["path"]

payload = {
    "version": 1,
    "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    "count": len(items),
    "wallpapers": items
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Generated {OUT} with {len(items)} wallpaper(s).")
