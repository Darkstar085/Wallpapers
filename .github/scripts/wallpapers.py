#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from tempfile import NamedTemporaryFile

from PIL import Image, ImageOps, UnidentifiedImageError

ROOTS = ("Mobile",)
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 50 * 1024 * 1024
MIN_WIDTH = 720
MIN_HEIGHT = 720
CATALOG_VERSION = 1
REPO = "Darkstar085/Wallpapers"
BRANCH = "main"


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def log(message: str) -> None:
    print(f"[wallpapers] {message}", flush=True)


def image_files() -> list[Path]:
    files = []
    for root_name in ROOTS:
        root = Path(root_name)
        if root.is_dir():
            files.extend(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSIONS)
    return sorted(files, key=lambda p: p.as_posix().lower())


def validate_path(path: Path) -> None:
    parts = path.parts
    if len(parts) != 3 or parts[0] not in ROOTS:
        raise ValueError(f"{path}: expected <Mobile>/<Category>/<file>")
    if not parts[1].strip():
        raise ValueError(f"{path}: category cannot be empty")


def read_image(path: Path) -> tuple[int, int, str]:
    size = path.stat().st_size
    if size <= 0:
        raise ValueError("empty file")
    if size > MAX_FILE_SIZE:
        raise ValueError(f"file exceeds {MAX_FILE_SIZE // (1024 * 1024)} MiB")
    try:
        with Image.open(path) as image:
            width, height = image.size
            fmt = (image.format or path.suffix.lstrip(".")).lower()
            image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"invalid image: {exc}") from exc
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        raise ValueError(f"resolution {width}x{height} is below {MIN_WIDTH}x{MIN_HEIGHT}")
    return width, height, fmt


def content_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def slug(category: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "-", category).strip("-").lower()
    return value or "wallpaper"


def git_added_paths(commit: str) -> list[Path]:
    try:
        parent = run("git", "rev-parse", f"{commit}^")
    except subprocess.CalledProcessError:
        parent = ""
    if parent:
        output = run(
            "git", "diff-tree", "--no-commit-id", "--name-status", "-r", "-M",
            parent, commit,
        )
    else:
        output = run(
            "git", "diff-tree", "--root", "--no-commit-id", "--name-status", "-r", "-M",
            commit,
        )
    added = []
    for line in output.splitlines():
        fields = line.split("\t")
        if fields and fields[0] == "A" and len(fields) >= 2:
            path = Path(fields[1])
            if path.suffix.lower() in EXTENSIONS and path.parts and path.parts[0] in ROOTS:
                added.append(path)
    return added



def canonical_name(path: Path, digest: str) -> str:
    return f"{slug(path.parts[1])}-{digest[:8]}{path.suffix.lower()}"


def allocate_name(path: Path, digest: str) -> Path:
    candidate = path.with_name(canonical_name(path, digest))
    if candidate == path or not candidate.exists():
        return candidate
    index = 2
    while True:
        candidate = path.with_name(f"{slug(path.parts[1])}-{digest[:8]}-{index}{path.suffix.lower()}")
        if not candidate.exists():
            return candidate
        index += 1


def optimize_new_image(path: Path) -> None:
    original_size = path.stat().st_size
    suffix = path.suffix.lower()
    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source)
        if suffix in {".jpg", ".jpeg"}:
            image = image.convert("RGB")
            save_kwargs = {"format": "JPEG", "quality": 90, "optimize": True, "progressive": True}
        elif suffix == ".png":
            if image.mode not in {"1", "L", "LA", "RGB", "RGBA", "P", "I", "I;16"}:
                image = image.convert("RGBA")
            save_kwargs = {"format": "PNG", "optimize": True}
        elif suffix == ".webp":
            if image.mode not in {"RGB", "RGBA"}:
                image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
            save_kwargs = {"format": "WEBP", "quality": 90, "method": 6}
        else:
            return
        with NamedTemporaryFile(dir=path.parent, suffix=suffix, delete=False) as tmp:
            temp_path = Path(tmp.name)
        try:
            image.save(temp_path, **save_kwargs)
            if temp_path.stat().st_size < original_size:
                temp_path.replace(path)
            else:
                temp_path.unlink(missing_ok=True)
        finally:
            temp_path.unlink(missing_ok=True)



