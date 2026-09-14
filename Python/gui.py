"""
Lumi - Modern Child-Friendly GUI Module
Provides a polished, responsive, voice-first Tkinter interface with live visual cards,
real-time mic/speaker status badges, interactive lesson buttons, and statistics dashboard.
100% Offline.
"""

import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, Callable

from Python.tts import speak, speak_async
from Python.speech import listen
from Python.serial_comm import is_connected as is_esp32_connected, find_esp32_port
from Python.database import get_summary_stats, get_progress, get_quiz_attempts
from Python.image_manager import get_tk_image, load_pil_image
from Python.answer_matcher import match_command

# Learning modules
from Python.Learning.alphabets import alphabet_lesson
from Python.Learning.animals import animal_lesson
from Python.Learning.colors import color_lesson
from Python.Learning.numbers import number_lesson
from Python.Learning.math import math_lesson
from Python.Learning.quiz import run_quiz
from Python.Learning.story import story_lesson


# Color Palette (Child-Friendly & Modern)
BG_MAIN = "#F8FAFC"        # Slate 50
BG_CARD = "#FFFFFF"        # Pure White
PRIMARY = "#4F46E5"        # Indigo 600
PRIMARY_HOVER = "#4338CA"  # Indigo 700
PRIMARY_LIGHT = "#EEF2FF"  # Indigo 50
ACCENT_YELLOW = "#F59E0B"  # Amber 500
ACCENT_GREEN = "#10B981"   # Emerald 500
ACCENT_RED = "#EF4444"     # Red 500
ACCENT_BLUE = "#0284C7"    # Sky 600
TEXT_DARK = "#0F172A"      # Slate 900
TEXT_MUTED = "#64748B"     # Slate 500
BORDER_COLOR = "#E2E8F0"   # Slate 200


