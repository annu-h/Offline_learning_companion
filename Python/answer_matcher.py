"""
Lumi - Answer Normalization and Intent Matching Module
Provides robust, flexible offline matching for natural child speech responses.
Handles numbers (digits and words), articles, filler phrases, and fuzzy choices.
100% Offline.
"""

import re
import string
from typing import Optional, List, Dict, Any, Union

# Word to number mapping
WORD_TO_NUM: Dict[str, int] = {
    "zero": 0, "none": 0, "nil": 0,
    "one": 1, "won": 1, "first": 1,
    "two": 2, "to": 2, "too": 2, "second": 2,
    "three": 3, "tree": 3, "third": 3,
    "four": 4, "for": 4, "fore": 4, "fourth": 4,
    "five": 5, "fifth": 5,
    "six": 6, "sixth": 6,
    "seven": 7, "seventh": 7,
    "eight": 8, "ate": 8, "eighth": 8,
    "nine": 9, "ninth": 9,
    "ten": 10, "tenth": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
    "hundred": 100
}

# Conversational prefix and filler patterns to strip
FILLER_PATTERNS = [
    r"^the answer is\s+",
    r"^my answer is\s+",
    r"^answer is\s+",
    r"^i think the answer is\s+",
    r"^i think it is\s+",
    r"^i think it's\s+",
    r"^i think its\s+",
    r"^i think\s+",
    r"^it is\s+",
    r"^it's\s+",
    r"^its\s+",
    r"^is it\s+",
    r"^maybe\s+",
    r"^i guess\s+",
    r"^it must be\s+",
    r"^can it be\s+",
    r"^could it be\s+",
    r"^the\s+",
    r"^a\s+",
    r"^an\s+",
    r"^number\s+",
    r"^letter\s+",
    r"^color\s+",
    r"^colour\s+",
    r"^animal\s+"
]


def normalize_text(text: Optional[str]) -> str:
    """Lowercases, removes punctuation, and normalizes whitespace."""
    if text is None:
        return ""
    s = str(text).lower().strip()
    # Replace punctuation with spaces
    for p in string.punctuation:
        s = s.replace(p, " ")
    # Normalize whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


def clean_spoken_response(text: Optional[str]) -> str:
    """Strips conversational fillers, articles, and prefixes from spoken text."""
    s = normalize_text(text)
    changed = True
    while changed:
        changed = False
        for pat in FILLER_PATTERNS:
            new_s = re.sub(pat, "", s).strip()
            if new_s != s and len(new_s) > 0:
                s = new_s
                changed = True
                break
    return s


def extract_number(text: Optional[str]) -> Optional[int]:
    """Extracts a numeric value from digits or number words in the text."""
    if text is None:
        return None

    cleaned = normalize_text(text)
    words = cleaned.split()

    # 1. Direct digit match in whole string
    digits = re.findall(r"\b\d+\b", cleaned)
    if digits:
        try:
            return int(digits[0])
        except ValueError:
            pass

    # 2. Compound numbers (e.g., twenty one = 21, forty five = 45)
    if len(words) >= 2:
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            if w1 in ("twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"):
                if w2 in WORD_TO_NUM and 1 <= WORD_TO_NUM[w2] <= 9:
                    return WORD_TO_NUM[w1] + WORD_TO_NUM[w2]

    # 3. Match single number word
    for word in words:
        if word in WORD_TO_NUM:
            return WORD_TO_NUM[word]

    return None


