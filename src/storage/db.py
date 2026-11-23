"""
src/storage/db.py
SQLite persistence engine for deduplication, Day 1 vs Day 2 diffing,
raw JSON/HTML snapshot tracking, runtime metrics, and cost accounting.
"""

import json
import os
import sqlite3
import time
from typing import Any, Dict, List, Optional, Tuple
from src.models import (
    ChangedDay2Enum,
    QuestionRecord,
    VisibilityStatusEnum,
)


class Database:
    """
    Manages SQLite database state for the IncuBrix Visibility Engine.
    Ensures strict deduplication, Day 1 to Day 2 diffing, and run auditability.
    """

    def __init__(self, db_path: str = "output/visibility_state.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        """Initializes tables for questions, snapshots, diffs, and execution runs."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Main questions table enforcing UNIQUE constraint on question text
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                question_id TEXT PRIMARY KEY,
                question TEXT NOT NULL UNIQUE,
                intent TEXT NOT NULL,
                source_type TEXT NOT NULL,
                source_url TEXT NOT NULL,
                market TEXT NOT NULL,
                google_position TEXT NOT NULL,
                answer_box_or_ai_overview TEXT NOT NULL,
                quoted_source_url TEXT NOT NULL,
                chatgpt TEXT NOT NULL,
                gemini TEXT NOT NULL,
                perplexity TEXT NOT NULL,
                claude_or_copilot TEXT NOT NULL,
                competitors_named TEXT NOT NULL,
                check_date_day1 TEXT NOT NULL,
                check_date_day2 TEXT NOT NULL,
                changed_on_day2 TEXT NOT NULL,
                raw_answers_url TEXT NOT NULL,
                priority TEXT NOT NULL,
                notes TEXT NOT NULL,
                day1_snapshot TEXT,
                day2_snapshot TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Raw snapshot log for evidence tracing
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id TEXT NOT NULL,
                tool_or_assistant TEXT NOT NULL,
                day INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                response_snippet TEXT,
                latency_ms INTEGER,
                cost_usd REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (question_id) REFERENCES questions(question_id)
            );
            """)

            # Day 1 vs Day 2 diff audit trail
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS day_diffs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                day1_val TEXT NOT NULL,
                day2_val TEXT NOT NULL,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (question_id) REFERENCES questions(question_id)
            );
            """)

            # Engine run audit table (for Tab 03_ENGINE_LAUNCH Section B)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_type TEXT NOT NULL,
                input_size INTEGER NOT NULL,
                items_produced INTEGER NOT NULL,
                items_rejected INTEGER NOT NULL,
                duplicates_removed INTEGER NOT NULL,
                runtime_seconds REAL NOT NULL,
                direct_cost_usd REAL NOT NULL,
                evidence_log_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Indices for rapid querying
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_q ON questions(question);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_market ON questions(market);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_priority ON questions(priority);")
            conn.commit()

    def question_exists(self, question_text: str) -> bool:
        """Checks if a normalized question already exists in the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM questions WHERE TRIM(LOWER(question)) = TRIM(LOWER(?))", (question_text,))
            return cursor.fetchone() is not None

    def upsert_question(self, record: QuestionRecord, day: int = 1) -> Tuple[bool, bool]:
        """
        Inserts or updates a question record.
        Returns:
            (inserted: bool, updated: bool)
        Calculates changed_on_day2 when day == 2.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Check existing record by question text or ID
            cursor.execute(
                "SELECT * FROM questions WHERE TRIM(LOWER(question)) = TRIM(LOWER(?)) OR question_id = ?",
                (record.question, record.question_id)
            )
            existing = cursor.fetchone()

            if existing is None:
                # Fresh insertion
                cursor.execute("""
                INSERT INTO questions (
                    question_id, question, intent, source_type, source_url, market,
                    google_position, answer_box_or_ai_overview, quoted_source_url,
                    chatgpt, gemini, perplexity, claude_or_copilot, competitors_named,
                    check_date_day1, check_date_day2, changed_on_day2, raw_answers_url,
                    priority, notes, day1_snapshot
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    record.question_id, record.question, record.intent.value, record.source_type,
                    record.source_url, record.market.value, str(record.google_position),
                    record.answer_box_or_ai_overview.value, record.quoted_source_url,
                    record.chatgpt.value, record.gemini.value, record.perplexity.value,
                    record.claude_or_copilot.value, record.competitors_named,
                    record.check_date_day1, record.check_date_day2, record.changed_on_day2.value,
                    record.raw_answers_url, record.priority.value, record.notes,
                    json.dumps(record.to_dict_20_columns())
                ))
                conn.commit()
                return True, False
            else:
                # Update existing record
                existing_dict = dict(existing)
                changed_on_day2 = existing_dict.get("changed_on_day2", "No")

                if day == 2:
                    # Diff Day 1 vs Day 2
                    diffs = []
                    metrics = [
                        ("google_position", existing_dict["google_position"], str(record.google_position)),
                        ("answer_box_or_ai_overview", existing_dict["answer_box_or_ai_overview"], record.answer_box_or_ai_overview.value),
                        ("chatgpt", existing_dict["chatgpt"], record.chatgpt.value),
                        ("gemini", existing_dict["gemini"], record.gemini.value),
                        ("perplexity", existing_dict["perplexity"], record.perplexity.value),
                        ("claude_or_copilot", existing_dict["claude_or_copilot"], record.claude_or_copilot.value),
                    ]
                    for name, d1, d2 in metrics:
                        if str(d1).strip().lower() != str(d2).strip().lower():
                            diffs.append((name, str(d1), str(d2)))
                            cursor.execute(
                                "INSERT INTO day_diffs (question_id, metric_name, day1_val, day2_val) VALUES (?, ?, ?, ?)",
                                (record.question_id, name, str(d1), str(d2))
                            )

                    changed_on_day2 = "Yes" if len(diffs) > 0 else "No"

                cursor.execute("""
                UPDATE questions SET
                    google_position = ?,
                    answer_box_or_ai_overview = ?,
                    quoted_source_url = ?,
                    chatgpt = ?,
                    gemini = ?,
                    perplexity = ?,
                    claude_or_copilot = ?,
                    competitors_named = ?,
                    check_date_day2 = ?,
                    changed_on_day2 = ?,
                    raw_answers_url = ?,
                    notes = ?,
                    day2_snapshot = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE question_id = ?;
                """, (
                    str(record.google_position),
                    record.answer_box_or_ai_overview.value,
                    record.quoted_source_url,
                    record.chatgpt.value,
                    record.gemini.value,
                    record.perplexity.value,
                    record.claude_or_copilot.value,
                    record.competitors_named,
                    record.check_date_day2,
                    changed_on_day2,
                    record.raw_answers_url,
                    record.notes,
                    json.dumps(record.to_dict_20_columns()),
                    record.question_id
                ))
                conn.commit()
                return False, True

    def save_snapshot(
        self,
        question_id: str,
        tool_or_assistant: str,
        day: int,
        file_path: str,
        response_snippet: str = "",
        latency_ms: int = 0,
        cost_usd: float = 0.0
    ) -> None:
        """Logs evidence snapshot path and metadata."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO snapshots (
                question_id, tool_or_assistant, day, file_path, response_snippet, latency_ms, cost_usd
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (question_id, tool_or_assistant, day, file_path, response_snippet[:300], latency_ms, cost_usd))
            conn.commit()

    def log_run(
        self,
        run_type: str,
        input_size: int,
        items_produced: int,
        items_rejected: int,
        duplicates_removed: int,
        runtime_seconds: float,
        direct_cost_usd: float,
        evidence_log_path: str = ""
    ) -> int:
        """Logs an engine execution run for the official workbook audit."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO runs (
                run_type, input_size, items_produced, items_rejected,
                duplicates_removed, runtime_seconds, direct_cost_usd, evidence_log_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                run_type, input_size, items_produced, items_rejected,
                duplicates_removed, runtime_seconds, direct_cost_usd, evidence_log_path
            ))
            conn.commit()
            return cursor.lastrowid

    def get_all_questions(self) -> List[QuestionRecord]:
        """Retrieves all stored questions ordered by question_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questions ORDER BY question_id ASC")
            rows = cursor.fetchall()
            return [QuestionRecord(**dict(row)) for row in rows]

    def get_question_count(self) -> int:
        """Returns total distinct question count."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM questions")
            return cursor.fetchone()[0]

    def get_run_history(self) -> List[Dict[str, Any]]:
        """Retrieves list of past runs."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM runs ORDER BY run_id ASC")
            return [dict(r) for r in cursor.fetchall()]

    def get_diff_summary(self) -> Dict[str, Any]:
        """Returns summary of Day 1 vs Day 2 differences."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM day_diffs")
            total_diffs = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT question_id) FROM day_diffs")
            changed_questions = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM questions WHERE changed_on_day2 = 'Yes'")
            marked_changed = cursor.fetchone()[0]
            return {
                "total_diff_events": total_diffs,
                "changed_question_count": changed_questions,
                "marked_changed": marked_changed
            }

    def clear_all(self) -> None:
        """Clears all questions, snapshots, diffs, and runs for a clean baseline run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM questions")
            cursor.execute("DELETE FROM snapshots")
            cursor.execute("DELETE FROM day_diffs")
            cursor.execute("DELETE FROM runs")
            conn.commit()
