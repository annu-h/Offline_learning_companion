"""
Lumi - Database Module
Stores progress, quiz attempts, and activity logs in SQLite.
Database: Database/learning_n.db (100% Offline).
"""

import sqlite3
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "Database"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "learning_n.db"


def connect_db() -> sqlite3.Connection:
    """Returns a connection to Database/learning_n.db."""
    return sqlite3.connect(str(DB_PATH))


def create_tables() -> None:
    """Initializes tables and ensures all columns exist."""
    connection = connect_db()
    cursor = connection.cursor()

    # Progress table (compatible with existing code, enhanced with category & details)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson TEXT NOT NULL,
            category TEXT,
            score INTEGER DEFAULT 0,
            total_questions INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            incorrect_answers INTEGER DEFAULT 0,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Check and migrate columns if progress table already existed with older schema
    cursor.execute("PRAGMA table_info(progress)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    if "category" not in existing_cols:
        cursor.execute("ALTER TABLE progress ADD COLUMN category TEXT")
    if "correct_answers" not in existing_cols:
        cursor.execute("ALTER TABLE progress ADD COLUMN correct_answers INTEGER DEFAULT 0")
    if "incorrect_answers" not in existing_cols:
        cursor.execute("ALTER TABLE progress ADD COLUMN incorrect_answers INTEGER DEFAULT 0")

    # Quiz attempts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT DEFAULT 'General',
            score INTEGER DEFAULT 0,
            total_questions INTEGER DEFAULT 0,
            percentage INTEGER DEFAULT 0,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Activity log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_type TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_progress(
    lesson: str,
    score: int,
    total_questions: int,
    category: Optional[str] = None,
    correct_answers: Optional[int] = None,
    incorrect_answers: Optional[int] = None,
) -> int:
    """Saves a completed lesson progress record and logs activity."""
    create_tables()
    cat = category or lesson
    correct = correct_answers if correct_answers is not None else score
    incorrect = incorrect_answers if incorrect_answers is not None else max(0, total_questions - score)

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO progress
        (lesson, category, score, total_questions, correct_answers, incorrect_answers)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (lesson, cat, score, total_questions, correct, incorrect))

    record_id = cursor.lastrowid or 0

    cursor.execute("""
        INSERT INTO activity_log (activity_type, details)
        VALUES (?, ?)
    """, ("lesson", f"Completed {lesson} lesson: {score}/{total_questions}"))

    connection.commit()
    connection.close()
    return record_id


def save_quiz_attempt(
    score: int,
    total_questions: int,
    category: str = "General"
) -> int:
    """Saves a quiz attempt and logs activity."""
    create_tables()
    percentage = int((score / total_questions) * 100) if total_questions > 0 else 0

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO quiz_attempts
        (category, score, total_questions, percentage)
        VALUES (?, ?, ?, ?)
    """, (category, score, total_questions, percentage))

    record_id = cursor.lastrowid or 0

    cursor.execute("""
        INSERT INTO activity_log (activity_type, details)
        VALUES (?, ?)
    """, ("quiz", f"Completed {category} Quiz: {score}/{total_questions} ({percentage}%)"))

    connection.commit()
    connection.close()
    return record_id


def log_activity(activity_type: str, details: str) -> None:
    """Logs any general interaction or event."""
    create_tables()
    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO activity_log (activity_type, details)
            VALUES (?, ?)
        """, (activity_type, details))
        connection.commit()
        connection.close()
    except Exception:
        pass


def get_progress(limit: int = 50) -> List[Tuple[Any, ...]]:
    """Returns progress records (lesson, score, total_questions, completed_at)."""
    create_tables()
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT lesson, score, total_questions, completed_at
        FROM progress
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    results = cursor.fetchall()
    connection.close()
    return results


def get_quiz_attempts(limit: int = 50) -> List[Tuple[Any, ...]]:
    """Returns quiz attempt records (category, score, total_questions, percentage, completed_at)."""
    create_tables()
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT category, score, total_questions, percentage, completed_at
        FROM quiz_attempts
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    results = cursor.fetchall()
    connection.close()
    return results


def get_summary_stats() -> Dict[str, Any]:
    """Computes summary statistics for progress reporting and GUI display."""
    create_tables()
    connection = connect_db()
    cursor = connection.cursor()

    # Total lessons completed
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(score), 0), COALESCE(SUM(total_questions), 0) FROM progress")
    row = cursor.fetchone()
    total_lessons = row[0] if row else 0
    total_score = row[1] if row else 0
    total_questions = row[2] if row else 0

    # Latest quiz score
    cursor.execute("SELECT score, total_questions, percentage FROM quiz_attempts ORDER BY id DESC LIMIT 1")
    quiz_row = cursor.fetchone()
    latest_quiz_score = quiz_row[0] if quiz_row else None
    latest_quiz_total = quiz_row[1] if quiz_row else None
    latest_quiz_pct = quiz_row[2] if quiz_row else None

    # Latest activity
    cursor.execute("SELECT activity_type, details, timestamp FROM activity_log ORDER BY id DESC LIMIT 1")
    act_row = cursor.fetchone()
    latest_activity = {
        "type": act_row[0],
        "details": act_row[1],
        "timestamp": act_row[2]
    } if act_row else None

    connection.close()

    return {
        "total_lessons": total_lessons,
        "total_score": total_score,
        "total_questions": total_questions,
        "overall_percentage": int((total_score / total_questions) * 100) if total_questions > 0 else 0,
        "latest_quiz_score": latest_quiz_score,
        "latest_quiz_total": latest_quiz_total,
        "latest_quiz_pct": latest_quiz_pct,
        "latest_activity": latest_activity
    }


def get_latest_activity() -> Optional[Dict[str, Any]]:
    """Returns the single latest activity record."""
    stats = get_summary_stats()
    return stats["latest_activity"]


if __name__ == "__main__":
    print(f"Database location: {DB_PATH}")
    create_tables()
    print("Database initialized successfully!")
    print("Stats:", get_summary_stats())
