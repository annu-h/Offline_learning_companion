"""
Lumi - Comprehensive Quiz Module
100% Offline quiz loaded dynamically from Dataset/quiz.csv.
Supports general and category-specific quizzes with voice input and database logging.
"""

import random
from typing import Optional, Callable
from Python.tts import speak
from Python.speech import listen
from Python.database import save_quiz_attempt
from Python.data_loader import load_quiz
from Python.answer_matcher import match_answer
from Python.serial_comm import send_signal


def run_quiz(
    category: Optional[str] = None,
    ui_callback: Optional[Callable[[str, str, str, str, str], None]] = None,
    status_callback: Optional[Callable[[str], None]] = None,
    stop_check: Optional[Callable[[], bool]] = None,
    max_questions: Optional[int] = None,
    interactive_voice: bool = True
) -> int:
    """
    Runs an interactive voice-driven Quiz session.
    category: Optional category filter ('Alphabet', 'Numbers', 'Colors', 'Animals', 'Math', or None for all)
    """
    questions = load_quiz(category=category)
    if not questions:
        speak("Quiz questions could not be loaded.")
        return 0

    random.shuffle(questions)
    if max_questions and max_questions < len(questions):
        questions = questions[:max_questions]

    cat_label = category if category else "General"
    speak(f"Let's start the {cat_label} Quiz! Are you ready?")

    # Initial quiz banner in UI
    if ui_callback:
        try:
            ui_callback("quiz", "quiz_star", "Quiz Time! 🌟", f"{cat_label} Challenge", "⭐")
        except Exception:
            pass

    score = 0
    total = len(questions)

    for idx, item in enumerate(questions, start=1):
        if stop_check and stop_check():
            print("🛑 Quiz stopped by user.")
            break

        q_text = item["question"]
        ans_target = item["answer"]
        accepted = item.get("accepted", [ans_target])
        q_cat = item.get("category", "Quiz")

        # Update GUI with current question
        if ui_callback:
            try:
                ui_callback("quiz", "quiz_star", f"Question {idx} of {total}", q_text, "❓")
            except Exception:
                pass

        speak(f"Question {idx}: {q_text}", rate=135)

        if interactive_voice:
            answer = listen(status_callback=status_callback)

            if not answer and (not stop_check or not stop_check()):
                speak(f"Take your time! {q_text}")
                answer = listen(status_callback=status_callback)

            if stop_check and stop_check():
                break

            is_correct = bool(answer and match_answer(answer, ans_target, accepted=accepted))

            if is_correct:
                send_signal("C")
                if ui_callback:
                    try:
                        ui_callback("quiz", "correct", "Correct! 🎉", f"Great job! The answer is {ans_target}", "✅")
                    except Exception:
                        pass
                speak(f"Correct! Super job! The answer is {ans_target}!")
                score += 1
            else:
                send_signal("W")
                if ui_callback:
                    try:
                        ui_callback("quiz", "try_again", "Good Try! 🌟", f"The answer is {ans_target}", "💡")
                    except Exception:
                        pass
                if answer:
                    speak(f"Good try! The correct answer is {ans_target}.")
                else:
                    speak(f"The correct answer is {ans_target}.")

    # Summary
    if total > 0:
        pct = int((score / total) * 100)
        speak(f"You finished the quiz! You got {score} out of {total} questions correct, which is {pct} percent!")

        if ui_callback:
            try:
                ui_callback("quiz", "trophy", f"Quiz Complete! 🏆", f"Final Score: {score}/{total} ({pct}%)", "🎉")
            except Exception:
                pass

        if score == total:
            speak("Incredible! You got every single question right! You earn a golden star! 🌟")
        elif pct >= 70:
            speak("Awesome work! You are doing so well! 🚀")
        else:
            speak("Great effort! Keep playing and learning with Lumi! 💖")

        # Save to database
        save_quiz_attempt(
            score=score,
            total_questions=total,
            category=cat_label
        )

    return score


if __name__ == "__main__":
    run_quiz()
