"""
Lumi - Math Practice Module
100% Offline fun math questions for children.
Integrates arithmetic problems, voice recognition, answer normalization, and database logging.
"""

import random
from typing import Optional, Callable, List, Tuple
from Python.tts import speak
from Python.speech import listen
from Python.database import save_progress
from Python.answer_matcher import match_answer
from Python.serial_comm import send_signal


MATH_QUESTIONS: List[Tuple[str, int, str]] = [
    ("What is two plus three?", 5, "2 + 3 = ?"),
    ("What is seven minus four?", 3, "7 - 4 = ?"),
    ("What is three times two?", 6, "3 × 2 = ?"),
    ("What is five plus five?", 10, "5 + 5 = ?"),
    ("What is ten minus six?", 4, "10 - 6 = ?"),
    ("What is four plus four?", 8, "4 + 4 = ?"),
    ("What is nine minus two?", 7, "9 - 2 = ?"),
    ("What is one plus six?", 7, "1 + 6 = ?"),
]


def math_lesson(
    ui_callback: Optional[Callable[[str, str, str, str, str], None]] = None,
    status_callback: Optional[Callable[[str], None]] = None,
    stop_check: Optional[Callable[[], bool]] = None,
    question_count: int = 5,
    interactive_voice: bool = True
) -> int:
    """Runs the Math Practice session."""
    speak("Let's practice some fun math together!")

    questions = list(MATH_QUESTIONS)
    random.shuffle(questions)
    active_questions = questions[:question_count]

    score = 0
    total = len(active_questions)

    for q_text, ans_num, formula in active_questions:
        if stop_check and stop_check():
            print("🛑 Lesson stopped by user.")
            break

        # Update GUI
        if ui_callback:
            try:
                ui_callback("numbers", str(ans_num), formula, q_text, "➕")
            except Exception:
                pass

        speak(q_text, rate=135)

        if interactive_voice:
            answer = listen(status_callback=status_callback)

            if not answer and (not stop_check or not stop_check()):
                speak(f"Take your time! {q_text}")
                answer = listen(status_callback=status_callback)

            if stop_check and stop_check():
                break

            accepted = [ans_num, str(ans_num)]
            if answer and match_answer(answer, ans_num, accepted=accepted):
                send_signal("C")
                speak(f"Correct! Great job! {formula.replace('?', str(ans_num))}")
                score += 1
            else:
                send_signal("W")
                if answer:
                    speak(f"Good try! The answer is {ans_num}.")
                else:
                    speak(f"The answer is {ans_num}.")

    # Summary
    if total > 0:
        speak(f"You finished math practice! You got {score} out of {total} correct!")
        if score == total:
            speak("Amazing! Perfect score! You are a math star! ⭐")
        elif score >= 3:
            speak("Great work! Keep practicing! 🌟")
        else:
            speak("Good effort! You get better every time! 💡")

        save_progress(
            lesson="Math",
            score=score,
            total_questions=total,
            category="Math",
            correct_answers=score,
            incorrect_answers=total - score
        )

    return score


if __name__ == "__main__":
    math_lesson()
