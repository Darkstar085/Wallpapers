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
    value = re.sub(r"[-_]+", " ", stem)
    value = re.sub(r"\b\d{2,5}\s*[xX×]\s*\d{2,5}\b", "", value)
    value = re.sub(r"\s+", " ", value).strip(" -_")
    return value.title() or "Wallpaper"


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


def dominant_colors(image, limit=6):
    """Return representative colors as uppercase #RRGGBB values, most common first."""
    rgb = image.convert("RGB")
    rgb.thumbnail((96, 96), Image.Resampling.LANCZOS)
    quantized = rgb.quantize(colors=limit, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette()
    colors = quantized.getcolors(maxcolors=limit)
    if not colors or not palette:
        return []

    result = []
    for count, palette_index in sorted(colors, reverse=True):
        offset = palette_index * 3
        color = "#{:02X}{:02X}{:02X}".format(
            palette[offset], palette[offset + 1], palette[offset + 2]
        )
        if color not in result:
            result.append(color)
    return result


repo = os.getenv("GITHUB_REPOSITORY")
items = []

if ROOT.exists():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in EXTS:
            continue
        try:
            with Image.open(path) as im:
                width, height = im.size
                colors = dominant_colors(im)
        except Exception:
            continue

        rel = path.as_posix()
        category = path.parent.name if path.parent != ROOT else "Miscellaneous"
        url = f"https://raw.githubusercontent.com/{repo}/main/{rel}" if repo else rel
        items.append({
            "id": stable_id(rel),
            "title": title(path.stem),
            "category": category,
            "filename": path.name,
            "width": width,
            "height": height,
            "format": path.suffix.lower().lstrip("."),
            "file_size_bytes": path.stat().st_size,
            "colors": colors,
            "path": rel,
            "url": url,
            "added_at": added_at(path),
        })

payload = {
    "version": 3,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "count": len(items),
    "wallpapers": items
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Generated {OUT} with {len(items)} Mobile wallpaper(s).")
