"""
Lumi - Dataset Loader Module
Safely loads and parses educational datasets from Dataset/ directory.
Handles missing files, encoding errors, malformed rows, and provides fallbacks.
100% Offline.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "Dataset"


def _safe_read_csv(file_name: str) -> List[Dict[str, str]]:
    """Reads a CSV file safely with multiple encoding fallbacks and stripping."""
    file_path = DATASET_DIR / file_name
    if not file_path.exists():
        return []

    encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            with open(file_path, mode="r", encoding=enc, errors="replace") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames is None:
                    continue
                rows = []
                for row in reader:
                    cleaned_row = {
                        (k.strip() if k else ""): (v.strip() if v else "")
                        for k, v in row.items()
                        if k is not None
                    }
                    # Filter out empty rows
                    if any(cleaned_row.values()):
                        rows.append(cleaned_row)
                return rows
        except Exception:
            continue
    return []


# ==========================================
# Fallbacks for robustness
# ==========================================
FALLBACK_ALPHABETS = [
    {"letter": "A", "word": "Apple", "emoji": "🍎"},
    {"letter": "B", "word": "Ball", "emoji": "⚽"},
    {"letter": "C", "word": "Cat", "emoji": "🐱"},
    {"letter": "D", "word": "Dog", "emoji": "🐶"},
    {"letter": "E", "word": "Elephant", "emoji": "🐘"},
    {"letter": "F", "word": "Fish", "emoji": "🐟"},
    {"letter": "G", "word": "Grapes", "emoji": "🍇"},
    {"letter": "H", "word": "Horse", "emoji": "🐴"},
    {"letter": "I", "word": "Ice cream", "emoji": "🍦"},
    {"letter": "J", "word": "Juice", "emoji": "🧃"},
    {"letter": "K", "word": "Kite", "emoji": "🪁"},
    {"letter": "L", "word": "Lion", "emoji": "🦁"},
    {"letter": "M", "word": "Mango", "emoji": "🥭"},
    {"letter": "N", "word": "Nest", "emoji": "🪺"},
    {"letter": "O", "word": "Orange", "emoji": "🍊"},
    {"letter": "P", "word": "Parrot", "emoji": "🦜"},
    {"letter": "Q", "word": "Queen", "emoji": "👑"},
    {"letter": "R", "word": "Rabbit", "emoji": "🐰"},
    {"letter": "S", "word": "Sun", "emoji": "☀️"},
    {"letter": "T", "word": "Tiger", "emoji": "🐯"},
    {"letter": "U", "word": "Umbrella", "emoji": "☂️"},
    {"letter": "V", "word": "Van", "emoji": "🚐"},
    {"letter": "W", "word": "Watch", "emoji": "⌚"},
    {"letter": "X", "word": "Xylophone", "emoji": "🎵"},
    {"letter": "Y", "word": "Yo-yo", "emoji": "🪀"},
    {"letter": "Z", "word": "Zebra", "emoji": "🦓"},
]

FALLBACK_ANIMALS = [
    {"animal": "dog", "sound": "bark", "emoji": "🐶"},
    {"animal": "cat", "sound": "meow", "emoji": "🐱"},
    {"animal": "cow", "sound": "moo", "emoji": "🐮"},
    {"animal": "lion", "sound": "roar", "emoji": "🦁"},
    {"animal": "duck", "sound": "quack", "emoji": "🦆"},
    {"animal": "sheep", "sound": "baa", "emoji": "🐑"},
    {"animal": "horse", "sound": "neigh", "emoji": "🐴"},
    {"animal": "elephant", "sound": "trumpet", "emoji": "🐘"},
    {"animal": "monkey", "sound": "chatter", "emoji": "🐒"},
    {"animal": "bird", "sound": "chirp", "emoji": "🐦"},
]

FALLBACK_COLORS = [
    {"color": "red", "example": "apple", "hex": "#E53935", "emoji": "🔴"},
    {"color": "yellow", "example": "banana", "hex": "#FDD835", "emoji": "🟡"},
    {"color": "green", "example": "leaf", "hex": "#43A047", "emoji": "🟢"},
    {"color": "blue", "example": "sky", "hex": "#1E88E5", "emoji": "🔵"},
    {"color": "orange", "example": "orange", "hex": "#FB8C00", "emoji": "🟠"},
    {"color": "purple", "example": "grapes", "hex": "#8E24AA", "emoji": "🟣"},
    {"color": "pink", "example": "flower", "hex": "#EC407A", "emoji": "🌸"},
    {"color": "brown", "example": "tree", "hex": "#6D4C41", "emoji": "🟤"},
    {"color": "black", "example": "night", "hex": "#212121", "emoji": "⚫"},
    {"color": "white", "example": "snow", "hex": "#FAFAFA", "emoji": "⚪"},
]

FALLBACK_NUMBERS = [
    {"number": 1, "word": "one", "emoji": "1️⃣"},
    {"number": 2, "word": "two", "emoji": "2️⃣"},
    {"number": 3, "word": "three", "emoji": "3️⃣"},
    {"number": 4, "word": "four", "emoji": "4️⃣"},
    {"number": 5, "word": "five", "emoji": "5️⃣"},
    {"number": 6, "word": "six", "emoji": "6️⃣"},
    {"number": 7, "word": "seven", "emoji": "7️⃣"},
    {"number": 8, "word": "eight", "emoji": "8️⃣"},
    {"number": 9, "word": "nine", "emoji": "9️⃣"},
    {"number": 10, "word": "ten", "emoji": "🔟"},
]

FALLBACK_QUIZ = [
    {"category": "Alphabet", "question": "What letter comes after A?", "answer": "B", "accepted": ["b", "B"]},
    {"category": "Alphabet", "question": "What letter comes after C?", "answer": "D", "accepted": ["d", "D"]},
    {"category": "Numbers", "question": "What number comes after two?", "answer": "three", "accepted": ["3", "three"]},
    {"category": "Numbers", "question": "What number comes after nine?", "answer": "ten", "accepted": ["10", "ten"]},
    {"category": "Colors", "question": "What color is a banana?", "answer": "yellow", "accepted": ["yellow"]},
    {"category": "Colors", "question": "What color is the sky?", "answer": "blue", "accepted": ["blue"]},
    {"category": "Animals", "question": "What animal says meow?", "answer": "cat", "accepted": ["cat", "the cat"]},
    {"category": "Animals", "question": "What animal says moo?", "answer": "cow", "accepted": ["cow", "the cow"]},
    {"category": "Math", "question": "What is two plus three?", "answer": "5", "accepted": ["5", "five"]},
    {"category": "Math", "question": "What is ten minus six?", "answer": "4", "accepted": ["4", "four"]},
]

FALLBACK_MATH: List[Tuple[str, int, str]] = [
    ("What is two plus three?", 5, "2 + 3 = ?"),
    ("What is seven minus four?", 3, "7 - 4 = ?"),
    ("What is three times two?", 6, "3 × 2 = ?"),
    ("What is five plus five?", 10, "5 + 5 = ?"),
    ("What is ten minus six?", 4, "10 - 6 = ?"),
    ("What is four plus four?", 8, "4 + 4 = ?"),
    ("What is nine minus two?", 7, "9 - 2 = ?"),
    ("What is one plus six?", 7, "1 + 6 = ?"),
    ("What is six plus two?", 8, "6 + 2 = ?"),
    ("What is eight minus three?", 5, "8 - 3 = ?"),
    ("What is four times two?", 8, "4 × 2 = ?"),
    ("What is three plus four?", 7, "3 + 4 = ?"),
    ("What is ten minus two?", 8, "10 - 2 = ?"),
    ("What is five plus four?", 9, "5 + 4 = ?"),
    ("What is nine minus five?", 4, "9 - 5 = ?"),
]


def load_alphabets() -> List[Dict[str, str]]:
    """Loads alphabets.csv with columns: letter, word, emoji."""
    rows = _safe_read_csv("alphabets.csv")
    if not rows:
        return FALLBACK_ALPHABETS
    result = []
    for r in rows:
        letter = r.get("letter", "").strip().upper()
        word = r.get("word", "").strip()
        emoji = r.get("emoji", "").strip()
        if letter and word:
            result.append({"letter": letter, "word": word, "emoji": emoji})
    return result if result else FALLBACK_ALPHABETS


def load_animals() -> List[Dict[str, str]]:
    """Loads animals.csv with columns: animal, sound, emoji."""
    rows = _safe_read_csv("animals.csv")
    if not rows:
        return [{"animal": a["animal"], "name": a["animal"], "sound": a["sound"], "emoji": a["emoji"]} for a in FALLBACK_ANIMALS]
    result = []
    for r in rows:
        animal = r.get("animal", "").strip().lower()
        sound = r.get("sound", "").strip().lower()
        emoji = r.get("emoji", "").strip()
        if animal and sound:
            result.append({"animal": animal, "name": animal, "sound": sound, "emoji": emoji})
    return result if result else [{"animal": a["animal"], "name": a["animal"], "sound": a["sound"], "emoji": a["emoji"]} for a in FALLBACK_ANIMALS]


def load_colors() -> List[Dict[str, str]]:
    """Loads colors.csv with columns: color, example, hex, emoji."""
    rows = _safe_read_csv("colors.csv")
    if not rows:
        return FALLBACK_COLORS
    result = []
    for r in rows:
        color = r.get("color", "").strip().lower()
        example = r.get("example", "").strip().lower()
        hex_val = r.get("hex", "#CCCCCC").strip()
        emoji = r.get("emoji", "").strip()
        if color:
            result.append({"color": color, "example": example, "hex": hex_val, "emoji": emoji})
    return result if result else FALLBACK_COLORS


def load_numbers() -> List[Dict[str, Any]]:
    """Loads numbers.csv with columns: number, word, emoji."""
    rows = _safe_read_csv("numbers.csv")
    if not rows:
        return FALLBACK_NUMBERS
    result = []
    for r in rows:
        num_str = r.get("number", "").strip()
        word = r.get("word", "").strip().lower()
        emoji = r.get("emoji", "").strip()
        try:
            num = int(num_str)
        except ValueError:
            continue
        result.append({"number": num, "word": word, "emoji": emoji})
    return result if result else FALLBACK_NUMBERS


def load_math_questions() -> List[Tuple[str, int, str]]:
    """Returns math practice questions with tuples (question_text, answer_int, formula_str)."""
    return FALLBACK_MATH


def load_quiz(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Loads quiz.csv with columns: category, question, answer, accepted."""
    rows = _safe_read_csv("quiz.csv")
    if not rows:
        quiz_data = FALLBACK_QUIZ
    else:
        quiz_data = []
        for r in rows:
            cat = r.get("category", "General").strip()
            q = r.get("question", "").strip()
            ans = r.get("answer", "").strip()
            acc_str = r.get("accepted", "").strip()
            if not q or not ans:
                continue
            # Parse accepted pipe-separated values
            accepted_list = [ans]
            if acc_str:
                for a in acc_str.split("|"):
                    a_clean = a.strip()
                    if a_clean and a_clean not in accepted_list:
                        accepted_list.append(a_clean)
            quiz_data.append({
                "category": cat,
                "question": q,
                "answer": ans,
                "accepted": accepted_list
            })
    if category:
        filtered = [q for q in quiz_data if q["category"].lower() == category.lower()]
        return filtered if filtered else quiz_data
    return quiz_data if quiz_data else FALLBACK_QUIZ


def load_stories() -> List[Dict[str, Any]]:
    """Loads stories.txt format: # Title followed by lines, ending with The End."""
    file_path = DATASET_DIR / "stories.txt"
    if not file_path.exists():
        return [
            {
                "title": "The Little Star",
                "content": "Once upon a time, a little star shone bright in the night sky. It twinkled happily and watched over all the sleeping children. The End.",
                "lines": [
                    "Once upon a time, a little star shone bright in the night sky.",
                    "It twinkled happily and watched over all the sleeping children.",
                    "The End."
                ]
            }
        ]

    stories = []
    current_title = ""
    current_lines = []

    try:
        with open(file_path, mode="r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line_str = line.strip()
                if line_str.startswith("#"):
                    if current_title and current_lines:
                        stories.append({
                            "title": current_title,
                            "content": " ".join(current_lines),
                            "lines": list(current_lines)
                        })
                        current_lines = []
                    current_title = line_str.lstrip("#").strip()
                elif line_str:
                    current_lines.append(line_str)

        if current_title and current_lines:
            stories.append({
                "title": current_title,
                "content": " ".join(current_lines),
                "lines": list(current_lines)
            })
    except Exception:
        pass

    return stories
