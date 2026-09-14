"""
Lumi - Master Entry Point & Voice Command Loop
100% Offline Learning Companion.
Launches the full interactive Tkinter GUI by default, or runs in Voice-First CLI mode with --cli.
"""

import sys
import argparse
from typing import Optional, Callable

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from Python.tts import speak
from Python.speech import listen
from Python.serial_comm import init_serial, is_connected as is_esp32_connected
from Python.database import create_tables, get_summary_stats, get_progress
from Python.answer_matcher import match_command

# Learning modules
from Python.Learning.alphabets import alphabet_lesson
from Python.Learning.animals import animal_lesson
from Python.Learning.colors import color_lesson
from Python.Learning.numbers import number_lesson
from Python.Learning.math import math_lesson
from Python.Learning.quiz import run_quiz
from Python.Learning.story import story_lesson


COMMAND_MAP = {
    "alphabet": [
        "alphabet", "alphabets", "abc", "abcs", "letters", "letter",
        "learn alphabet", "start alphabet", "letters lesson"
    ],
    "numbers": [
        "number", "numbers", "counting", "count", "learn numbers",
        "learn counting", "math numbers"
    ],
    "colors": [
        "color", "colors", "colour", "colours", "rainbow",
        "learn colors", "paint", "show colors"
    ],
    "animals": [
        "animal", "animals", "creatures", "pets", "zoo",
        "learn animals", "wild animals", "farm animals"
    ],
    "math": [
        "math", "mathematics", "addition", "subtraction",
        "maths", "plus", "minus", "arithmetic", "do math"
    ],
    "quiz": [
        "quiz", "test", "trivia", "game", "challenge",
        "exam", "ask questions", "play quiz"
    ],
    "story": [
        "story", "stories", "bedtime story", "tale", "read a story",
        "tell a story", "tell me a story", "story time", "book"
    ],
    "progress": [
        "progress", "score", "scores", "performance", "how am i doing",
        "report", "stats", "statistics", "achievements", "history"
    ],
    "help": [
        "help", "what can you do", "commands", "options", "menu", "instructions"
    ],
    "exit": [
        "exit", "quit", "stop", "bye", "goodbye", "close", "shut down", "see you"
    ]
}


def understand_command(spoken_text: Optional[str]) -> str:
    """
    Parses child speech and maps to normalized command intent.
    Returns: 'alphabet' | 'numbers' | 'colors' | 'animals' | 'math' | 'quiz' | 'story' | 'progress' | 'help' | 'exit' | 'unknown'
    """
    if not spoken_text:
        return "unknown"

    matched = match_command(spoken_text, COMMAND_MAP)
    return matched if matched else "unknown"


def show_progress_summary(audio: bool = True):
    """Fetches and announces learning progress."""
    stats = get_summary_stats()
    total_lessons = stats["total_lessons"]
    total_score = stats["total_score"]
    total_q = stats["total_questions"]
    pct = stats["overall_percentage"]

    print("\n" + "=" * 40)
    print("📊 LUMI LEARNING PROGRESS")
    print(f"• Total Lessons: {total_lessons}")
    print(f"• Total Score: {total_score} / {total_q} ({pct}%)")
    if stats["latest_quiz_score"] is not None:
        print(f"• Latest Quiz: {stats['latest_quiz_score']}/{stats['latest_quiz_total']} ({stats['latest_quiz_pct']}%)")
    print("=" * 40 + "\n")

    if audio:
        if total_lessons == 0:
            speak("You haven't completed any lessons yet. Start a lesson to earn your golden stars!")
        else:
            speak(f"You have completed {total_lessons} lessons with an overall score of {total_score} out of {total_q}, which is {pct} percent!")


def run_cli_loop():
    """Master offline voice-driven loop for terminal execution."""
    print("\n" + "🌟" * 20)
    print(" LUMI - OFFLINE LEARNING COMPANION ")
    print(" 100% Offline | Voice-First AI ")
    print("🌟" * 20 + "\n")

    # Initialize SQLite database
    create_tables()

    # Try connecting to ESP32
    esp_connected = init_serial()
    if esp_connected:
        print("🟢 ESP32 Hardware Companion connected.")
    else:
        print("⚪ ESP32 Hardware not detected (Operating in standalone software mode).")

    speak("Hello! I am Lumi, your friendly learning buddy.")

    while True:
        speak(
            "What would you like to learn? "
            "You can say alphabet, numbers, colors, animals, math, quiz, story, or progress.",
            rate=140
        )

        user_input = listen()

        if not user_input:
            speak("I didn't hear anything. Please try again or say help.")
            continue

        cmd = understand_command(user_input)

        if cmd == "alphabet":
            speak("Starting Alphabet lesson! Let's learn our A B Cs!")
            alphabet_lesson()

        elif cmd == "numbers":
            speak("Starting Numbers lesson! Let's count together!")
            number_lesson()

        elif cmd == "colors":
            speak("Starting Colors lesson! Let's discover beautiful colors!")
            color_lesson()

        elif cmd == "animals":
            speak("Starting Animals lesson! Let's meet some wonderful animals!")
            animal_lesson()

        elif cmd == "math":
            speak("Starting Math lesson! Let's solve fun math questions!")
            math_lesson()

        elif cmd == "quiz":
            speak("Starting Quiz time! Get ready for a challenge!")
            run_quiz()

        elif cmd == "story":
            speak("Starting Story time! Settle in for a wonderful story!")
            story_lesson()

        elif cmd == "progress":
            show_progress_summary(audio=True)

        elif cmd == "help":
            speak(
                "You can say: alphabet, numbers, colors, animals, math, "
                "quiz, story, progress, or exit. What would you like to do?"
            )

        elif cmd == "exit":
            speak("Goodbye! You did wonderful learning today! See you next time! 🌟")
            break

        else:
            speak(
                "I didn't quite understand that. "
                "You can say alphabet, numbers, colors, animals, math, quiz, or story."
            )


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Lumi - Offline Learning Companion")
    parser.add_argument("--cli", action="store_true", help="Run in terminal voice-loop mode without Tkinter GUI")
    parser.add_argument("--gui", action="store_true", help="Run with full Tkinter GUI (Default)")
    args = parser.parse_args()

    # Initialize database
    create_tables()

    if args.cli:
        run_cli_loop()
    else:
        try:
            from Python.gui import launch_gui
            launch_gui()
        except Exception as e:
            print(f"⚠️ GUI could not start ({e}). Falling back to voice CLI mode...")
            run_cli_loop()


if __name__ == "__main__":
    main()
