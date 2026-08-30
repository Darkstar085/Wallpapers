#!/usr/bin/env python3

from pathlib import Path
from PIL import Image
import argparse, re

ROOT = Path("Mobile")
EXTS = {".jpg", ".jpeg", ".png", ".webp"}

def slug(s: str) -> str:
    s = re.sub(r"[_\-]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    s = re.sub(r"[^a-z0-9 ]+", "", s)
    return re.sub(r"\s+", "-", s) or "wallpaper"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    counters = {}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXTS:
            continue
        try:
            with Image.open(path) as im:
                w, h = im.size
        except Exception:
            continue

        category = path.parent.name
        base = f"{slug(category)}-{w}x{h}"
        counters[base] = counters.get(base, 0) + 1
        n = counters[base]
        new_name = f"{base}-{n:03d}{path.suffix.lower()}"
        target = path.with_name(new_name)

        if target == path:
            continue
        if target.exists():
            print(f"skip (exists): {target}")
            continue

        print(f"{path} -> {target}")
        if not args.dry_run:
            path.rename(target)

if __name__ == "__main__":
    main()