def validate_all() -> None:
    files = image_files()
    log(f"Validating {len(files)} wallpaper(s)...")
    if not files:
        raise SystemExit("No wallpapers found.")
    errors = []
    for index, path in enumerate(files, 1):
        log(f"Validating [{index}/{len(files)}] {path}")
        try:
            validate_path(path)
            read_image(path)
        except ValueError as exc:
            errors.append(str(exc))
    if errors:
        raise SystemExit("Wallpaper validation failed:\n" + "\n".join(f"- {e}" for e in errors))


def detect_duplicates(files: list[Path]) -> None:
    log(f"Checking {len(files)} wallpaper(s) for duplicates...")
    seen: dict[str, Path] = {}
    for index, path in enumerate(files, 1):
        log(f"Duplicate check [{index}/{len(files)}] {path}")
        digest = content_sha(path)
        if digest in seen and seen[digest] != path:
            raise SystemExit(f"Duplicate wallpaper detected: {path} matches {seen[digest]}")
        seen[digest] = path

def process_path(original: Path) -> Path:
    validate_path(original)
    read_image(original)
    path = original
    original_digest = content_sha(path)
    already_canonical = path.name == canonical_name(path, original_digest)

    before = path.stat().st_size
    optimize_new_image(path)
    after = path.stat().st_size
    if after < before:
        log(f"Optimized {path.name}: {before} -> {after} bytes")

    if already_canonical:
        return path

    digest = content_sha(path)
    target = allocate_name(path, digest)
    if target != path:
        log(f"Renaming {path} -> {target}")
        path.rename(target)
        path = target
    return path


def process_pending() -> None:
    files = image_files()
    pending = [p for p in files if p.name != canonical_name(p, content_sha(p))]
    log(f"Found {len(pending)} wallpaper(s) pending rename.")
    for index, original in enumerate(pending, 1):
        log(f"Processing [{index}/{len(pending)}] {original}")
        process_path(original)

def process_new(commit: str) -> list[Path]:
    added = git_added_paths(commit)
    log(f"Found {len(added)} newly added wallpaper(s).")
    changed = []
    for index, original in enumerate(added, 1):
        log(f"Processing new [{index}/{len(added)}] {original}")
        changed.append(process_path(original))
    return changed

def catalog_files() -> list[Path]:
    if not Path("Mobile").is_dir():
        return []
    return sorted(
        (p for p in Path("Mobile").rglob("*") if p.is_file() and p.suffix.lower() in EXTENSIONS),
        key=lambda p: p.as_posix().lower(),
    )


def build_catalog() -> dict:
    wallpapers = []
    files = catalog_files()
    log(f"Building catalogue from {len(files)} Mobile wallpaper(s)...")
    for index, path in enumerate(files, 1):
        log(f"Catalogue [{index}/{len(files)}] {path}")
        validate_path(path)
        width, height, image_format = read_image(path)
        relative = path.as_posix()
        wallpapers.append({
            "id": content_sha(path)[:16],
            "title": path.stem.replace("-", " ").replace("_", " ").strip(),
            "category": path.parts[1],
            "device": path.parts[0].lower(),
            "width": width,
            "height": height,
            "aspect_ratio": f"{width}:{height}",
            "orientation": "landscape" if width > height else "portrait" if height > width else "square",
            "format": image_format,
            "path": relative,
            "url": f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{relative}",
            "filename": path.name,
            "file_size_bytes": path.stat().st_size,
        })
    return {"version": CATALOG_VERSION, "wallpapers": wallpapers}


