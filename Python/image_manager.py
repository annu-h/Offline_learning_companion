"""
Lumi - Image Manager Module
Loads, resizes, and caches local educational images for Tkinter GUI.
Supports PNG, JPG, JPEG with aspect ratio preservation and automatic fallback generation.
100% Offline.
"""

from pathlib import Path
from typing import Tuple, Optional, Dict
from PIL import Image, ImageTk, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = BASE_DIR / "Images"

# Cache for loaded images: key -> (PIL.Image, ImageTk.PhotoImage)
_IMAGE_CACHE: Dict[str, Image.Image] = {}
_TK_CACHE: Dict[str, ImageTk.PhotoImage] = {}


def get_image_path(category: str, name: str) -> Optional[Path]:
    """Finds an image file under Images/<category>/<name>.(png|jpg|jpeg)."""
    cat_dir = IMAGES_DIR / category
    if not cat_dir.exists():
        return None

    # Normalize name
    clean_name = str(name).strip().lower().replace(" ", "_")
    candidates = [
        clean_name + ".png",
        clean_name + ".jpg",
        clean_name + ".jpeg",
        str(name).strip() + ".png",
        str(name).strip().upper() + ".png",
        str(name).strip().lower() + ".png",
    ]

    for candidate in candidates:
        target = cat_dir / candidate
        if target.is_file():
            return target

    return None