class LumiGUI:
    """Master Tkinter GUI for Lumi Offline Learning Companion."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Lumi 🌟 Offline Learning Companion")
        self.root.geometry("860x740")
        self.root.minsize(800, 680)
        self.root.configure(bg=BG_MAIN)

        # Execution and thread control
        self.active_thread: Optional[threading.Thread] = None
        self.is_running_lesson = False
        self.stop_requested = False
        self.voice_loop_active = False
        self.current_tk_image = None

        # Set app icon if available
        try:
            logo_img = load_pil_image("ui", "lumi_logo", size=(64, 64), fallback_title="Lumi", fallback_emoji="🌟")
            # Convert to photo image for icon
            from PIL import ImageTk
            self._icon_photo = ImageTk.PhotoImage(logo_img)
            self.root.iconphoto(False, self._icon_photo)
        except Exception:
            pass

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Initial welcome card
        self.update_card("ui", "lumi_logo", "Hello! I am Lumi 🌟", "Your friendly offline learning companion! Speak or click below.", "✨")
        self.set_status("Ready", "✨", ACCENT_GREEN)

        # Announce welcome on start
        self.root.after(500, self._welcome_greeting)

    def _build_ui(self):
        """Constructs all GUI widgets and layout."""
        # Top Header Bar
        header_frame = tk.Frame(self.root, bg=PRIMARY, height=75)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        header_content = tk.Frame(header_frame, bg=PRIMARY)
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        title_lbl = tk.Label(
            header_content,
            text="🌟 LUMI",
            font=("Segoe UI", 22, "bold"),
            fg="#FFFFFF",
            bg=PRIMARY
        )
        title_lbl.pack(side=tk.LEFT, padx=(0, 10))

        sub_title_lbl = tk.Label(
            header_content,
            text="Offline Learning Companion",
            font=("Segoe UI", 12, "italic"),
            fg="#C7D2FE",
            bg=PRIMARY
        )
        sub_title_lbl.pack(side=tk.LEFT, pady=4)

        # ESP32 Status Pill on top right
        self.esp32_lbl = tk.Label(
            header_content,
            text="⚪ ESP32: Offline",
            font=("Segoe UI", 10, "bold"),
            fg="#E0E7FF",
            bg=PRIMARY_HOVER,
            padx=12,
            pady=4,
            relief=tk.FLAT
        )
        self.esp32_lbl.pack(side=tk.RIGHT, padx=5)
        self._update_esp32_indicator()

        # Stats Button on header
        stats_btn = tk.Button(
            header_content,
            text="📊 My Progress",
            font=("Segoe UI", 10, "bold"),
            bg="#3730A3",
            fg="#FFFFFF",
            activebackground="#312E81",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.open_stats_modal
        )
        stats_btn.pack(side=tk.RIGHT, padx=5)

        # Main Central Card Container
        self.card_outer = tk.Frame(self.root, bg=BG_MAIN, padx=24, pady=12)
        self.card_outer.pack(fill=tk.BOTH, expand=True)

        self.card_inner = tk.Frame(
            self.card_outer,
            bg=BG_CARD,
            bd=1,
            relief=tk.SOLID,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            padx=20,
            pady=16
        )
        self.card_inner.pack(fill=tk.BOTH, expand=True)

        # Top of Card: Title & Subtitle
        self.card_title_lbl = tk.Label(
            self.card_inner,
            text="Welcome to Lumi!",
            font=("Segoe UI", 20, "bold"),
            fg=TEXT_DARK,
            bg=BG_CARD,
            wraplength=650
        )
        self.card_title_lbl.pack(pady=(4, 2))

        self.card_sub_lbl = tk.Label(
            self.card_inner,
            text="Your Voice-First Learning Companion",
            font=("Segoe UI", 13),
            fg=TEXT_MUTED,
            bg=BG_CARD,
            wraplength=650
        )
        self.card_sub_lbl.pack(pady=(0, 10))

        # Center of Card: Image Display
        self.image_container = tk.Frame(self.card_inner, bg=BG_CARD, width=260, height=260)
        self.image_container.pack(pady=5)
        self.image_container.pack_propagate(False)

        self.card_img_lbl = tk.Label(
            self.image_container,
            bg=BG_CARD,
            bd=0
        )
        self.card_img_lbl.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Live Transcript Preview Box
        self.transcript_frame = tk.Frame(self.card_inner, bg=PRIMARY_LIGHT, bd=0, padx=12, pady=6)
        self.transcript_frame.pack(fill=tk.X, pady=(10, 4), padx=20)

        self.transcript_lbl = tk.Label(
            self.transcript_frame,
            text="💬 Say something like: \"Let's learn animals\" or \"Tell me a story\"",
            font=("Segoe UI", 11, "italic"),
            fg=PRIMARY,
            bg=PRIMARY_LIGHT,
            wraplength=650
        )
        self.transcript_lbl.pack()

        # Status & Activity Bar
        status_bar = tk.Frame(self.root, bg=BG_MAIN, padx=24, pady=4)
        status_bar.pack(fill=tk.X)

        self.status_pill = tk.Label(
            status_bar,
            text="✨ Ready",
            font=("Segoe UI", 11, "bold"),
            fg="#FFFFFF",
            bg=ACCENT_GREEN,
            padx=16,
            pady=4
        )
        self.status_pill.pack(side=tk.LEFT)

        # Stop Button (prominent when running)
        self.stop_btn = tk.Button(
            status_bar,
            text="🛑 Stop Activity",
            font=("Segoe UI", 10, "bold"),
            bg="#FEE2E2",
            fg=ACCENT_RED,
            activebackground="#FCA5A5",
            activeforeground="#991B1B",
            relief=tk.FLAT,
            padx=12,
            pady=3,
            cursor="hand2",
            command=self.stop_current_activity
        )
        self.stop_btn.pack(side=tk.RIGHT, padx=5)

        # Voice Mode Toggle Button
        self.voice_btn = tk.Button(
            status_bar,
            text="🎙️ Voice Command",
            font=("Segoe UI", 10, "bold"),
            bg="#E0E7FF",
            fg=PRIMARY,
            activebackground="#C7D2FE",
            activeforeground="#3730A3",
            relief=tk.FLAT,
            padx=14,
            pady=3,
            cursor="hand2",
            command=self.trigger_voice_command
        )
        self.voice_btn.pack(side=tk.RIGHT, padx=5)

        # Bottom Button Grid (Learning Modules)
        btn_container = tk.Frame(self.root, bg=BG_MAIN, padx=20, pady=10)
        btn_container.pack(fill=tk.X, side=tk.BOTTOM)

        modules = [
            ("🔤 Alphabet", "#F59E0B", lambda: self.launch_module("alphabet")),
            ("🔢 Numbers", "#3B82F6", lambda: self.launch_module("numbers")),
            ("🎨 Colors", "#EC4899", lambda: self.launch_module("colors")),
            ("🐶 Animals", "#10B981", lambda: self.launch_module("animals")),
            ("➕ Math", "#8B5CF6", lambda: self.launch_module("math")),
            ("🧠 Quiz", "#F97316", lambda: self.launch_module("quiz")),
            ("📖 Story", "#06B6D4", lambda: self.launch_module("story")),
        ]

        for idx, (label, color, cmd) in enumerate(modules):
            btn = tk.Button(
                btn_container,
                text=label,
                font=("Segoe UI", 10, "bold"),
                bg="#FFFFFF",
                fg=TEXT_DARK,
                activebackground=color,
                activeforeground="#FFFFFF",
                bd=1,
                relief=tk.SOLID,
                highlightbackground=BORDER_COLOR,
                highlightthickness=1,
                padx=8,
                pady=6,
                cursor="hand2",
                command=cmd
            )
            btn.grid(row=0, column=idx, padx=4, pady=2, sticky="nsew")
            btn_container.grid_columnconfigure(idx, weight=1)

    def _welcome_greeting(self):
        """Warm audio welcome on startup."""
        def greet():
            speak("Hello! I am Lumi, your friendly learning buddy! What would you like to learn today?")
        threading.Thread(target=greet, daemon=True).start()

    def _update_esp32_indicator(self):
        """Checks ESP32 connection state and updates indicator badge."""
        if is_esp32_connected():
            self.esp32_lbl.config(text="🟢 ESP32: Connected", bg="#065F46", fg="#A7F3D0")
        else:
            port = find_esp32_port()
            if port:
                self.esp32_lbl.config(text=f"🟡 ESP32: Port {port}", bg="#92400E", fg="#FDE68A")
            else:
                self.esp32_lbl.config(text="⚪ ESP32: Offline", bg=PRIMARY_HOVER, fg="#E0E7FF")

        # Periodically refresh ESP32 status every 10 seconds
        self.root.after(10000, self._update_esp32_indicator)

    def set_status(self, text: str, emoji: str = "✨", bg_color: str = ACCENT_GREEN):
        """Thread-safe update of status pill badge."""
        def update():
            self.status_pill.config(text=f"{emoji} {text}", bg=bg_color)
        self.root.after(0, update)

    def set_transcript(self, text: str):
        """Thread-safe update of transcript preview."""
        def update():
            self.transcript_lbl.config(text=text)
        self.root.after(0, update)

    def update_card(
        self,
        category: str,
        name: str,
        title: str,
        subtitle: str,
        emoji: str = "✨"
    ):
        """
        Thread-safe callback to update the central card with image, title, and subtitle.
        Matches the ui_callback signature used across all learning modules.
        """
        def update():
            self.card_title_lbl.config(text=title)
            self.card_sub_lbl.config(text=subtitle)

            # Load and set Tkinter image
            try:
                tk_img = get_tk_image(
                    category=category,
                    name=name,
                    size=(250, 250),
                    fallback_title=title,
                    fallback_subtitle=subtitle,
                    fallback_emoji=emoji
                )
                self.current_tk_image = tk_img
                self.card_img_lbl.config(image=tk_img)
            except Exception as e:
                print(f"⚠️ Image render error: {e}")

        self.root.after(0, update)

    def status_callback(self, state: str):
        """
        Callback for speech/TTS state changes.
        """
        if state == "listening":
            self.set_status("Listening...", "🎙️", ACCENT_YELLOW)
            self.set_transcript("🎤 Listening to your voice... Speak clearly!")
        elif state == "speech_detected":
            self.set_status("Hearing you...", "👂", ACCENT_YELLOW)
        elif state == "processing":
            self.set_status("Understanding...", "⏳", ACCENT_BLUE)
            self.set_transcript("⏳ Processing what you said...")
        elif state == "speaking":
            self.set_status("Speaking...", "🔊", PRIMARY)
        elif state == "idle":
            if not self.is_running_lesson:
                self.set_status("Ready", "✨", ACCENT_GREEN)

    def stop_check(self) -> bool:
        """Returns True if the user requested stopping the current activity."""
        return self.stop_requested

    def stop_current_activity(self):
        """Signals stop flag to interrupt ongoing lesson or speech."""
        self.stop_requested = True
        self.set_status("Stopping...", "🛑", ACCENT_RED)
        self.set_transcript("🛑 Stopped by user.")
        speak_async("Activity stopped.")

    def launch_module(self, module_name: str, interactive_voice: bool = True):
        """Launches a learning module on a worker thread."""
        if self.is_running_lesson:
            self.stop_current_activity()
            # Wait briefly for previous thread to notice stop flag
            self.root.after(400, lambda: self._start_module_thread(module_name, interactive_voice))
        else:
            self._start_module_thread(module_name, interactive_voice)

    def _start_module_thread(self, module_name: str, interactive_voice: bool):
        """Internal helper to start thread."""
        self.stop_requested = False
        self.is_running_lesson = True
        self.set_status(f"Learning {module_name.capitalize()}", "📚", PRIMARY)

        def runner():
            try:
                if module_name == "alphabet":
                    alphabet_lesson(
                        ui_callback=self.update_card,
                        status_callback=self.status_callback,
                        stop_check=self.stop_check,
                        interactive_voice=interactive_voice
                    )
                elif module_name == "numbers":
                    number_lesson(
                        ui_callback=self.update_card,
                        status_callback=self.status_callback,
                        stop_check=self.stop_check,
                        interactive_voice=interactive_voice
                    )
                elif module_name == "colors":
                    color_lesson(
                        ui_callback=self.update_card,
                        status_callback=self.status_callback,
                        stop_check=self.stop_check,
                        interactive_voice=interactive_voice
                    )
                elif module_name == "animals":
                    animal_lesson(
                        ui_callback=self.update_card,
                        status_callback=self.status_callback,
                        stop_check=self.stop_check,
                        interactive_voice=interactive_voice
                    )
                elif module_name == "math":
                    math_lesson(
                        ui_callback=self.update_card,
                        status_callback=self.status_callback,
                        stop_check=self.stop_check,
                        interactive_voice=interactive_voice
                    )
                elif module_name == "quiz":
                    run_quiz(
                        ui_callback=self.update_card,
                        status_callback=self.status_callback,
                        stop_check=self.stop_check,
                        interactive_voice=interactive_voice
                    )
                elif module_name == "story":
                    story_lesson(
                        ui_callback=self.update_card,
                        status_callback=self.status_callback,
                        stop_check=self.stop_check,
                        interactive_voice=interactive_voice
                    )
            except Exception as e:
                print(f"⚠️ Error running {module_name}: {e}")
            finally:
                self.is_running_lesson = False
                self.set_status("Ready", "✨", ACCENT_GREEN)

        self.active_thread = threading.Thread(target=runner, daemon=True)
        self.active_thread.start()

    def trigger_voice_command(self):
        """Listens for a voice command and dispatches to the matching intent."""
        if self.is_running_lesson:
            self.stop_current_activity()

        def listen_and_dispatch():
            self.status_callback("listening")
            spoken = listen(status_callback=self.status_callback)

            if not spoken:
                self.set_status("Ready", "✨", ACCENT_GREEN)
                self.set_transcript("💬 I didn't hear anything. Click Voice Command or any button to try again!")
                speak("I didn't hear you. Please try again or click a lesson below.")
                return

            self.set_transcript(f'💬 You said: "{spoken}"')
            self.dispatch_voice_command(spoken)

        threading.Thread(target=listen_and_dispatch, daemon=True).start()

    def dispatch_voice_command(self, spoken_text: str):
        """Analyzes spoken text and triggers the appropriate action."""
        command_map = {
            "alphabet": ["alphabet", "alphabets", "abc", "abcs", "letters", "letter", "learn alphabet"],
            "numbers": ["number", "numbers", "counting", "count", "learn numbers"],
            "colors": ["color", "colors", "colour", "colours", "rainbow", "learn colors"],
            "animals": ["animal", "animals", "creatures", "pets", "zoo", "learn animals"],
            "math": ["math", "mathematics", "addition", "subtraction", "plus", "minus", "arithmetic"],
            "quiz": ["quiz", "test", "trivia", "game", "challenge", "exam"],
            "story": ["story", "stories", "bedtime story", "tale", "read a story", "tell a story", "book"],
            "progress": ["progress", "score", "scores", "performance", "report", "stats", "history"],
            "help": ["help", "what can you do", "commands", "options", "menu"],
            "exit": ["exit", "quit", "bye", "goodbye", "close", "shut down"]
        }

        intent = match_command(spoken_text, command_map)

        if intent in ("alphabet", "numbers", "colors", "animals", "math", "quiz", "story"):
            speak(f"Starting {intent} lesson!")
            self.launch_module(intent)
        elif intent == "progress":
            self.read_progress_summary()
            self.open_stats_modal()
        elif intent == "help":
            help_msg = "You can ask me to learn alphabets, numbers, colors, animals, math, play a quiz, or hear a story!"
            speak(help_msg)
            self.set_transcript(f"💡 {help_msg}")
        elif intent == "exit":
            speak("Goodbye! Keep learning and see you soon!")
            self.root.after(1000, self.on_close)
        else:
            fallback_msg = "I didn't quite catch that. You can say alphabet, numbers, colors, animals, math, quiz, or story."
            speak(fallback_msg)
            self.set_transcript(f"❓ {fallback_msg}")

    def read_progress_summary(self):
        """Reads overall progress stats via audio."""
        def read_stats():
            stats = get_summary_stats()
            total_lessons = stats["total_lessons"]
            pct = stats["overall_percentage"]
            if total_lessons == 0:
                speak("You haven't completed any lessons yet. Start a lesson to earn your stars!")
            else:
                speak(f"You have completed {total_lessons} lessons with an overall accuracy of {pct} percent! Super job!")

        threading.Thread(target=read_stats, daemon=True).start()

    def open_stats_modal(self):
        """Opens a modal popup showing detailed progress and quiz scores."""
        stats = get_summary_stats()
        progress_data = get_progress(limit=10)
        quiz_data = get_quiz_attempts(limit=5)

        modal = tk.Toplevel(self.root)
        modal.title("📊 My Learning Progress")
        modal.geometry("520x560")
        modal.configure(bg=BG_MAIN)
        modal.transient(self.root)
        modal.grab_set()

        # Modal Header
        m_head = tk.Frame(modal, bg=PRIMARY, padx=16, pady=12)
        m_head.pack(fill=tk.X)

        m_title = tk.Label(
            m_head,
            text="🏆 Learning Achievements",
            font=("Segoe UI", 16, "bold"),
            fg="#FFFFFF",
            bg=PRIMARY
        )
        m_title.pack(side=tk.LEFT)

        # Overview Stats Card
        overview_frame = tk.Frame(modal, bg=BG_CARD, bd=1, relief=tk.SOLID, highlightbackground=BORDER_COLOR, padx=16, pady=12)
        overview_frame.pack(fill=tk.X, padx=16, pady=12)

        tk.Label(overview_frame, text=f"Total Lessons Completed: {stats['total_lessons']}", font=("Segoe UI", 12, "bold"), fg=TEXT_DARK, bg=BG_CARD).pack(anchor="w", pady=2)
        tk.Label(overview_frame, text=f"Total Score: {stats['total_score']} / {stats['total_questions']} ({stats['overall_percentage']}%)", font=("Segoe UI", 11), fg=ACCENT_GREEN, bg=BG_CARD).pack(anchor="w", pady=2)

        if stats["latest_quiz_score"] is not None:
            tk.Label(overview_frame, text=f"Latest Quiz: {stats['latest_quiz_score']}/{stats['latest_quiz_total']} ({stats['latest_quiz_pct']}%)", font=("Segoe UI", 11), fg=PRIMARY, bg=BG_CARD).pack(anchor="w", pady=2)

        # Recent Lessons List
        tk.Label(modal, text="Recent Completed Activities", font=("Segoe UI", 12, "bold"), fg=TEXT_DARK, bg=BG_MAIN).pack(anchor="w", padx=16, pady=(8, 4))

        list_frame = tk.Frame(modal, bg=BG_CARD, bd=1, relief=tk.SOLID, highlightbackground=BORDER_COLOR)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_box = tk.Text(list_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, font=("Segoe UI", 10), bg=BG_CARD, fg=TEXT_DARK, bd=0, padx=10, pady=10)
        text_box.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_box.yview)

        if not progress_data and not quiz_data:
            text_box.insert(tk.END, "No learning records found yet. Complete a lesson to see your achievements here!\n")
        else:
            if progress_data:
                text_box.insert(tk.END, "--- Lessons ---\n")
                for row in progress_data:
                    lesson, score, total, completed_at = row[0], row[1], row[2], row[3]
                    pct = int((score / total) * 100) if total > 0 else 0
                    text_box.insert(tk.END, f"• {lesson}: {score}/{total} ({pct}%) on {completed_at}\n")
                text_box.insert(tk.END, "\n")

            if quiz_data:
                text_box.insert(tk.END, "--- Quizzes ---\n")
                for q in quiz_data:
                    cat, score, total, pct, completed_at = q[0], q[1], q[2], q[3], q[4]
                    text_box.insert(tk.END, f"• {cat} Quiz: {score}/{total} ({pct}%) on {completed_at}\n")

        text_box.config(state=tk.DISABLED)

        # Close button
        close_btn = tk.Button(
            modal,
            text="Close",
            font=("Segoe UI", 10, "bold"),
            bg=PRIMARY,
            fg="#FFFFFF",
            activebackground=PRIMARY_HOVER,
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=16,
            pady=6,
            cursor="hand2",
            command=modal.destroy
        )
        close_btn.pack(pady=(0, 12))

    def on_close(self):
        """Handles application shutdown cleanly."""
        self.stop_requested = True
        self.root.destroy()
        sys.exit(0)


def launch_gui():
    """Starts the Lumi GUI main loop."""
    root = tk.Tk()
    app = LumiGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
