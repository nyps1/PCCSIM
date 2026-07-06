import sqlite3


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
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

        conn.commit()
        conn.close()