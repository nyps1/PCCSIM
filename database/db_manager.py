import sqlite3
from typing import Any

class DatabaseManager:
    """
    資料庫連線管理員 (Database Manager)
    採用 Factory Pattern (工廠模式) 來提供資料庫連線實體。
    
    [深度原理揭示]
    為了避免多執行緒 (Multi-threading) 下的 Concurrency Safety (併發安全) 問題，
    我們採用每個 Request 動態呼叫 `get_connection()` 建立獨立連線。
    此機制能有效避免跨執行緒共用連線所引發的 Thread Safety 異常。
    """
    def __init__(self, db_path: str) -> None:
        self.db_path: str = db_path

    def get_connection(self) -> sqlite3.Connection:
        """
        建立並回傳一個全新的資料庫連線。
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                request_no TEXT UNIQUE NOT NULL,
                apply_date TEXT,

                title TEXT,
                in_dn TEXT,
                create_date TEXT,
                close_date TEXT,
                machine_or_tool TEXT,
                module_name TEXT,
                department TEXT,
                author TEXT,

                content_input_mode TEXT DEFAULT 'manual',

                problem_description TEXT,
                problem_timeline TEXT,

                action_taken TEXT,

                impact TEXT,

                container TEXT,

                need_help TEXT,

                root_cause_description TEXT,
                root_cause_possible_cause TEXT,
                root_cause_troubleshooting_timeline TEXT,

                solution TEXT,

                implementation TEXT,

                monitoring TEXT,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                request_no TEXT NOT NULL,

                section_name TEXT NOT NULL,
                attachment_no INTEGER,

                file_path TEXT NOT NULL,
                original_file_name TEXT,
                file_type TEXT,

                remark TEXT,

                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS application_edit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                request_no TEXT NOT NULL,

                modifier_department TEXT NOT NULL,
                modifier_author TEXT NOT NULL,

                edit_summary TEXT,

                edited_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()


"""
application table right now

application_edit_logs
│
├── id
├── request_no
├── modifier_department
├── modifier_author
├── edit_summary
└── edited_at
"""