"""
Lumi - Numbers Learning Module
100% Offline number counting lesson loaded dynamically from Dataset/numbers.csv.
Integrates counting card visuals, voice recognition, and database tracking.
"""

from typing import Optional, Callable
from Python.tts import speak
from Python.speech import listen
from Python.database import save_progress
from Python.data_loader import load_numbers
from Python.answer_matcher import match_answer
from Python.serial_comm import send_signal


def number_lesson(
    ui_callback: Optional[Callable[[str, str, str, str, str], None]] = None,
    status_callback: Optional[Callable[[str], None]] = None,
    stop_check: Optional[Callable[[], bool]] = None,
    interactive_voice: bool = True
) -> int:
    """Runs the Numbers lesson."""
    numbers = load_numbers()
    if not numbers:
        speak("Numbers dataset could not be loaded.")
        return 0

    speak("Let's count together from one to ten!")
    score = 0
    total = len(numbers)

    for item in numbers:
        if stop_check and stop_check():
            print("🛑 Lesson stopped by user.")
            break

        num = item["number"]
        word = item["word"]
        emoji = item.get("emoji", "🔢")

        # Update GUI
        if ui_callback:
            try:
                ui_callback("numbers", str(num), str(num), f"Number {word.capitalize()} ({num})", emoji)
            except Exception:
                pass

        # Speak presentation
        speak(f"This is number {num}, spelled {word}.", rate=135)

        if interactive_voice:
            speak(f"What number is this?", rate=140)

            answer = listen(status_callback=status_callback)

            if not answer and (not stop_check or not stop_check()):
                speak(f"Take your time! Can you say number {word}?")
                answer = listen(status_callback=status_callback)

            if stop_check and stop_check():
                break

            accepted_answers = [num, str(num), word, f"number {num}", f"number {word}"]
            if answer and match_answer(answer, num, accepted=accepted_answers):
                send_signal("C")
                speak(f"Correct! Great job! That is number {word}!")
                score += 1
            else:
                send_signal("W")
                if answer:
                    speak(f"Good try! The answer is number {word}.")
                else:
                    speak(f"The answer is number {word}.")

    # Summary
    if total > 0:
        speak(f"Super counting! You got {score} out of {total} numbers correct!")
        save_progress(
            lesson="Numbers",
            score=score,
            total_questions=total,
            category="Numbers",
            correct_answers=score,
            incorrect_answers=total - score
        )

    return score


if __name__ == "__main__":
    number_lesson()
