#!/usr/bin/env python3

from pathlib import Path
from PIL import Image
import hashlib
import re

ROOTS = [Path("Mobile"), Path("Desktop")]
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}

TITLE_WORDS = {
    "gods": (["Divine", "Sacred", "Celestial", "Eternal", "Golden", "Mystic", "Heavenly", "Blessed", "Ancient", "Serene", "Holy", "Radiant", "Infinite", "Majestic", "Timeless", "Pure", "Graceful", "Immortal", "Glowing", "Sublime", "Noble", "Peaceful", "Luminous", "Ethereal", "Hallowed", "Quiet", "Sovereign", "Seraphic", "Hallowed", "Divine"], ["Grace", "Aura", "Light", "Spirit", "Glory", "Presence", "Blessing", "Divinity", "Radiance", "Guardian", "Wisdom", "Mercy", "Wonder", "Halo", "Peace", "Sanctuary", "Essence", "Dawn", "Majesty", "Serenity", "Faith", "Splendor", "Reverence", "Soul", "Embrace", "Harmony", "Guidance", "Eternity", "Mystery", "Glory"]),
    "flowers": (["Velvet", "Morning", "Golden", "Wild", "Soft", "Blushing", "Secret", "Spring", "Dreamy", "Petal", "Violet", "Crimson", "Gentle", "Fresh", "Sunlit", "Moonlit", "Hidden", "Rosy", "Silver", "Lush", "Tender", "Radiant", "Quiet", "Lovely", "Dewy", "Blooming", "Pastel", "Fragrant", "Meadow", "Enchanted"], ["Bloom", "Garden", "Whisper", "Grace", "Dream", "Bouquet", "Charm", "Meadow", "Glow", "Promise", "Petals", "Blossom", "Spring", "Dawn", "Haven", "Wonder", "Kiss", "Breeze", "Magic", "Colors", "Secret", "Joy", "Drift", "Song", "Muse", "Rain", "Light", "Velvet", "Bloom", "Whisper"]),
    "nature": (["Wild", "Morning", "Golden", "Misty", "Quiet", "Emerald", "Secret", "Sunlit", "Fresh", "Serene", "Hidden", "Green", "Rustic", "Whispering", "Peaceful", "Lush", "Autumn", "Winter", "Summer", "Spring", "Earthy", "Mountain", "River", "Forest", "Open", "Still", "Natural", "Soft", "Wandering", "Dewy"], ["Breeze", "Whisper", "Forest", "Garden", "Trails", "Roots", "Calm", "Light", "Escape", "Wonder", "Meadow", "Valley", "Haven", "Journey", "Canopy", "River", "Woods", "Morning", "Path", "Stillness", "Glow", "Mist", "Leaves", "Horizon", "Peace", "Shelter", "Wilds", "Drift", "Dawn", "Wonder"]),
    "landscape": (["Golden", "Misty", "Wild", "Silent", "Hidden", "Alpine", "Dreamy", "Endless", "Serene", "Wandering", "Sunlit", "Moonlit", "Distant", "Peaceful", "Ancient", "Open", "Vast", "Rolling", "Snowy", "Quiet", "Emerald", "Autumn", "Twilight", "Stormy", "Majestic", "Remote", "Timeless", "Crystal", "Soft", "Luminous"], ["Horizon", "Valley", "Escape", "Trails", "Meadow", "Peaks", "Vista", "Journey", "Wilderness", "Dawn", "Summit", "Ridge", "Lake", "River", "Pass", "Highlands", "Dream", "Skies", "Voyage", "Shelter", "Fields", "Cliffs", "Morning", "Refuge", "Frontier", "Wonder", "Silence", "Overlook", "Valley", "Horizon"]),
    "animals": (["Wild", "Gentle", "Fierce", "Golden", "Silent", "Mystic", "Noble", "Midnight", "Brave", "Free", "Majestic", "Curious", "Hidden", "Arctic", "Desert", "Forest", "Royal", "Lone", "Swift", "Calm", "Ancient", "Untamed", "Proud", "Soft", "Wandering", "Shadow", "Bright", "Fearless", "Quiet", "Sacred"], ["Spirit", "Roar", "Eyes", "Guardian", "Wanderer", "Soul", "Kingdom", "Trail", "Whisper", "Call", "Heart", "Companion", "Instinct", "Hunter", "Grace", "Journey", "Watcher", "Wilds", "Pride", "Gaze", "Tracks", "Echo", "Fur", "Wings", "Haven", "Ranger", "Legend", "Path", "Freedom", "Presence"]),
    "anime & cartoon": (["Moonlit", "Hidden", "Crimson", "Dreamy", "Mystic", "Starlit", "Golden", "Electric", "Silent", "Celestial", "Neon", "Azure", "Rosy", "Magical", "Radiant", "Midnight", "Pastel", "Fabled", "Lunar", "Cosmic", "Playful", "Brilliant", "Enchanted", "Scarlet", "Vivid", "Secret", "Summer", "Winter", "Twilight", "Charming"], ["Hero", "Journey", "Realm", "Dream", "Adventure", "Spirit", "Legend", "Story", "Sky", "Quest", "World", "Moment", "Promise", "Wonder", "Magic", "Heart", "Destiny", "Voyage", "Horizon", "Chronicle", "Fantasy", "Odyssey", "Whisper", "Tale", "Light", "Star", "Path", "Echo", "Bloom", "Secret"]),
    "abstract": (["Fluid", "Neon", "Velvet", "Prism", "Liquid", "Silent", "Cosmic", "Aurora", "Dream", "Chrome", "Electric", "Glass", "Digital", "Soft", "Infinite", "Vivid", "Luminous", "Fading", "Hidden", "Colorful", "Radiant", "Abstract", "Fractal", "Smooth", "Glowing", "Modern", "Hazy", "Violet", "Crimson", "Azure"], ["Motion", "Echo", "Flow", "Pulse", "Mist", "Wave", "Bloom", "Drift", "Spectrum", "Dream", "Orbit", "Current", "Rhythm", "Form", "Light", "Signal", "Vision", "Shift", "Glow", "Space", "Texture", "Fragment", "Energy", "Field", "Prism", "Tide", "Trace", "Refraction", "Haze", "Pattern"]),
    "space": (["Cosmic", "Stellar", "Lunar", "Deep", "Infinite", "Astral", "Galactic", "Solar", "Nebula", "Celestial", "Midnight", "Distant", "Radiant", "Frozen", "Silent", "Endless", "Crimson", "Azure", "Golden", "Mystic", "Dark", "Bright", "Ancient", "Orbital", "Starlit", "Vast", "Eternal", "Moonlit", "Supernova", "Ethereal"], ["Voyage", "Drift", "Horizon", "Dream", "Echo", "Journey", "Orbit", "Dust", "Frontier", "Light", "Galaxy", "Void", "Nebula", "Comet", "Moon", "Stars", "Signal", "Realm", "Sky", "Beyond", "Expanse", "Station", "Gravity", "Night", "Trail", "Wander", "Pulse", "Sphere", "Discovery", "Dawn"]),
    "cars": (["Midnight", "Turbo", "Crimson", "Silver", "Phantom", "Velocity", "Electric", "Racing", "Shadow", "Golden", "Carbon", "Chrome", "Rapid", "Urban", "Luxury", "Classic", "Stealth", "Scarlet", "Frozen", "Neon", "Black", "White", "Blue", "Red", "Street", "Thunder", "Silent", "Wild", "Precision", "Dynamic"], ["Drive", "Rush", "Machine", "Motion", "Legend", "Road", "Velocity", "Runner", "Cruiser", "Spirit", "Journey", "Garage", "Engine", "Ride", "Track", "Racer", "Pursuit", "Roadster", "Tour", "Cruise", "Circuit", "Power", "Speed", "Dream", "Force", "Flight", "Wheels", "Rev", "Chase", "Shift"]),
    "city": (["Midnight", "Neon", "Golden", "Rainy", "Quiet", "Electric", "Urban", "Hidden", "Twilight", "Skyline", "Modern", "Downtown", "Luminous", "Vibrant", "Silent", "Misty", "Busy", "Cosmic", "Late", "Bright", "Nocturnal", "Sunlit", "Glass", "Concrete", "Endless", "Distant", "Amber", "Secret", "Blue", "Urban"], ["Lights", "Streets", "Horizon", "Pulse", "Dream", "Glow", "Stories", "Reflections", "Heights", "Nights", "Avenue", "Crossing", "District", "Boulevard", "Windows", "Corners", "Skies", "Traffic", "Walk", "Dawn", "Rain", "Tower", "View", "Rhythm", "Rush", "Lane", "Moments", "City", "Signs", "Stories"]),
    "dark": (["Obsidian", "Shadow", "Midnight", "Silent", "Black", "Noir", "Eclipse", "Phantom", "Hidden", "Velvet", "Dark", "Smoky", "Moonlit", "Raven", "Deep", "Faded", "Dusky", "Onyx", "Mystic", "Cold", "Night", "Gothic", "Hollow", "Quiet", "Stormy", "Ashen", "Secret", "Twilight", "Obscure", "Shadowed"], ["Soul", "Void", "Whisper", "Night", "Ember", "Dream", "Haze", "Silence", "Echo", "Dusk", "Smoke", "Shade", "Mist", "Abyss", "Glow", "Rain", "Shadow", "Stillness", "Moon", "Depth", "Ritual", "Gloom", "Drift", "Veil", "Hollow", "Mystery", "Ash", "Dawn", "Nightfall", "Secret"]),
    "fantasy": (["Enchanted", "Mystic", "Ancient", "Moonlit", "Forgotten", "Crystal", "Celestial", "Sacred", "Hidden", "Eternal", "Arcane", "Whimsical", "Golden", "Shadowed", "Dreamy", "Royal", "Magical", "Fabled", "Emerald", "Silver", "Twilight", "Lost", "Ethereal", "Glowing", "Legendary", "Secret", "Timeless", "Wonderous", "Astral", "Mystical"], ["Realm", "Kingdom", "Forest", "Dream", "Quest", "Crown", "Valley", "Legend", "Gate", "Myth", "Castle", "Garden", "Woods", "Throne", "Tales", "Haven", "Journey", "Sanctuary", "Empire", "Citadel", "Path", "Portal", "Wonder", "Keep", "Lore", "Meadow", "Story", "Cavern", "Tower", "Odyssey"]),
    "technology": (["Quantum", "Digital", "Cyber", "Neon", "Future", "Virtual", "Electric", "Synthetic", "Pixel", "Chrome", "Atomic", "Binary", "Modern", "Smart", "Luminous", "Hyper", "Advanced", "Neural", "Data", "Cloud", "Robotic", "Futuristic", "Connected", "Infinite", "Dynamic", "Artificial", "Nano", "Signal", "Matrix", "Digital"], ["Pulse", "Core", "Grid", "Dream", "Signal", "Wave", "Matrix", "Circuit", "Vision", "Flow", "Network", "Code", "System", "Logic", "Future", "Data", "Link", "Node", "Frame", "Engine", "Interface", "Protocol", "Cloud", "Pixel", "Stream", "Vector", "Module", "Orbit", "Spectrum"]),
}

