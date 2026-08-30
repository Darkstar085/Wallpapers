#!/usr/bin/env python3

from pathlib import Path
from PIL import Image
import os

ROOT = Path("Mobile")
QUALITY = int(os.getenv("WEBP_QUALITY", "95"))
METHOD = int(os.getenv("WEBP_METHOD", "6"))
EXTS = {".jpg", ".jpeg", ".png", ".webp"}

def optimize(path: Path) -> bool:
    if path.suffix.lower() == ".webp":
        return False

    out = path.with_suffix(".webp")
    if out.exists():
        return False

    try:
        with Image.open(path) as im:
            has_alpha = "A" in im.getbands()
            kwargs = {"method": METHOD}
            if has_alpha:
                # Keep transparent wallpapers lossless.
                kwargs["lossless"] = True
            else:
                kwargs["quality"] = QUALITY
                kwargs["lossless"] = False

            im.save(out, "WEBP", **kwargs)

        if out.stat().st_size < path.stat().st_size:
            path.unlink()
            print(f"optimized: {path} -> {out} ({out.stat().st_size:,} bytes)")
            return True

        out.unlink()
        print(f"kept original (WebP larger): {path}")
        return False
    except Exception as exc:
        if out.exists():
            out.unlink()
        print(f"ERROR {path}: {exc}")
        return False

changed = 0
for path in ROOT.rglob("*"):
    if path.is_file() and path.suffix.lower() in EXTS:
        changed += optimize(path)

print(f"Done. Optimized {changed} image(s).")
