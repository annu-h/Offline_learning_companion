"""
Lumi - Alphabet Learning Module
100% Offline alphabet lesson loaded dynamically from Dataset/alphabets.csv.
Integrates voice recognition, answer normalization, image display, and database tracking.
"""

from typing import Optional, Callable
from Python.tts import speak
from Python.speech import listen
from Python.database import save_progress
from Python.data_loader import load_alphabets
from Python.answer_matcher import match_answer
from Python.serial_comm import send_signal


def alphabet_lesson(
    ui_callback: Optional[Callable[[str, str, str, str, str], None]] = None,
    status_callback: Optional[Callable[[str], None]] = None,
    stop_check: Optional[Callable[[], bool]] = None,
    interactive_voice: bool = True
) -> int:
    """
    Runs the Alphabet lesson.
    ui_callback: fn(category, name, title, subtitle, emoji)
    status_callback: fn(status_text)
    stop_check: fn() -> bool (returns True if user requested stop/exit)
    """
    letters = load_alphabets()
    if not letters:
        speak("Alphabet dataset could not be loaded.")
        return 0

    speak("Let's learn the alphabet together!")
    score = 0
    total = len(letters)

    for item in letters:
        if stop_check and stop_check():
            print("🛑 Lesson stopped by user.")
            break

        letter = item["letter"]
        word = item["word"]
        emoji = item.get("emoji", "🌟")

        # Update GUI if attached
        if ui_callback:
            try:
                ui_callback("alphabet", letter, letter, f"{letter} is for {word}", emoji)
            except Exception:
                pass

        # Speak letter presentation
        speak(f"{letter} is for {word}.", rate=135)

        if interactive_voice:
            speak(f"What letter is for {word}?", rate=140)

            # Listen with status
            answer = listen(status_callback=status_callback)

            if not answer and (not stop_check or not stop_check()):
                speak("That's okay. Take your time.")
                answer = listen(status_callback=status_callback)

            if stop_check and stop_check():
                break

            # Normalize and evaluate answer
            accepted_answers = [letter, letter.lower(), word, f"{letter} for {word}"]
            if answer and match_answer(answer, letter, accepted=accepted_answers):
                send_signal("C")
                speak(f"Correct! Great job! {letter} is for {word}!")
                score += 1
            else:
                send_signal("W")
                if answer:
                    speak(f"Good try! The answer is {letter}, for {word}.")
                else:
                    speak(f"The answer is {letter}, for {word}.")

    # Summary
    if total > 0:
        speak(f"Wonderful job! You got {score} out of {total} letters!")
        save_progress(
            lesson="Alphabet",
            score=score,
            total_questions=total,
            category="Alphabet",
            correct_answers=score,
            incorrect_answers=total - score
        )

    return score


if __name__ == "__main__":
    alphabet_lesson()