def match_answer(
    spoken: Optional[str],
    target: Any,
    accepted: Optional[List[Union[str, int]]] = None
) -> bool:
    """
    Robustly checks if spoken response matches the target answer or any accepted variants.
    Handles:
    - Digits vs spelled numbers ('4' vs 'four', 'the answer is 4')
    - Articles and fillers ('the cat' vs 'cat', 'it is a dog' vs 'dog')
    - Exact matching, substring matching for unique tokens, and accepted list matching.
    """
    if spoken is None or target is None:
        return False

    raw_spoken = str(spoken)
    norm_spoken = normalize_text(raw_spoken)
    clean_spoken = clean_spoken_response(raw_spoken)

    # Prepare list of target representations
    targets: List[str] = [str(target)]
    if accepted:
        for acc in accepted:
            if acc is not None:
                targets.append(str(acc))

    # 1. Numeric comparison if target is numeric
    target_num = None
    if isinstance(target, int):
        target_num = target
    else:
        target_num = extract_number(str(target))

    if target_num is not None:
        spoken_num = extract_number(raw_spoken)
        if spoken_num is not None and spoken_num == target_num:
            return True

    # Check numeric equality across all accepted items
    if accepted:
        spoken_num = extract_number(raw_spoken)
        if spoken_num is not None:
            for acc in accepted:
                acc_num = acc if isinstance(acc, int) else extract_number(str(acc))
                if acc_num is not None and acc_num == spoken_num:
                    return True

    # 2. Text comparison
    spoken_tokens = set(norm_spoken.split())
    clean_tokens = set(clean_spoken.split())

    for t in targets:
        norm_t = normalize_text(t)
        clean_t = clean_spoken_response(t)

        if not norm_t:
            continue

        # Direct match on normalized or cleaned
        if norm_spoken == norm_t or clean_spoken == norm_t or clean_spoken == clean_t:
            return True

        # Single word target present in tokens (e.g. target "cat" in "i see a cat")
        if len(norm_t.split()) == 1:
            if norm_t in spoken_tokens or norm_t in clean_tokens:
                return True
        else:
            # Multi-word target appears as a contiguous phrase
            if f" {norm_t} " in f" {norm_spoken} ":
                return True

    return False


def match_choice(spoken: Optional[str], choices: List[str]) -> Optional[str]:
    """Finds which choice in choices best matches the spoken text, if any."""
    if not spoken or not choices:
        return None

    clean_spoken = clean_spoken_response(spoken)
    norm_spoken = normalize_text(spoken)
    spoken_tokens = set(norm_spoken.split())

    # 1. Check exact match
    for choice in choices:
        norm_c = normalize_text(choice)
        if clean_spoken == norm_c or norm_spoken == norm_c:
            return choice

    # 2. Check contiguous phrase match
    for choice in choices:
        norm_c = normalize_text(choice)
        if len(norm_c.split()) == 1:
            if norm_c in spoken_tokens:
                return choice
        elif f" {norm_c} " in f" {norm_spoken} " or norm_c in norm_spoken:
            return choice

    # 3. Check number-based selection (e.g., choice "1", "first", "two")
    spoken_num = extract_number(spoken)
    if spoken_num is not None and 1 <= spoken_num <= len(choices):
        return choices[spoken_num - 1]

    # 4. Check distinctive keyword token overlap
    stopwords = {"the", "a", "an", "and", "or", "to", "for", "with", "story", "tale", "read", "want", "i", "please"}
    best_choice = None
    max_overlap = 0

    for choice in choices:
        norm_c = normalize_text(choice)
        choice_words = set(norm_c.split()) - stopwords
        overlap = len(choice_words.intersection(spoken_tokens))
        if overlap > max_overlap:
            max_overlap = overlap
            best_choice = choice

    if max_overlap > 0:
        return best_choice

    return None


def match_command(spoken: Optional[str], command_map: Dict[str, List[str]]) -> Optional[str]:
    """
    Matches spoken text against a dictionary of intent -> list of trigger keywords/phrases.
    Returns the intent name if matched.
    """
    if not spoken or not command_map:
        return None

    norm = normalize_text(spoken)
    tokens = set(norm.split())

    for cmd, triggers in command_map.items():
        for trigger in triggers:
            norm_trig = normalize_text(trigger)
            if not norm_trig:
                continue

            # Multi-word trigger
            if len(norm_trig.split()) > 1:
                if f" {norm_trig} " in f" {norm} " or norm == norm_trig:
                    return cmd
            else:
                # Single word trigger
                if norm_trig in tokens:
                    return cmd

    return None
