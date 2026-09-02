#!/usr/bin/env python3

from pathlib import Path
from PIL import Image
import hashlib, json, os, re, subprocess
from datetime import datetime, timezone

ROOT = Path("Mobile")
OUT = Path("api/wallpapers.json")
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}

def stable_id(path):
    return hashlib.sha1(path.encode()).hexdigest()[:12]

def title(stem):
    return re.sub(r"\s+", " ", re.sub(r"[-_]+", " ", stem)).strip().title()

def added_at(path):
    try:
        result = subprocess.run(
            ["git", "log", "--follow", "--format=%cI", "--reverse", "--", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
        value = result.stdout.strip().splitlines()
        if value:
            return value[0]
    except (OSError, subprocess.CalledProcessError):
        pass
    return datetime.now(timezone.utc).isoformat()

repo = os.getenv("GITHUB_REPOSITORY")
items = []

if ROOT.exists():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in EXTS:
            continue
        try:
            with Image.open(path) as im:
                width, height = im.size
        except Exception:
            continue

        rel = path.as_posix()
        category = path.parent.name if path.parent != ROOT else "Miscellaneous"
        url = f"https://raw.githubusercontent.com/{repo}/main/{rel}" if repo else rel
        items.append({
            "id": stable_id(rel),
            "title": title(path.stem),
            "category": category,
            "width": width,
            "height": height,
            "format": path.suffix.lower().lstrip("."),
            "path": rel,
            "url": url,
            "added_at": added_at(path),
        })

payload = {
    "version": 2,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "count": len(items),
    "wallpapers": items
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Generated {OUT} with {len(items)} Mobile wallpaper(s).")
