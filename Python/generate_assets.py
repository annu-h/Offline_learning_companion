"""
Lumi - Local Asset Generator
Generates clean, colorful, child-friendly educational image assets using Pillow.
100% Offline.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = BASE_DIR / "Images"

# Ensure all directories exist
for cat in ["alphabet", "animals", "colors", "numbers", "quiz", "ui"]:
    (IMAGES_DIR / cat).mkdir(parents=True, exist_ok=True)


def get_fonts():
    try:
        f_huge = ImageFont.truetype("arial.ttf", 64)
        f_large = ImageFont.truetype("arial.ttf", 44)
        f_mid = ImageFont.truetype("arial.ttf", 28)
        f_small = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        f_huge = ImageFont.load_default()
        f_large = ImageFont.load_default()
        f_mid = ImageFont.load_default()
        f_small = ImageFont.load_default()
    return f_huge, f_large, f_mid, f_small


def draw_card_base(draw, size, bg_color, border_color="#38BDF8"):
    w, h = size
    # Outer soft glow/border
    draw.rounded_rectangle([6, 6, w - 6, h - 6], radius=32, fill=bg_color, outline=border_color, width=4)
    # Inner decorative border
    draw.rounded_rectangle([14, 14, w - 14, h - 14], radius=24, outline="#FFFFFF", width=2)


def draw_centered_text(draw, text, font, pos_y, color="#0F172A", size=(300, 300)):
    w, _ = size
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    tx = (w - tw) // 2
    draw.text((tx, pos_y), text, fill=color, font=font)


# ==========================================
# ALPHABET ASSETS
# ==========================================
ALPHABET_DATA = [
    ("A", "apple", "Apple", "#FEE2E2", "#EF4444", "🍎"),
    ("B", "ball", "Ball", "#DBEAFE", "#3B82F6", "⚽"),
    ("C", "cat", "Cat", "#FEF3C7", "#F59E0B", "🐱"),
    ("D", "dog", "Dog", "#E0E7FF", "#6366F1", "🐶"),
    ("E", "elephant", "Elephant", "#EDE9FE", "#8B5CF6", "🐘"),
    ("F", "fish", "Fish", "#CFFAFE", "#06B6D4", "🐟"),
    ("G", "grapes", "Grapes", "#F3E8FF", "#A855F7", "🍇"),
    ("H", "horse", "Horse", "#FED7AA", "#F97316", "🐴"),
    ("I", "ice_cream", "Ice cream", "#FCE7F3", "#EC4899", "🍦"),
    ("J", "juice", "Juice", "#FEF08A", "#EAB308", "🧃"),
    ("K", "kite", "Kite", "#CCFBF1", "#14B8A6", "🪁"),
    ("L", "lion", "Lion", "#FEF3C7", "#D97706", "🦁"),
    ("M", "mango", "Mango", "#FED7AA", "#EA580C", "🥭"),
    ("N", "nest", "Nest", "#E2E8F0", "#64748B", "🪺"),
    ("O", "orange", "Orange", "#FFEDD5", "#F97316", "🍊"),
    ("P", "parrot", "Parrot", "#DCFCE7", "#22C55E", "🦜"),
    ("Q", "queen", "Queen", "#FCE7F3", "#DB2777", "👑"),
    ("R", "rabbit", "Rabbit", "#F1F5F9", "#94A3B8", "🐰"),
    ("S", "sun", "Sun", "#FEF9C3", "#EAB308", "☀️"),
    ("T", "tiger", "Tiger", "#FFEDD5", "#EA580C", "🐯"),
    ("U", "umbrella", "Umbrella", "#E0E7FF", "#4F46E5", "☂️"),
    ("V", "van", "Van", "#E0F2FE", "#0284C7", "🚐"),
    ("W", "watch", "Watch", "#F3E8FF", "#9333EA", "⌚"),
    ("X", "xylophone", "Xylophone", "#CCFBF1", "#0D9488", "🎵"),
    ("Y", "yo-yo", "Yo-yo", "#FFE4E6", "#E11D48", "🪀"),
    ("Z", "zebra", "Zebra", "#F1F5F9", "#334155", "🦓"),
]


def generate_alphabet_images():
    f_huge, f_large, f_mid, f_small = get_fonts()
    size = (300, 300)

    for letter, filename, word, bg_color, accent_color, emoji in ALPHABET_DATA:
        img = Image.new("RGBA", size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        draw_card_base(draw, size, bg_color, accent_color)

        # Draw Letter Badge circle
        cx, cy = 150, 115
        radius = 55
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill="#FFFFFF", outline=accent_color, width=3)

        # Draw big letter inside badge
        draw_centered_text(draw, letter, f_huge, 80, color=accent_color, size=size)

        # Subtitle banner: "A is for Apple"
        draw_centered_text(draw, f"{letter} is for", f_mid, 185, color="#64748B", size=size)
        draw_centered_text(draw, word, f_large, 220, color="#0F172A", size=size)

        # Save both as word.png and letter.png
        out_path1 = IMAGES_DIR / "alphabet" / f"{filename}.png"
        out_path2 = IMAGES_DIR / "alphabet" / f"{letter}.png"
        img.save(out_path1, "PNG")
        img.save(out_path2, "PNG")


# ==========================================
# ANIMALS ASSETS
# ==========================================
ANIMALS_DATA = [
    ("dog", "Dog", "Woof! Woof!", "#FEF3C7", "#D97706"),
    ("cat", "Cat", "Meow! Meow!", "#FCE7F3", "#EC4899"),
    ("cow", "Cow", "Moo! Moo!", "#DCFCE7", "#16A34A"),
    ("lion", "Lion", "Roar! Roar!", "#FFEDD5", "#EA580C"),
    ("duck", "Duck", "Quack! Quack!", "#FEF9C3", "#CA8A04"),
    ("sheep", "Sheep", "Baa! Baa!", "#F1F5F9", "#64748B"),
    ("horse", "Horse", "Neigh! Neigh!", "#FED7AA", "#C2410C"),
    ("elephant", "Elephant", "Trumpet! Pawoo!", "#EDE9FE", "#7C3AED"),
    ("monkey", "Monkey", "Ooh Ooh Aah Aah!", "#FEF3C7", "#B45309"),
    ("bird", "Bird", "Chirp! Tweet!", "#CFFAFE", "#0891B2"),
]


def generate_animal_images():
    f_huge, f_large, f_mid, f_small = get_fonts()
    size = (300, 300)

    for name, title, sound, bg_color, accent_color in ANIMALS_DATA:
        img = Image.new("RGBA", size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        draw_card_base(draw, size, bg_color, accent_color)

        # Circular animal badge
        cx, cy = 150, 110
        radius = 58
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill="#FFFFFF", outline=accent_color, width=3)

        # Cute decorative animal initials/features badge
        draw_centered_text(draw, title[:2].upper(), f_huge, 78, color=accent_color, size=size)

        # Animal Title
        draw_centered_text(draw, title, f_large, 180, color="#0F172A", size=size)

        # Animal sound bubble
        sound_box = [40, 235, 260, 275]
        draw.rounded_rectangle(sound_box, radius=15, fill="#FFFFFF", outline=accent_color, width=2)
        draw_centered_text(draw, sound, f_small, 243, color=accent_color, size=size)

        out_path = IMAGES_DIR / "animals" / f"{name}.png"
        img.save(out_path, "PNG")


# ==========================================
# COLORS ASSETS
# ==========================================
COLORS_DATA = [
    ("red", "Red", "Apple", "#EF4444", "#FFFFFF"),
    ("yellow", "Yellow", "Banana", "#FACC15", "#0F172A"),
    ("green", "Green", "Leaf", "#22C55E", "#FFFFFF"),
    ("blue", "Blue", "Sky", "#3B82F6", "#FFFFFF"),
    ("orange", "Orange", "Orange", "#F97316", "#FFFFFF"),
    ("purple", "Purple", "Grapes", "#A855F7", "#FFFFFF"),
    ("pink", "Pink", "Flower", "#EC4899", "#FFFFFF"),
    ("brown", "Brown", "Tree", "#854D0E", "#FFFFFF"),
    ("black", "Black", "Night", "#1E293B", "#FFFFFF"),
    ("white", "White", "Snow", "#F8FAFC", "#0F172A"),
]


def generate_color_images():
    f_huge, f_large, f_mid, f_small = get_fonts()
    size = (300, 300)

    for name, title, example, hex_val, text_col in COLORS_DATA:
        img = Image.new("RGBA", size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        # Background card in matching pastel or white with bold swatch
        border_col = hex_val if name != "white" else "#CBD5E1"
        draw_card_base(draw, size, "#FFFFFF", border_col)

        # Large Color Swatch with glossy highlight
        swatch_rect = [45, 35, 255, 175]
        draw.rounded_rectangle(swatch_rect, radius=24, fill=hex_val, outline="#CBD5E1", width=2)

        # Title
        draw_centered_text(draw, title, f_large, 190, color="#0F172A", size=size)

        # Example text
        draw_centered_text(draw, f"Like a {example}", f_mid, 240, color="#64748B", size=size)

        out_path = IMAGES_DIR / "colors" / f"{name}.png"
        img.save(out_path, "PNG")


# ==========================================
# NUMBERS ASSETS
# ==========================================
NUMBERS_DATA = [
    (1, "one", "#DBEAFE", "#2563EB"),
    (2, "two", "#DCFCE7", "#16A34A"),
    (3, "three", "#FEF3C7", "#D97706"),
    (4, "four", "#FCE7F3", "#DB2777"),
    (5, "five", "#EDE9FE", "#7C3AED"),
    (6, "six", "#CFFAFE", "#0891B2"),
    (7, "seven", "#FED7AA", "#EA580C"),
    (8, "eight", "#F3E8FF", "#9333EA"),
    (9, "nine", "#FFE4E6", "#E11D48"),
    (10, "ten", "#FEF9C3", "#CA8A04"),
]


def generate_number_images():
    f_huge, f_large, f_mid, f_small = get_fonts()
    size = (300, 300)

    for num, word, bg_color, accent_color in NUMBERS_DATA:
        img = Image.new("RGBA", size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        draw_card_base(draw, size, bg_color, accent_color)

        # Number circle badge
        cx, cy = 150, 95
        radius = 50
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill="#FFFFFF", outline=accent_color, width=3)

        # Giant number
        draw_centered_text(draw, str(num), f_huge, 65, color=accent_color, size=size)

        # Word label
        draw_centered_text(draw, word.upper(), f_large, 155, color="#0F172A", size=size)

        # Draw counting dots/stars
        # Layout dots neatly across bottom
        dot_radius = 8 if num > 5 else 11
        spacing = 22 if num > 5 else 28
        total_w = (num - 1) * spacing
        start_x = (300 - total_w) // 2
        dot_y = 235

        for i in range(num):
            dx = start_x + (i * spacing)
            draw.ellipse([dx - dot_radius, dot_y - dot_radius, dx + dot_radius, dot_y + dot_radius], fill=accent_color, outline="#FFFFFF", width=1)

        draw_centered_text(draw, f"Count: {num}", f_small, 260, color="#64748B", size=size)

        out_path = IMAGES_DIR / "numbers" / f"{num}.png"
        img.save(out_path, "PNG")


# ==========================================
# QUIZ ASSETS
# ==========================================
def generate_quiz_images():
    f_huge, f_large, f_mid, f_small = get_fonts()
    size = (300, 300)

    # 1. Quiz Star
    img_star = Image.new("RGBA", size, (255, 255, 255, 0))
    d = ImageDraw.Draw(img_star)
    draw_card_base(d, size, "#FEF3C7", "#F59E0B")
    # Star badge
    d.ellipse([90, 45, 210, 165], fill="#FFFFFF", outline="#F59E0B", width=4)
    draw_centered_text(d, "★", f_huge, 65, color="#F59E0B", size=size)
    draw_centered_text(d, "QUIZ TIME", f_large, 185, color="#0F172A", size=size)
    draw_centered_text(d, "Show what you know!", f_small, 238, color="#64748B", size=size)
    img_star.save(IMAGES_DIR / "quiz" / "quiz_star.png", "PNG")

    # 2. Correct Badge
    img_cor = Image.new("RGBA", size, (255, 255, 255, 0))
    d = ImageDraw.Draw(img_cor)
    draw_card_base(d, size, "#DCFCE7", "#16A34A")
    d.ellipse([90, 45, 210, 165], fill="#FFFFFF", outline="#16A34A", width=4)
    draw_centered_text(d, "✓", f_huge, 65, color="#16A34A", size=size)
    draw_centered_text(d, "CORRECT!", f_large, 185, color="#16A34A", size=size)
    draw_centered_text(d, "Awesome Job! ⭐", f_mid, 235, color="#0F172A", size=size)
    img_cor.save(IMAGES_DIR / "quiz" / "correct.png", "PNG")

    # 3. Try Again Badge
    img_try = Image.new("RGBA", size, (255, 255, 255, 0))
    d = ImageDraw.Draw(img_try)
    draw_card_base(d, size, "#FFEDD5", "#EA580C")
    d.ellipse([90, 45, 210, 165], fill="#FFFFFF", outline="#EA580C", width=4)
    draw_centered_text(d, "↺", f_huge, 65, color="#EA580C", size=size)
    draw_centered_text(d, "Good Try!", f_large, 185, color="#EA580C", size=size)
    draw_centered_text(d, "Let's keep learning! 💪", f_small, 238, color="#0F172A", size=size)
    img_try.save(IMAGES_DIR / "quiz" / "try_again.png", "PNG")

    # 4. Trophy Badge
    img_trophy = Image.new("RGBA", size, (255, 255, 255, 0))
    d = ImageDraw.Draw(img_trophy)
    draw_card_base(d, size, "#FEF9C3", "#CA8A04")
    d.ellipse([90, 45, 210, 165], fill="#FFFFFF", outline="#CA8A04", width=4)
    draw_centered_text(d, "🏆", f_huge, 65, color="#CA8A04", size=size)
    draw_centered_text(d, "GREAT WORK!", f_large, 185, color="#CA8A04", size=size)
    draw_centered_text(d, "You are a Champion! 🌟", f_small, 238, color="#0F172A", size=size)
    img_trophy.save(IMAGES_DIR / "quiz" / "trophy.png", "PNG")


# ==========================================
# UI ASSETS
# ==========================================
def generate_ui_images():
    f_huge, f_large, f_mid, f_small = get_fonts()
    size = (300, 300)

    # 1. Lumi Logo
    img_lumi = Image.new("RGBA", size, (255, 255, 255, 0))
    d = ImageDraw.Draw(img_lumi)
    draw_card_base(d, size, "#F0FDF4", "#10B981")
    # Friendly robot/companion face
    d.ellipse([85, 40, 215, 170], fill="#FFFFFF", outline="#10B981", width=4)
    # Robot eyes & smile
    d.ellipse([110, 80, 135, 105], fill="#10B981")
    d.ellipse([165, 80, 190, 105], fill="#10B981")
    d.arc([120, 105, 180, 140], start=0, end=180, fill="#10B981", width=5)
    # Cute antennae
    d.line([150, 40, 150, 20], fill="#10B981", width=4)
    d.ellipse([142, 12, 158, 28], fill="#F59E0B")

    draw_centered_text(d, "LUMI", f_large, 185, color="#0F172A", size=size)
    draw_centered_text(d, "Learning Companion", f_small, 238, color="#10B981", size=size)
    img_lumi.save(IMAGES_DIR / "ui" / "lumi_logo.png", "PNG")

    # 2. Mic Active
    img_mic_act = Image.new("RGBA", (100, 100), (255, 255, 255, 0))
    d_m = ImageDraw.Draw(img_mic_act)
    d_m.ellipse([5, 5, 95, 95], fill="#EF4444", outline="#DC2626", width=3)
    d_m.rounded_rectangle([38, 22, 62, 58], radius=12, fill="#FFFFFF")
    d_m.arc([30, 35, 70, 68], start=0, end=180, fill="#FFFFFF", width=3)
    d_m.line([50, 68, 50, 80], fill="#FFFFFF", width=3)
    d_m.line([38, 80, 62, 80], fill="#FFFFFF", width=3)
    img_mic_act.save(IMAGES_DIR / "ui" / "mic_active.png", "PNG")

    # 3. Mic Idle
    img_mic_idle = Image.new("RGBA", (100, 100), (255, 255, 255, 0))
    d_mi = ImageDraw.Draw(img_mic_idle)
    d_mi.ellipse([5, 5, 95, 95], fill="#3B82F6", outline="#2563EB", width=3)
    d_mi.rounded_rectangle([38, 22, 62, 58], radius=12, fill="#FFFFFF")
    d_mi.arc([30, 35, 70, 68], start=0, end=180, fill="#FFFFFF", width=3)
    d_mi.line([50, 68, 50, 80], fill="#FFFFFF", width=3)
    d_mi.line([38, 80, 62, 80], fill="#FFFFFF", width=3)
    img_mic_idle.save(IMAGES_DIR / "ui" / "mic_idle.png", "PNG")

    # 4. Speaker
    img_spk = Image.new("RGBA", (100, 100), (255, 255, 255, 0))
    d_s = ImageDraw.Draw(img_spk)
    d_s.ellipse([5, 5, 95, 95], fill="#8B5CF6", outline="#7C3AED", width=3)
    # Speaker shape
    d_s.polygon([(25, 38), (40, 38), (58, 24), (58, 76), (40, 62), (25, 62)], fill="#FFFFFF")
    # Sound waves
    d_s.arc([52, 35, 72, 65], start=-60, end=60, fill="#FFFFFF", width=3)
    d_s.arc([52, 25, 84, 75], start=-60, end=60, fill="#FFFFFF", width=3)
    img_spk.save(IMAGES_DIR / "ui" / "speaker.png", "PNG")


def main():
    print("Generating local educational assets...")
    generate_alphabet_images()
    print("✓ Alphabet images generated (52 files: A-Z by letter and word)")
    generate_animal_images()
    print("✓ Animal images generated (10 files)")
    generate_color_images()
    print("✓ Color images generated (10 files)")
    generate_number_images()
    print("✓ Number images generated (10 files)")
    generate_quiz_images()
    print("✓ Quiz images generated (4 files)")
    generate_ui_images()
    print("✓ UI images generated (4 files)")
    print("All educational assets generated successfully!")


if __name__ == "__main__":
    main()