def resize_and_fit(img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
    """Resizes an image preserving aspect ratio and pads to fit target_size."""
    target_w, target_h = target_size
    img_w, img_h = img.size

    if img_w == 0 or img_h == 0:
        return Image.new("RGBA", target_size, (255, 255, 255, 0))

    ratio = min(target_w / img_w, target_h / img_h)
    new_w = max(1, int(img_w * ratio))
    new_h = max(1, int(img_h * ratio))

    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = Image.LANCZOS

    resized = img.resize((new_w, new_h), resample=resample)

    # Place centered on transparent canvas
    canvas = Image.new("RGBA", target_size, (255, 255, 255, 0))
    paste_x = (target_w - new_w) // 2
    paste_y = (target_h - new_h) // 2

    if resized.mode in ("RGBA", "LA") or (resized.mode == "P" and "transparency" in resized.info):
        canvas.paste(resized, (paste_x, paste_y), mask=resized.convert("RGBA"))
    else:
        canvas.paste(resized, (paste_x, paste_y))

    return canvas


def create_fallback_card(
    title: str = "",
    subtitle: str = "",
    emoji: str = "",
    bg_color: str = "#E0F2FE",
    size: Tuple[int, int] = (250, 250)
) -> Image.Image:
    """Dynamically creates a clean, child-friendly fallback card if image file is missing."""
    w, h = size
    card = Image.new("RGBA", size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(card)

    # Draw rounded background card
    margin = 8
    draw.rounded_rectangle(
        [margin, margin, w - margin, h - margin],
        radius=24,
        fill=bg_color,
        outline="#38BDF8",
        width=3
    )

    # Use default font
    try:
        font_large = ImageFont.truetype("arial.ttf", 48)
        font_mid = ImageFont.truetype("arial.ttf", 22)
    except Exception:
        font_large = ImageFont.load_default()
        font_mid = ImageFont.load_default()

    # Draw text
    display_text = title if title else emoji
    if display_text:
        bbox = draw.textbbox((0, 0), display_text, font=font_large)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = (w - tw) // 2
        ty = (h - th) // 2 - (15 if subtitle else 0)
        draw.text((tx, ty), display_text, fill="#0F172A", font=font_large)

    if subtitle:
        sbox = draw.textbbox((0, 0), subtitle, font=font_mid)
        sw = sbox[2] - sbox[0]
        sx = (w - sw) // 2
        sy = (h // 2) + 30
        draw.text((sx, sy), subtitle, fill="#475569", font=font_mid)

    return card


def load_pil_image(
    category: str,
    name: str,
    size: Tuple[int, int] = (250, 250),
    fallback_title: str = "",
    fallback_subtitle: str = "",
    fallback_emoji: str = "",
    fallback_bg: str = "#E0F2FE"
) -> Image.Image:
    """Loads a PIL image from disk or returns a generated fallback."""
    cache_key = f"{category}:{name}:{size[0]}x{size[1]}"
    if cache_key in _IMAGE_CACHE:
        return _IMAGE_CACHE[cache_key]

    path = get_image_path(category, name)
    if path and path.exists():
        try:
            with Image.open(path) as img:
                img_copy = img.convert("RGBA")
                processed = resize_and_fit(img_copy, size)
                _IMAGE_CACHE[cache_key] = processed
                return processed
        except Exception:
            pass

    # Generate safe fallback
    fallback = create_fallback_card(
        title=fallback_title or str(name),
        subtitle=fallback_subtitle,
        emoji=fallback_emoji,
        bg_color=fallback_bg,
        size=size
    )
    _IMAGE_CACHE[cache_key] = fallback
    return fallback


def get_tk_image(
    category: str,
    name: str,
    size: Tuple[int, int] = (250, 250),
    fallback_title: str = "",
    fallback_subtitle: str = "",
    fallback_emoji: str = "",
    fallback_bg: str = "#E0F2FE"
) -> ImageTk.PhotoImage:
    """Returns a Tkinter-compatible PhotoImage for display in GUI."""
    cache_key = f"tk:{category}:{name}:{size[0]}x{size[1]}"
    if cache_key in _TK_CACHE:
        return _TK_CACHE[cache_key]

    pil_img = load_pil_image(
        category=category,
        name=name,
        size=size,
        fallback_title=fallback_title,
        fallback_subtitle=fallback_subtitle,
        fallback_emoji=fallback_emoji,
        fallback_bg=fallback_bg
    )
    tk_img = ImageTk.PhotoImage(pil_img)
    _TK_CACHE[cache_key] = tk_img
    return tk_img


# Category-specific helpers
def get_alphabet_image(letter: str, word: str = "", emoji: str = "", size: Tuple[int, int] = (250, 250)) -> ImageTk.PhotoImage:
    return get_tk_image("alphabet", word or letter, size=size, fallback_title=letter, fallback_subtitle=word, fallback_emoji=emoji, fallback_bg="#FEF3C7")


def get_animal_image(animal: str, emoji: str = "", size: Tuple[int, int] = (250, 250)) -> ImageTk.PhotoImage:
    return get_tk_image("animals", animal, size=size, fallback_title=animal.capitalize(), fallback_emoji=emoji, fallback_bg="#DCFCE7")


def get_color_image(color: str, hex_val: str = "#E0F2FE", size: Tuple[int, int] = (250, 250)) -> ImageTk.PhotoImage:
    return get_tk_image("colors", color, size=size, fallback_title=color.capitalize(), fallback_bg=hex_val)


def get_number_image(number: int, word: str = "", emoji: str = "", size: Tuple[int, int] = (250, 250)) -> ImageTk.PhotoImage:
    return get_tk_image("numbers", str(number), size=size, fallback_title=str(number), fallback_subtitle=word.capitalize(), fallback_emoji=emoji, fallback_bg="#E0E7FF")


def get_quiz_image(name: str, size: Tuple[int, int] = (250, 250)) -> ImageTk.PhotoImage:
    return get_tk_image("quiz", name, size=size, fallback_title="Quiz Time! 🌟", fallback_bg="#FCE7F3")


def get_ui_image(name: str, size: Tuple[int, int] = (250, 250)) -> ImageTk.PhotoImage:
    return get_tk_image("ui", name, size=size, fallback_title="Lumi 🌟", fallback_bg="#F3E8FF")


def clear_cache():
    """Clears cached images."""
    _IMAGE_CACHE.clear()
    _TK_CACHE.clear()
