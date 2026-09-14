"""
Unit tests for all Learning Modules with mocked TTS for fast execution.
"""
import unittest.mock as mock
from Python.database import get_summary_stats

def test_modules_fast():
    print("Testing learning modules with fast execution...")

    # Mock speak so it doesn't take 2 minutes of real audio speech
    with mock.patch("Python.tts.speak") as mock_speak:
        from Python.Learning.alphabets import alphabet_lesson
        from Python.Learning.animals import animal_lesson
        from Python.Learning.colors import color_lesson
        from Python.Learning.numbers import number_lesson
        from Python.Learning.math import math_lesson
        from Python.Learning.quiz import run_quiz
        from Python.Learning.story import story_lesson

        displayed = []
        def mock_ui(cat, name, title, sub, emoji):
            displayed.append((cat, name, title))

        # Test alphabet (non-interactive)
        s_alpha = alphabet_lesson(ui_callback=mock_ui, interactive_voice=False)
        print(f"Alphabet lesson ran: {len(displayed)} UI calls")

        # Test animals
        s_anim = animal_lesson(ui_callback=mock_ui, interactive_voice=False)
        print("Animals lesson ran")

        # Test colors
        s_col = color_lesson(ui_callback=mock_ui, interactive_voice=False)
        print("Colors lesson ran")

        # Test numbers
        s_num = number_lesson(ui_callback=mock_ui, interactive_voice=False)
        print("Numbers lesson ran")

        # Test math
        s_math = math_lesson(ui_callback=mock_ui, interactive_voice=False, question_count=2)
        print("Math lesson ran")

        # Test quiz
        s_quiz = run_quiz(ui_callback=mock_ui, interactive_voice=False, max_questions=2)
        print("Quiz ran")

        # Test story
        s_story = story_lesson(story_title="The Little Seed", ui_callback=mock_ui, interactive_voice=False)
        print("Story ran")

    stats = get_summary_stats()
    print("Summary stats after test runs:", stats)
    assert stats["total_lessons"] > 0
    print("All Learning Modules passed tests successfully!")

if __name__ == "__main__":
    test_modules_fast()
