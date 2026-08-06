import os
import glob
from datetime import datetime
from typing import Dict, Any, List, Optional
import sqlite3
from database.db_manager import DatabaseManager
from werkzeug.datastructures import FileStorage
from services.ppt_importer import ppt_importer
from utils.file_helper import FileHelper
from models.attachment import Attachment


class PCCIMService:
    """
    PCCIM 核心商業邏輯服務 (Service Layer)
    
    [設計模式約束]
    本模組實作了 Service/Repository Pattern。
    將商業邏輯 (Business Logic) 與資料庫存取細節從 Controller (Flask Routes) 中抽離。
    Controller 僅負責接收請求與回傳回應，所有具體實作皆由 Service 負責，達到關注點分離 (Separation of Concerns)。
    """
    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager: DatabaseManager = db_manager

    def generate_request_no(self) -> str:
        now = datetime.now()
        return now.strftime("PCCIM-%Y%m%d-%H%M%S-%f")

    def get_today(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")

    def create_label(self, name: str) -> Optional[sqlite3.Row]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO labels (name) VALUES (?)", (name,))
            conn.commit()
            return cursor.execute("SELECT * FROM labels WHERE id = ?", (cursor.lastrowid,)).fetchone()
        except sqlite3.IntegrityError:
            return conn.execute("SELECT * FROM labels WHERE name = ?", (name,)).fetchone()
        finally:
            conn.close()

    def get_all_labels(self) -> List[sqlite3.Row]:
        conn = self.db_manager.get_connection()
        rows = conn.execute("SELECT * FROM labels ORDER BY name").fetchall()
        conn.close()
        return rows

    def create_application(self, application: Any) -> None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO applications (
                request_no,
                apply_date,

                title,
                in_dn,
                create_date,
                close_date,
                machine_or_tool,
                module_name,
                department,
                author,

                content_input_mode,

                problem_description,
                problem_timeline,

                action_taken,

                impact,

                container,

                need_help,

                root_cause_description,
                root_cause_possible_cause,
                root_cause_troubleshooting_timeline,

                solution,

                implementation,

                monitoring
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, application.to_tuple())

        if getattr(application, 'labels', None):
            for label_id in application.labels:
                cursor.execute(
                    "INSERT INTO application_labels (application_request_no, label_id) VALUES (?, ?)",
                    (application.request_no, label_id)
                )

        conn.commit()
        conn.close()

    def update_application(self, request_no: str, data: Dict[str, Any]) -> None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE applications
            SET
                title = ?,
                in_dn = ?,
                create_date = ?,
                close_date = ?,
                machine_or_tool = ?,
                module_name = ?,
                department = ?,
                author = ?,

                problem_description = ?,
                problem_timeline = ?,

                action_taken = ?,

                impact = ?,

                container = ?,

                need_help = ?,

                root_cause_description = ?,
                root_cause_possible_cause = ?,
                root_cause_troubleshooting_timeline = ?,

                solution = ?,

                implementation = ?,

                monitoring = ?,

                updated_at = CURRENT_TIMESTAMP
            WHERE request_no = ?
        """, (
            data.get("title", ""),
            data.get("in_dn", ""),
            data.get("create_date", ""),
            data.get("close_date", ""),
            data.get("machine_or_tool", ""),
            data.get("module_name", ""),
            data.get("department", ""),
            data.get("author", ""),

            data.get("problem_description", ""),
            data.get("problem_timeline", ""),

            data.get("action_taken", ""),

            data.get("impact", ""),

            data.get("container", ""),

            data.get("need_help", ""),

            data.get("root_cause_description", ""),
            data.get("root_cause_possible_cause", ""),
            data.get("root_cause_troubleshooting_timeline", ""),

            data.get("solution", ""),

            data.get("implementation", ""),

            data.get("monitoring", ""),

            request_no
        ))

        labels = data.get("labels", [])
        cursor.execute("DELETE FROM application_labels WHERE application_request_no = ?", (request_no,))
        for label_id in labels:
            cursor.execute(
                "INSERT INTO application_labels (application_request_no, label_id) VALUES (?, ?)",
                (request_no, label_id)
            )

        conn.commit()
        conn.close()

    def add_attachment(self, attachment: Any) -> None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO attachments (
                request_no,
                section_name,
                attachment_no,
                file_path,
                original_file_name,
                file_type,
                remark
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, attachment.to_tuple())

        conn.commit()
        conn.close()

    def add_edit_log(
        self,
        request_no: str,
        modifier_department: str,
        modifier_author: str,
        edit_summary: str
    ) -> None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO application_edit_logs (
                request_no,
                modifier_department,
                modifier_author,
                edit_summary
            )
            VALUES (?, ?, ?, ?)
        """, (
            request_no,
            modifier_department,
            modifier_author,
            edit_summary
        ))

        conn.commit()
        conn.close()

    def get_edit_logs_by_request_no(self, request_no: str) -> List[sqlite3.Row]:
        conn = self.db_manager.get_connection()

        rows = conn.execute("""
            SELECT *
            FROM application_edit_logs
            WHERE request_no = ?
            ORDER BY edited_at DESC
        """, (request_no,)).fetchall()

        conn.close()
        return rows

    def search_applications(self, filters: Dict[str, Any]) -> List[sqlite3.Row]:
        conn = self.db_manager.get_connection()

        sql = """
            SELECT
                a.request_no,
                a.apply_date,

                a.title,
                a.in_dn,
                a.create_date,
                a.close_date,
                a.machine_or_tool,
                a.module_name,
                a.department,
                a.author,
                a.content_input_mode,
                GROUP_CONCAT(l.id) as label_ids,
                GROUP_CONCAT(l.name) as label_names
            FROM applications a
            LEFT JOIN application_labels al ON a.request_no = al.application_request_no
            LEFT JOIN labels l ON al.label_id = l.id
            WHERE 1 = 1
        """

        params = []

        if filters.get("apply_date"):
            sql += " AND apply_date = ?"
            params.append(filters["apply_date"])

        if filters.get("title"):
            sql += " AND title LIKE ?"
            params.append(f"%{filters['title']}%")

        if filters.get("in_dn"):
            sql += " AND in_dn LIKE ?"
            params.append(f"%{filters['in_dn']}%")

        if filters.get("create_date"):
            sql += " AND create_date = ?"
            params.append(filters["create_date"])

        if filters.get("close_date"):
            sql += " AND close_date = ?"
            params.append(filters["close_date"])

        if filters.get("machine_or_tool"):
            sql += " AND machine_or_tool LIKE ?"
            params.append(f"%{filters['machine_or_tool']}%")

        if filters.get("module_name"):
            sql += " AND module_name LIKE ?"
            params.append(f"%{filters['module_name']}%")

        if filters.get("department"):
            sql += " AND department LIKE ?"
            params.append(f"%{filters['department']}%")

        if filters.get("author"):
            sql += " AND author LIKE ?"
            params.append(f"%{filters['author']}%")

        if filters.get("content_input_mode"):
            sql += " AND a.content_input_mode = ?"
            params.append(filters["content_input_mode"])

        if filters.get("label_id"):
            sql += " AND a.request_no IN (SELECT application_request_no FROM application_labels WHERE label_id = ?)"
            params.append(filters["label_id"])

        sql += " GROUP BY a.request_no ORDER BY a.id DESC"

        rows = conn.execute(sql, params).fetchall()
        conn.close()

        return rows

    def get_application_by_request_no(self, request_no: str) -> Optional[sqlite3.Row]:
        conn = self.db_manager.get_connection()

        row = conn.execute("""
            SELECT 
                a.*,
                GROUP_CONCAT(l.id) as label_ids,
                GROUP_CONCAT(l.name) as label_names
            FROM applications a
            LEFT JOIN application_labels al ON a.request_no = al.application_request_no
            LEFT JOIN labels l ON al.label_id = l.id
            WHERE a.request_no = ?
            GROUP BY a.request_no
        """, (request_no,)).fetchone()

        conn.close()
        return row

    def get_attachments_by_request_no(self, request_no: str) -> List[sqlite3.Row]:
        conn = self.db_manager.get_connection()

        rows = conn.execute("""
            SELECT *
            FROM attachments
            WHERE request_no = ?
            ORDER BY section_name, attachment_no
        """, (request_no,)).fetchall()

        conn.close()
        return rows

    def get_attachments_by_section(self, request_no: str, section_name: str) -> List[sqlite3.Row]:
        conn = self.db_manager.get_connection()

        rows = conn.execute("""
            SELECT *
            FROM attachments
            WHERE request_no = ?
            AND section_name = ?
            ORDER BY attachment_no
        """, (request_no, section_name)).fetchall()

        conn.close()
        return rows

    def import_batch_from_directory(self, folder_path: str) -> Dict[str, Any]:
        """
        Scan a local directory for PPT/PPTX files and import them into the system.
        """
        clean_path = folder_path.strip().strip('"\'')
        if not clean_path or not os.path.exists(clean_path) or not os.path.isdir(clean_path):
            return {
                "success": False,
                "message": f"Directory '{folder_path}' does not exist or is not a valid folder.",
                "total": 0,
                "success_count": 0,
                "error_count": 0,
                "details": []
            }

        search_pattern_pptx = os.path.join(clean_path, "*.pptx")
        search_pattern_ppt = os.path.join(clean_path, "*.ppt")
        files = glob.glob(search_pattern_pptx) + glob.glob(search_pattern_ppt)

        if not files:
            return {
                "success": True,
                "message": f"No .ppt or .pptx files found in directory '{clean_path}'.",
                "total": 0,
                "success_count": 0,
                "error_count": 0,
                "details": []
            }

        details = []
        success_count = 0
        error_count = 0

        for file_path in files:
            filename = os.path.basename(file_path)
            try:
                with open(file_path, "rb") as f:
                    file_storage = FileStorage(
                        stream=f,
                        filename=filename,
                        content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    )

                    request_no = self.generate_request_no()
                    apply_date = self.get_today()

                    application, attachments = ppt_importer.import_ppt(file_storage, request_no, apply_date)
                    application.content_input_mode = "ppt"

                    self.create_application(application)

                    for att in attachments:
                        self.add_attachment(att)

                    # Save the original PPT file as an attachment
                    f.seek(0)
                    saved_filename = FileHelper.save_attachment(
                        file=file_storage,
                        request_no=request_no,
                        section_name="content_ppt",
                        attachment_no=1,
                    )

                    ppt_attachment = Attachment(
                        request_no=request_no,
                        section_name="content_ppt",
                        attachment_no=1,
                        file_path=saved_filename,
                        original_file_name=filename,
                        file_type=FileHelper.get_extension(filename),
                        remark="Uploaded content PPT (Batch Directory Import)",
                    )
                    self.add_attachment(ppt_attachment)

                    success_count += 1
                    details.append({
                        "filename": filename,
                        "status": "success",
                        "request_no": request_no,
                        "message": "Successfully imported"
                    })
            except Exception as e:
                error_count += 1
                details.append({
                    "filename": filename,
                    "status": "error",
                    "request_no": "-",
                    "message": str(e)
                })

        return {
            "success": True,
            "message": f"Directory scan complete: {success_count} succeeded, {error_count} failed out of {len(files)} file(s).",
            "total": len(files),
            "success_count": success_count,
            "error_count": error_count,
            "details": details
        }