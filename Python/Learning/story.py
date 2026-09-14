"""
Lumi - Offline Storytelling Module
Reads heartwarming children's bedtime and educational stories from Dataset/stories.txt.
100% Offline with sentence-by-sentence gentle voice pacing, GUI illustrations, and activity logging.
"""

import time
import random
from typing import Optional, Callable, List, Dict, Any

from Python.tts import speak
from Python.speech import listen
from Python.database import save_progress, log_activity
from Python.data_loader import load_stories
from Python.answer_matcher import match_choice, normalize_text


def story_lesson(
    story_title: Optional[str] = None,
    ui_callback: Optional[Callable[[str, str, str, str, str], None]] = None,
    status_callback: Optional[Callable[[str], None]] = None,
    stop_check: Optional[Callable[[], bool]] = None,
    interactive_voice: bool = True
) -> bool:
    """
    Runs the offline storytelling session.
    Loads stories from Dataset/stories.txt and narrates warmly.
    """
    stories = load_stories()
    if not stories:
        speak("I could not find any stories right now.")
        return False

    selected_story: Optional[Dict[str, Any]] = None

    if story_title:
        # Match requested title
        for s in stories:
            if normalize_text(story_title) in normalize_text(s["title"]):
                selected_story = s
                break

    # If no specific story chosen, offer choices or pick
    if not selected_story:
        if interactive_voice:
            story_names = [s["title"] for s in stories]
            speak("I have wonderful stories! Which story would you like to hear?")
            for i, name in enumerate(story_names, start=1):
                speak(f"Story {i}: {name}.", rate=140)

            user_choice = listen(status_callback=status_callback)
            if user_choice:
                chosen_title = match_choice(user_choice, story_names)
                if chosen_title:
                    for s in stories:
                        if s["title"] == chosen_title:
                            selected_story = s
                            break

    # Default to first or random if not selected
    if not selected_story:
        selected_story = stories[0]

    title = selected_story["title"]
    lines = selected_story.get("lines", [selected_story.get("content", "")])

    speak(f"Now playing: {title}. Settle in and listen closely.", rate=130)

    # Initial UI card
    if ui_callback:
        try:
            ui_callback("ui", "lumi_logo", title, "Story Time with Lumi 📖", "✨")
        except Exception:
            pass

    # Read story lines
    for idx, line in enumerate(lines, start=1):
        if stop_check and stop_check():
            print("🛑 Story reading stopped by user.")
            break

        if ui_callback:
            try:
                ui_callback("ui", "lumi_logo", title, line, "📖")
            except Exception:
                pass

        # Speak each line with gentle, expressive pacing
        speak(line, rate=125)
        time.sleep(0.4)

    # Final wrap-up
    speak("I hope you loved this story! You did great listening today.", rate=135)

    if ui_callback:
        try:
            ui_callback("ui", "lumi_logo", f"{title} - The End", "Great listening! 🌟", "💖")
        except Exception:
            pass

    # Log in database
    log_activity("story", f"Listened to story: {title}")
    save_progress(
        lesson="Story",
        score=len(lines),
        total_questions=len(lines),
        category="Story",
        correct_answers=len(lines),
        incorrect_answers=0
    )

    return True


if __name__ == "__main__":
    story_lesson()