DEFAULT_WORDS = (["Golden", "Silent", "Mystic", "Hidden", "Dreamy", "Midnight", "Serene", "Electric", "Wild", "Eternal", "Radiant", "Quiet", "Luminous", "Secret", "Timeless", "Soft", "Vivid", "Moonlit", "Sunlit", "Infinite", "Gentle", "Noble", "Distant", "Cosmic", "Velvet", "Ancient", "Fresh", "Wandering", "Peaceful", "Brilliant"], ["Moment", "Dream", "Whisper", "Horizon", "Glow", "Journey", "Spirit", "Echo", "Vista", "Light", "Wonder", "Breeze", "Path", "Story", "Dawn", "Escape", "Drift", "Realm", "Sky", "Soul", "Promise", "Vision", "Haven", "Mystery", "Serenity", "Voyage", "Bloom", "Reflection", "Silence", "Magic"])
LEGACY_DIMENSIONS = re.compile(r"\b\d{2,5}\s*[xX×]\s*\d{2,5}\b")
LEGACY_NUMBER = re.compile(r"[-_ ]+\d{1,4}$")


def slug(value):
    value = re.sub(r"[^a-zA-Z0-9 ]+", "", value.replace("_", " ").replace("-", " "))
    return re.sub(r"\s+", "-", value.strip()).lower()


