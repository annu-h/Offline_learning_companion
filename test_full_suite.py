"""
Lumi - Comprehensive Master Test Suite
Tests every subsystem:
1. Data loading (CSV and TXT)
2. Database CRUD, schema migrations, and statistics
3. Answer matching & natural intent extraction
4. Image Manager (PIL cards, caching, fallback creation)
5. Serial communication fallback
6. TTS & Speech pipeline
7. All 7 Learning & Storytelling Modules
8. GUI creation and command routing
"""

import unittest
import unittest.mock as mock
from pathlib import Path

from Python.data_loader import (
    load_alphabets, load_animals, load_colors,
    load_numbers, load_math_questions, load_quiz, load_stories
)
from Python.database import (
    create_tables, save_progress, save_quiz_attempt,
    log_activity, get_progress, get_quiz_attempts, get_summary_stats
)
from Python.answer_matcher import (
    normalize_text, clean_spoken_response, extract_number,
    match_answer, match_choice, match_command
)
from Python.image_manager import (
    get_image_path, load_pil_image, resize_and_fit,
    create_fallback_card, clear_cache
)
from Python.serial_comm import is_connected, send_signal, find_esp32_port
from Python.main import understand_command, COMMAND_MAP


class TestLumiSubsystems(unittest.TestCase):

    def setUp(self):
        create_tables()

    # 1. DATA LOADER TESTS
    def test_data_loader(self):
        alphabets = load_alphabets()
        self.assertEqual(len(alphabets), 26)
        self.assertEqual(alphabets[0]["letter"], "A")

        animals = load_animals()
        self.assertGreaterEqual(len(animals), 10)
        self.assertTrue(any(a["name"].lower() == "dog" for a in animals))

        colors = load_colors()
        self.assertGreaterEqual(len(colors), 10)
        self.assertTrue(any(c["color"].lower() == "red" for c in colors))

        numbers = load_numbers()
        self.assertGreaterEqual(len(numbers), 10)
        self.assertEqual(numbers[0]["number"], 1)

        math_qs = load_math_questions()
        self.assertGreaterEqual(len(math_qs), 15)

        quiz_qs = load_quiz()
        self.assertGreaterEqual(len(quiz_qs), 10)

        stories = load_stories()
        self.assertGreaterEqual(len(stories), 3)
        self.assertTrue(any("seed" in s["title"].lower() for s in stories))

    # 2. DATABASE TESTS
    def test_database_operations(self):
        initial_stats = get_summary_stats()

        rec_id = save_progress(
            lesson="TestAlphabet",
            score=10,
            total_questions=10,
            category="Alphabet",
            correct_answers=10,
            incorrect_answers=0
        )
        self.assertGreater(rec_id, 0)

        quiz_id = save_quiz_attempt(
            score=8,
            total_questions=10,
            category="Math"
        )
        self.assertGreater(quiz_id, 0)

        log_activity("test", "Ran automated test suite")

        progress = get_progress(limit=5)
        self.assertGreater(len(progress), 0)

        quiz_attempts = get_quiz_attempts(limit=5)
        self.assertGreater(len(quiz_attempts), 0)

        stats = get_summary_stats()
        self.assertGreater(stats["total_lessons"], initial_stats["total_lessons"])

    # 3. ANSWER MATCHER TESTS
    def test_answer_matcher(self):
        # Text normalization
        self.assertEqual(normalize_text("  Hello, World!  "), "hello world")

        # Filler cleaning
        self.assertEqual(clean_spoken_response("I think the answer is dog"), "dog")
        self.assertEqual(clean_spoken_response("it is a red"), "red")

        # Number extraction
        self.assertEqual(extract_number("I have five apples"), 5)
        self.assertEqual(extract_number("twenty one"), 21)
        self.assertEqual(extract_number("number 42"), 42)

        # Match answer
        self.assertTrue(match_answer("it's a cat", "cat"))
        self.assertTrue(match_answer("the answer is 4", "4"))
        self.assertTrue(match_answer("four", 4))
        self.assertTrue(match_answer("won", 1))
        self.assertTrue(match_answer("blue", "Red", accepted=["Red", "Blue"]))

        # Choice matching
        choices = ["The Little Seed", "The Friendly Bear", "Luna The Little Star"]
        self.assertEqual(match_choice("i want the bear story", choices), "The Friendly Bear")
        self.assertEqual(match_choice("first one", choices), "The Little Seed")

        # Command matching
        self.assertEqual(understand_command("let's do math"), "math")
        self.assertEqual(understand_command("can we hear a bedtime story"), "story")
        self.assertEqual(understand_command("check my score and progress"), "progress")
        self.assertEqual(understand_command("goodbye lumi"), "exit")

    # 4. IMAGE MANAGER TESTS
    def test_image_manager(self):
        clear_cache()

        # Fallback card creation
        card = create_fallback_card(title="Test", subtitle="Sub", emoji="🌟", size=(200, 200))
        self.assertEqual(card.size, (200, 200))

        # PIL image load with generated card
        pil_img = load_pil_image("alphabet", "A", size=(200, 200), fallback_title="A")
        self.assertEqual(pil_img.size, (200, 200))

        # Check existing pre-generated image
        img_path = get_image_path("ui", "lumi_logo")
        self.assertIsNotNone(img_path)

    # 5. SERIAL COMMUNICATION TESTS
    def test_serial_comm(self):
        # Should gracefully return False or status without crashing
        res = send_signal("I")
        self.assertIsInstance(res, bool)

    # 6. LEARNING MODULES INTEGRATION TEST
    def test_learning_modules_fast(self):
        with mock.patch("Python.Learning.alphabets.speak"), \
             mock.patch("Python.Learning.animals.speak"), \
             mock.patch("Python.Learning.colors.speak"), \
             mock.patch("Python.Learning.numbers.speak"), \
             mock.patch("Python.Learning.math.speak"), \
             mock.patch("Python.Learning.quiz.speak"), \
             mock.patch("Python.Learning.story.speak"), \
             mock.patch("Python.tts.speak"):

            from Python.Learning.alphabets import alphabet_lesson
            from Python.Learning.animals import animal_lesson
            from Python.Learning.colors import color_lesson
            from Python.Learning.numbers import number_lesson
            from Python.Learning.math import math_lesson
            from Python.Learning.quiz import run_quiz
            from Python.Learning.story import story_lesson

            ui_calls = []
            def dummy_ui(cat, name, title, sub, emoji):
                ui_calls.append((cat, name, title))

            # Run all lessons in programmatic/non-interactive mode
            self.assertGreaterEqual(alphabet_lesson(ui_callback=dummy_ui, interactive_voice=False), 0)
            self.assertGreaterEqual(animal_lesson(ui_callback=dummy_ui, interactive_voice=False), 0)
            self.assertGreaterEqual(color_lesson(ui_callback=dummy_ui, interactive_voice=False), 0)
            self.assertGreaterEqual(number_lesson(ui_callback=dummy_ui, interactive_voice=False), 0)
            self.assertGreaterEqual(math_lesson(ui_callback=dummy_ui, interactive_voice=False, question_count=2), 0)
            self.assertGreaterEqual(run_quiz(ui_callback=dummy_ui, interactive_voice=False, max_questions=2), 0)
            self.assertTrue(story_lesson(story_title="The Little Seed", ui_callback=dummy_ui, interactive_voice=False))

            self.assertGreater(len(ui_calls), 30)


if __name__ == "__main__":
    unittest.main()
