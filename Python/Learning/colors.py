"""
Lumi - Colors Learning Module
100% Offline color lesson loaded dynamically from Dataset/colors.csv.
Integrates image display, color palettes, voice recognition, and database tracking.
"""

from typing import Optional, Callable
from Python.tts import speak
from Python.speech import listen
from Python.database import save_progress
from Python.data_loader import load_colors
from Python.answer_matcher import match_answer
from Python.serial_comm import send_signal


def color_lesson(
    ui_callback: Optional[Callable[[str, str, str, str, str], None]] = None,
    status_callback: Optional[Callable[[str], None]] = None,
    stop_check: Optional[Callable[[], bool]] = None,
    interactive_voice: bool = True
) -> int:
    """Runs the Colors lesson."""
    colors = load_colors()
    if not colors:
        speak("Color dataset could not be loaded.")
        return 0

    speak("Let's explore beautiful colors all around us!")
    score = 0
    total = len(colors)

    for item in colors:
        if stop_check and stop_check():
            print("🛑 Lesson stopped by user.")
            break

        color = item["color"]
        example = item.get("example", "")
        emoji = item.get("emoji", "🎨")

        # Update GUI
        if ui_callback:
            try:
                subtitle = f"Like a {example}!" if example else f"Color {color}"
                ui_callback("colors", color, color.capitalize(), subtitle, emoji)
            except Exception:
                pass

        # Speak presentation
        if example:
            speak(f"This is {color}. Think of a {color} {example}!", rate=135)
        else:
            speak(f"This is {color}.", rate=135)

        if interactive_voice:
            if example:
                speak(f"What color is a {example}?", rate=140)
            else:
                speak(f"What color is this?", rate=140)

            answer = listen(status_callback=status_callback)

            if not answer and (not stop_check or not stop_check()):
                speak(f"Take your time! What color is the {example}?")
                answer = listen(status_callback=status_callback)

            if stop_check and stop_check():
                break

            accepted_answers = [color, f"it is {color}", f"the color is {color}", f"{color} color"]
            if answer and match_answer(answer, color, accepted=accepted_answers):
                send_signal("C")
                speak(f"Correct! Great job! It is {color}!")
                score += 1
            else:
                send_signal("W")
                if answer:
                    speak(f"Good try! The color is {color}.")
                else:
                    speak(f"The color is {color}.")

    # Summary
    if total > 0:
        speak(f"You got {score} out of {total} colors correct! Fantastic!")
        save_progress(
            lesson="Colors",
            score=score,
            total_questions=total,
            category="Colors",
            correct_answers=score,
            incorrect_answers=total - score
        )

    return score


if __name__ == "__main__":
    color_lesson()
