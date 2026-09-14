# 🌟 Lumi - 100% Offline AI Learning Companion for Kids

Lumi is a **100% offline**, voice-first educational AI companion designed for children. It delivers interactive multimodal lessons, quizzes, storytelling, and progress tracking with zero cloud dependencies, zero external APIs, and full privacy.

---

## ✨ Features

- **100% Offline Operation**: Powered entirely by local on-device models, offline TTS, local SQLite database, and local CSV/text datasets.
- **Local Voice Recognition**: Faster-Whisper base-en running locally on CPU with INT8 quantization, paired with streaming WebRTC VAD and dynamic silence detection.
- **Child-Friendly Voice Output**: Offline speech synthesis via `pyttsx3` (SAPI5) calibrated to a clear 140 WPM pace.
- **Modern Multimodal Tkinter GUI**: Responsive visual cards, real-time live status pills, transcript display, quick-action module buttons, and statistics viewer.
- **Educational Modules**:
  1. 🔤 **Alphabet Learning**: A-Z phonics, vocabulary words, and interactive voice recall.
  2. 🔢 **Numbers & Counting**: 1-10 counting, number words, and visual digit cards.
  3. 🎨 **Colors & Rainbows**: Color recognition, real-world examples, and hex visual swatches.
  4. 🐾 **Animals & Sounds**: Animal names, sounds, and interactive guessing.
  5. ➕ **Math Practice**: Mental arithmetic (addition, subtraction, multiplication) with dynamic formula rendering.
  6. ❓ **Interactive Quiz**: Multidisciplinary quiz with score tracking and instant feedback.
  7. 📖 **Bedtime Stories**: Expressive read-aloud storybook mode with chapter visuals.
- **Robust Child Speech Normalization**: Flexible answer matching supporting number words ("twenty one" -> 21), conversational filler stripping ("I think the answer is..."), and fuzzy selection.
- **Local Progress & Analytics**: Persistent SQLite storage (`Database/learning_n.db`) tracking lesson mastery, quiz scores, accuracy, and activity history.
- **Optional ESP32 Hardware Integration**: Expressive LED and facial signals over serial with auto-detection and safe headless fallback when disconnected.

---

## 📁 Project Structure

```
Offline_learning_companion/
│
├── Python/
│   ├── Learning/
│   │   ├── alphabets.py      # Alphabet lesson module
│   │   ├── animals.py        # Animal learning module
│   │   ├── colors.py         # Colors learning module
│   │   ├── math.py           # Arithmetic practice module
│   │   ├── numbers.py        # Counting and numbers module
│   │   ├── quiz.py           # Multidisciplinary quiz module
│   │   └── story.py          # Bedtime storytelling module
│   │
│   ├── answer_matcher.py     # Child speech normalization & intent matching
│   ├── data_loader.py        # Safe CSV & TXT dataset loader
│   ├── database.py           # SQLite database schema & migrations
│   ├── generate_assets.py    # Offline asset generator
│   ├── gui.py                # Tkinter graphical interface
│   ├── image_manager.py      # Pillow visual card renderer & image caching
│   ├── main.py               # Master entrypoint & voice command loop
│   ├── serial_comm.py        # Optional ESP32 serial communication
│   ├── speech.py             # Offline Whisper & WebRTC VAD recognition
│   └── tts.py                # Offline pyttsx3 speech synthesis
│
├── Dataset/
│   ├── alphabets.csv         # Alphabet words and emojis
│   ├── animals.csv           # Animals and sounds
│   ├── colors.csv            # Colors, hex codes, examples
│   ├── numbers.csv           # Numbers and words
│   ├── quiz.csv              # Question bank and accepted answers
│   └── stories.txt           # Storybook tales
│
├── Database/
│   └── learning_n.db         # Local SQLite database
│
├── Images/
│   ├── Alphabet/             # Alphabet visual cards
│   ├── Animals/              # Animal cards
│   ├── Colors/               # Color cards
│   ├── Numbers/              # Number cards
│   ├── Stories/              # Storybook illustrations
│   └── UI/                   # UI assets and logos
│
├── Models/
│   └── whisper-base-en/      # Local Faster-Whisper model weights
│
├── Arduino/
│   └── esp32_firmware.ino    # Optional ESP32 companion firmware
│
├── test_full_suite.py        # Comprehensive test suite
├── requirements.txt          # Python dependencies
├── install.bat               # One-click environment installer
└── run.bat                   # One-click Lumi launcher
```

---

## 🚀 Getting Started

### 1. One-Click Environment Setup
Run the automated installer to set up the virtual environment and dependencies:
```cmd
install.bat
```
Or manually:
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Launching Lumi

**GUI Mode (Default):**
Double-click `run.bat` or run:
```cmd
.venv\Scripts\python.exe -m Python.main
```

**Voice-Only CLI Mode:**
```cmd
.venv\Scripts\python.exe -m Python.main --cli
```

---

## 🧪 Running Automated Tests

Run the full automated test suite covering all data loaders, database operations, speech normalization, image cards, serial fallback, and learning modules:

```cmd
.venv\Scripts\python.exe -m unittest test_full_suite.py
```

---

## 🎙️ Spoken Voice Commands

Lumi naturally understands child voice intents, including:
- *"Let's learn the alphabet"* / *"Letters"* -> Alphabet Module
- *"Can we count numbers?"* / *"Numbers"* -> Numbers Module
- *"Show me colors"* / *"Rainbow"* -> Colors Module
- *"What animals are there?"* / *"Zoo"* -> Animals Module
- *"Let's do math"* / *"Addition"* -> Math Module
- *"Play a quiz"* / *"Ask me questions"* -> Quiz Mode
- *"Tell me a story"* / *"Bedtime story"* -> Story Mode
- *"Check my score"* / *"Progress"* -> Progress & Stats Summary
- *"What can you do?"* / *"Help"* -> Help menu
- *"Goodbye"* / *"Exit"* -> Shut down