def is_legacy_name(stem, category):
    normalized = stem.replace("_", " ").replace("-", " ").strip()
    return bool(LEGACY_DIMENSIONS.search(normalized) or (LEGACY_NUMBER.search(normalized) and normalized.lower().startswith(category.lower())))


def title_for(category, stem, attempt=0):
    first, second = TITLE_WORDS.get(category.lower(), DEFAULT_WORDS)
    digest = hashlib.sha256(f"{category}\0{stem}\0{attempt}".encode()).digest()
    return f"{first[digest[0] % len(first)]} {second[digest[1] % len(second)]}"


def main():
    renamed = 0
    used = set()
    candidates = []

    for root in ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in EXTS:
                continue
            try:
                with Image.open(path):
                    pass
            except Exception:
                continue
            category = path.parent.name if path.parent != root else root.name
            if is_legacy_name(path.stem, category):
                candidates.append((path, category))
            else:
                used.add(path.stem.lower())

    for path, category in candidates:
        target = None
        for attempt in range(256):
            title = title_for(category, path.stem, attempt)
            filename = slug(title)
            if filename and filename.lower() not in used:
                target = path.with_name(f"{filename}{path.suffix.lower()}")
                break

        if target is None:
            digest = hashlib.sha256(f"{category}\0{path.stem}".encode()).hexdigest()[:8]
            target = path.with_name(f"{slug(title_for(category, path.stem))}-{digest}{path.suffix.lower()}")

        if target == path:
            used.add(path.stem.lower())
            continue

        print(f"{path} -> {target}")
        path.rename(target)
        used.add(target.stem.lower())
        renamed += 1

    print(f"Renamed {renamed} legacy wallpaper(s) with stable category-aware titles.")


if __name__ == "__main__":
    main()
