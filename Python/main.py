"""
Lumi - Master Entry Point & Voice Command Loop
100% Offline Learning Companion.
Launches the full interactive Tkinter GUI by default, or runs in Voice-First CLI mode with --cli.
"""

import sys
import argparse
from typing import Optional, Callable
from datetime import datetime

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

def handle_general_conversation(user_input: str) -> bool:
    """
    Handles simple conversational questions.
    Returns True if the input was handled here.
    Returns False if it should be passed to the normal command system.
    """

    text = user_input.lower().strip()

    # Current time
    if (
        "what time" in text
        or "current time" in text
        or "time is it" in text
        or "tell me the time" in text
    ):
        current_time = datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}.")
        return True

    # Current date
    if (
        "what date" in text
        or "today's date" in text
        or "todays date" in text
        or "what day is today" in text
        or "what is today's day" in text
    ):
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        speak(f"Today is {current_date}.")
        return True

    # Greetings
    if (
        text == "hi"
        or text == "hello"
        or text == "hey"
        or "hello lumi" in text
        or "hi lumi" in text
    ):
        speak("Hello! It is nice to talk to you. What would you like to do?")
        return True

    # Thanks
    if "thank you" in text or "thanks" in text:
        speak("You're welcome! I am happy to help you.")
        return True

    return False

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

    # --------------------------------------------------
    # LUMI INTRODUCTION
    # --------------------------------------------------

    speak(
        "Hello! I am Lumi, your friendly learning companion. "
        "I am here to guide you. "
        "You can ask me questions or choose a learning activity. "
        "What would you like to do?"
    )

    # --------------------------------------------------
    # INTERACTIVE CONVERSATION LOOP
    # --------------------------------------------------

    while True:

        # Listen to the child
        user_input = listen()

        # Nothing heard
        if not user_input:
            speak("I didn't hear anything. Please try again.")
            continue

        print(f"\n👦 User: {user_input}")

        # --------------------------------------------------
        # Handle normal conversation
        # --------------------------------------------------

        if handle_general_conversation(user_input):
            continue

        # --------------------------------------------------
        # Understand learning command
        # --------------------------------------------------

        cmd = understand_command(user_input)

        # --------------------------------------------------
        # ALPHABET
        # --------------------------------------------------

        if cmd == "alphabet":
            speak(
                "Great! Let's learn the alphabet together. "
                "Starting our alphabet lesson!"
            )
            alphabet_lesson()

        # --------------------------------------------------
        # NUMBERS
        # --------------------------------------------------

        elif cmd == "numbers":
            speak(
                "Wonderful! Let's count together. "
                "Starting our numbers lesson!"
            )
            number_lesson()

        # --------------------------------------------------
        # COLORS
        # --------------------------------------------------

        elif cmd == "colors":
            speak(
                "Great choice! Let's discover some beautiful colors!"
            )
            color_lesson()

        # --------------------------------------------------
        # ANIMALS
        # --------------------------------------------------

        elif cmd == "animals":
            speak(
                "I love animals! Let's learn about some wonderful animals!"
            )
            animal_lesson()

        # --------------------------------------------------
        # MATH
        # --------------------------------------------------

        elif cmd == "math":
            speak(
                "Let's have some fun with numbers! "
                "Starting our math lesson!"
            )
            math_lesson()

        # --------------------------------------------------
        # QUIZ
        # --------------------------------------------------

        elif cmd == "quiz":
            speak(
                "Quiz time! Let's see what you know!"
            )
            run_quiz()

        # --------------------------------------------------
        # STORY
        # --------------------------------------------------

        elif cmd == "story":
            speak(
                "Story time! Get comfortable and let's begin our story."
            )
            story_lesson()

        # --------------------------------------------------
        # PROGRESS
        # --------------------------------------------------

        elif cmd == "progress":
            show_progress_summary(audio=True)

        # --------------------------------------------------
        # HELP
        # --------------------------------------------------

        elif cmd == "help":
            speak(
                "I can teach you alphabet, numbers, colors, animals, "
                "and math. We can also play a quiz, listen to a story, "
                "or check your learning progress. "
                "You can also ask me simple questions like "
                "what time it is or today's date."
            )

        # --------------------------------------------------
        # EXIT
        # --------------------------------------------------

        elif cmd == "exit" or cmd == "end":
            speak(
                "Goodbye! You did wonderful learning today. "
                "See you next time!"
            )
            break

        # --------------------------------------------------
        # UNKNOWN INPUT
        # --------------------------------------------------

        else:
            speak(
                "Hmm, I didn't understand that. "
                "You can ask me a question or say "
                "alphabet, numbers, colors, animals, math, "
                "quiz, story, progress, help, or exit."
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