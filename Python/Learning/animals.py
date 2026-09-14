"""
Lumi - Animal Learning Module
100% Offline animal lesson loaded dynamically from Dataset/animals.csv.
Integrates sound emulation, image display, voice recognition, and database tracking.
"""

from typing import Optional, Callable
from Python.tts import speak
from Python.speech import listen
from Python.database import save_progress
from Python.data_loader import load_animals
from Python.answer_matcher import match_answer
from Python.serial_comm import send_signal


def animal_lesson(
    ui_callback: Optional[Callable[[str, str, str, str, str], None]] = None,
    status_callback: Optional[Callable[[str], None]] = None,
    stop_check: Optional[Callable[[], bool]] = None,
    interactive_voice: bool = True
) -> int:
    """Runs the Animal lesson."""
    animals = load_animals()
    if not animals:
        speak("Animal dataset could not be loaded.")
        return 0

    speak("Let's learn about amazing animals and their sounds!")
    score = 0
    total = len(animals)

    for item in animals:
        if stop_check and stop_check():
            print("🛑 Lesson stopped by user.")
            break

        animal = item["animal"]
        sound = item["sound"]
        emoji = item.get("emoji", "🐾")

        # Update GUI
        if ui_callback:
            try:
                ui_callback("animals", animal, animal.capitalize(), f"Makes a {sound} sound!", emoji)
            except Exception:
                pass

        # Speak presentation
        speak(f"This is a {animal}. A {animal} says {sound}!", rate=135)

        if interactive_voice:
            speak(f"What animal makes a {sound} sound?", rate=140)

            answer = listen(status_callback=status_callback)

            if not answer and (not stop_check or not stop_check()):
                speak("That's okay! What animal says " + sound + "?")
                answer = listen(status_callback=status_callback)

            if stop_check and stop_check():
                break

            accepted_answers = [animal, f"the {animal}", f"a {animal}"]
            if answer and match_answer(answer, animal, accepted=accepted_answers):
                send_signal("C")
                speak(f"Correct! Great job! A {animal} says {sound}!")
                score += 1
            else:
                send_signal("W")
                if answer:
                    speak(f"Good try! A {animal} makes a {sound} sound.")
                else:
                    speak(f"A {animal} makes a {sound} sound.")

    # Summary
    if total > 0:
        speak(f"You finished the animal lesson! You got {score} out of {total} animals correct!")
        save_progress(
            lesson="Animals",
            score=score,
            total_questions=total,
            category="Animals",
            correct_answers=score,
            incorrect_answers=total - score
        )

    return score


if __name__ == "__main__":
    animal_lesson()
