#!/usr/bin/env python3

from pathlib import Path
from PIL import Image
import argparse, re

ROOTS = [Path("Mobile"), Path("Desktop")]
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}

def slug(value):
    value = re.sub(r"[_-]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip().lower()
    value = re.sub(r"[^a-z0-9 ]+", "", value)
    return re.sub(r"\s+", "-", value) or "wallpaper"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for root in ROOTS:
        if not root.exists():
            continue
        counters = {}
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in EXTS:
                continue
            try:
                with Image.open(path) as im:
                    width, height = im.size
            except Exception:
                continue

            category = path.parent.name if path.parent != root else root.name
            base = f"{slug(category)}-{width}x{height}"
            counters[base] = counters.get(base, 0) + 1
            target = path.with_name(f"{base}-{counters[base]:03d}{path.suffix.lower()}")

            if target == path or target.exists():
                if target.exists() and target != path:
                    print(f"skip (target exists): {target}")
                continue

            print(f"{path} -> {target}")
            if not args.dry_run:
                path.rename(target)

if __name__ == "__main__":
    main()