def write_catalog(output: Path) -> None:
    log("Generating Mobile wallpaper catalogue...")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(build_catalog(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    log(f"Catalogue written to {output}")



def collection_stats() -> list[tuple[str, int, int]]:
    stats: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for path in image_files():
        category = path.parts[1]
        stats[category][0] += 1
        stats[category][1] += path.stat().st_size
    return [(category, values[0], values[1]) for category, values in sorted(stats.items())]


def format_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} GB"


def update_readme() -> None:
    readme = Path("README.md")
    text = readme.read_text(encoding="utf-8") if readme.exists() else "# Wallpapers\n"
    begin = "<!-- WALLPAPER-STATS:START -->"
    finish = "<!-- WALLPAPER-STATS:END -->"
    rows = ["## 📊 Collection Stats", "", "| Folder | Files | Size |", "|---|---:|---:|"]
    total_files = 0
    total_size = 0
    for category, count, size in collection_stats():
        rows.append(f"| Mobile/{category} | {count} | {format_size(size)} |")
        total_files += count
        total_size += size
    rows.append(f"| **Total** | **{total_files}** | **{format_size(total_size)}** |")
    block = begin + "\n" + "\n".join(rows) + "\n\n" + finish
    if begin in text and finish in text:
        before = text.split(begin, 1)[0].rstrip()
        after = text.split(finish, 1)[1].lstrip()
        text = before + "\n\n" + block + ("\n\n" + after if after else "\n")
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    readme.write_text(text, encoding="utf-8")
    log(f"README updated with {len(collection_stats())} folder stats.")


def build_message(added: list[Path]) -> str:
    lines: list[str] = []
    if added:
        by_category: dict[str, list[Path]] = {}
        for path in added:
            by_category.setdefault(path.parts[1], []).append(path)
        total = len(added)
        subject = f"chore: add {total} wallpaper{'s' if total != 1 else ''}"
        for category, paths in sorted(by_category.items()):
            lines.append(f"- Add {len(paths)} wallpaper{'s' if len(paths) != 1 else ''} to {category}.")
            for path in paths:
                try:
                    width, height, _ = read_image(path)
                    mb = path.stat().st_size / (1024 * 1024)
                    lines.append(f"  - {path.name} · {width}x{height} · {mb:.1f} MB")
                except (ValueError, FileNotFoundError):
                    pass
    else:
        subject = "chore: update wallpaper collection"
        lines.append("- Normalize filenames and optimize images without changing their original formats.")
        lines.append("- Refresh collection metadata and folder statistics.")
    lines.append("")
    lines.append("Folder stats:")
    for category, count, size in collection_stats():
        lines.append(f"- {category}: {count} files · {format_size(size)}")
    lines.extend(["", "Signed-off-by: S I P U N <sipunkumar85@gmail.com>"])
    return subject + "\n\n" + "\n".join(lines)

def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("process")
    sub.add_parser("repair")
    sub.add_parser("catalog")
    sub.add_parser("validate")
    args = parser.parse_args()
    commit = os.environ.get("GITHUB_SHA", "HEAD")
    log(f"Starting '{args.command}' for commit {commit}")
    if args.command == "process":
        added = git_added_paths(commit)
        process_new(commit)
        process_pending()
        validate_all()
        detect_duplicates(image_files())
        write_catalog(Path("api/wallpapers.json"))
        update_readme()
        Path(".wallpaper-commit-message").write_text(
            build_message(added) + "\n",
            encoding="utf-8",
        )
        log("Wallpaper processing complete.")
    elif args.command == "repair":
        process_pending()
        validate_all()
        detect_duplicates(image_files())
        write_catalog(Path("api/wallpapers.json"))
        update_readme()
        Path(".wallpaper-commit-message").write_text(
            build_message([]) + "\n",
            encoding="utf-8",
        )
        log("Wallpaper repair complete.")
    elif args.command == "catalog":
        validate_all()
        detect_duplicates(image_files())
        write_catalog(Path("api/wallpapers.json"))
        log("Catalogue command complete.")
    else:
        validate_all()
        detect_duplicates(image_files())
        log("Validation complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
