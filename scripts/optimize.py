#!/usr/bin/env python3

from pathlib import Path
from PIL import Image
import os

ROOTS = [Path("Mobile"), Path("Desktop")]
QUALITY = int(os.getenv("WEBP_QUALITY", "95"))
METHOD = int(os.getenv("WEBP_METHOD", "6"))
EXTS = {".jpg", ".jpeg", ".png"}

stats = {"processed": 0, "converted": 0}

def optimize(path):
    before = path.stat().st_size
    out = path.with_suffix(".webp")
    try:
        with Image.open(path) as im:
            kwargs = {"method": METHOD}
            if "A" in im.getbands():
                kwargs["lossless"] = True
            else:
                kwargs.update(lossless=False, quality=QUALITY)
            im.save(out, "WEBP", **kwargs)

        optimized = out.stat().st_size
        stats["processed"] += 1
        if optimized < before:
            path.unlink()
            stats["converted"] += 1
            print(f"optimized: {path} -> {out}")
        else:
            out.unlink()
            print(f"kept: {path} (WebP was larger)")
    except Exception as exc:
        if out.exists():
            out.unlink()
        print(f"ERROR {path}: {exc}")

for root in ROOTS:
    if root.exists():
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in EXTS:
                optimize(path)

for key, value in stats.items():
    print(f"STAT_{key.upper()}={value}")
