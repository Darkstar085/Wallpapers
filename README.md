# 🖼️ Wallpapers

<p align="center">
  <strong>A curated collection of wallpapers for mobile devices.</strong><br>
  <sub>Simple · Clean · Organized</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-CC_BY_4.0-blue?style=flat-square" alt="CC BY 4.0">
  <img src="https://img.shields.io/github/last-commit/Darkstar085/Wallpapers?style=flat-square" alt="Last commit">
</p>

---

## ✨ Collection

A growing collection of mobile wallpapers organized into focused categories.

| Category | Description |
|---|---|
| 🎨 **Abstract** | Abstract and artistic compositions |
| 🐾 **Animals** | Wildlife and animal wallpapers |
| 🎌 **Anime** | Anime and animated artwork |
| 🖤 **Black** | Dark and black-focused wallpapers |
| 🚗 **Cars** | Automotive wallpapers |
| 🌸 **Flowers** | Floral and botanical wallpapers |
| 🛕 **Gods** | Deities and spiritual artwork |
| 🏔️ **Landscape** | Natural landscapes and wide scenes |
| ◻️ **Minimal** | Minimal and clean designs |
| 🧩 **Misc** | Wallpapers outside the main categories |
| 🌄 **Scenery** | Scenic and environment-focused wallpapers |
| 🌌 **Space** | Space, planets, and cosmic artwork |

## 📱 Mobile

All wallpapers are available under:

`Mobile/<Category>/`

Supported formats:

`JPG` · `JPEG` · `PNG` · `WebP`

Original image formats are preserved.

## 🔄 How It Works

1. Add a wallpaper to the appropriate `Mobile/<Category>/` directory.
2. GitHub Actions validates the image, format, dimensions, and file size.
3. Optimization is applied only when the optimized file is smaller.
4. The original image format is preserved.
5. A content-based filename is generated from the final image.
6. Duplicate content is rejected.
7. The catalogue and collection statistics are updated automatically.

## 🧩 File Naming

Wallpapers use category-based, content-derived filenames.

Example:

`Mobile/Anime/anime-0a006fa1.jpg`

The hash is derived from the final image content, keeping filenames deterministic and tied to the actual wallpaper.

## 🗂️ Catalogue API

The generated catalogue is available at:

`api/wallpapers.json`

Each wallpaper entry contains metadata such as:

- ID and title
- Category and device
- Width, height, and aspect ratio
- Orientation and format
- Repository path and raw URL
- Filename and file size

The catalogue can be consumed by apps and other projects without scanning the repository.

## 🤖 GitHub Actions

Repository maintenance is handled automatically through GitHub Actions.

Pushes affecting `Mobile/` or the maintenance script trigger processing. Manual runs use an idempotent repair mode so they can be repeated without unnecessarily changing already-canonical filenames.

## 📌 Contribution Guidelines

To add a wallpaper:

- Place it under the appropriate `Mobile/<Category>/` directory.
- Use JPG/JPEG, PNG, or WebP.
- Keep individual files at or below 50 MiB.
- Avoid duplicate images.
- Prefer an existing category instead of creating a new one unnecessarily.
- Let the repository automation handle naming, optimization, catalogue updates, and statistics.

## 🛠️ Repository Structure

```
Mobile/
├── Abstract/
├── Animals/
├── Anime/
├── Black/
├── Cars/
├── Flowers/
├── Gods/
├── Landscape/
├── Minimal/
├── Misc/
├── Scenery/
└── Space/

api/
└── wallpapers.json
```


## 📊 Collection Stats

| Folder | Files | Size |
|---|---:|---:|
| Mobile/Abstract | 26 | 31.8 MB |
| Mobile/Animals | 2 | 5.1 MB |
| Mobile/Anime | 45 | 51.2 MB |
| Mobile/Black | 14 | 19.5 MB |
| Mobile/Cars | 5 | 4.5 MB |
| Mobile/Flowers | 24 | 36.5 MB |
| Mobile/Gods | 10 | 3.8 MB |
| Mobile/Landscape | 3 | 6.4 MB |
| Mobile/Minimal | 4 | 5.8 MB |
| Mobile/Misc | 10 | 26.0 MB |
| Mobile/Scenery | 14 | 30.8 MB |
| Mobile/Space | 7 | 25.0 MB |
| **Total** | **164** | **246.3 MB** |

## 📄 License

See [LICENSE](LICENSE) for ownership, attribution, and third-party licensing terms.
