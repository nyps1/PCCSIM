from datetime import datetime


class PCCIMService:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def generate_request_no(self):
        now = datetime.now()
        return now.strftime("PCCIM-%Y%m%d-%H%M%S-%f")

    def get_today(self):
        return datetime.now().strftime("%Y-%m-%d")

    def create_application(self, application):
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
                machine,
                module_name,
                department,
                author,
                problem_description,
                action_taken,
                impact_container,
                need_help,
                root_cause,
                solution
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, application.to_tuple())

        conn.commit()
        conn.close()

    def add_attachment(self, attachment):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO attachments (
                request_no,
                image_no,
                file_path,
                remark
            )
            VALUES (?, ?, ?, ?)
        """, attachment.to_tuple())

        conn.commit()
        conn.close()

    def search_applications(self, filters):
        conn = self.db_manager.get_connection()

        sql = """
            SELECT
                request_no,
                apply_date,
                title,
                in_dn,
                create_date,
                close_date,
                machine,
                module_name,
                department,
                author
            FROM applications
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
            sql += " AND in_dn = ?"
            params.append(filters["in_dn"])

        if filters.get("create_date"):
            sql += " AND create_date = ?"
            params.append(filters["create_date"])

        if filters.get("close_date"):
            sql += " AND close_date = ?"
            params.append(filters["close_date"])

        if filters.get("machine"):
            sql += " AND machine LIKE ?"
            params.append(f"%{filters['machine']}%")

        if filters.get("module_name"):
            sql += " AND module_name LIKE ?"
            params.append(f"%{filters['module_name']}%")

        if filters.get("department"):
            sql += " AND department LIKE ?"
            params.append(f"%{filters['department']}%")

        if filters.get("author"):
            sql += " AND author LIKE ?"
            params.append(f"%{filters['author']}%")

        sql += " ORDER BY id DESC"

        rows = conn.execute(sql, params).fetchall()
        conn.close()

        return rows

    def get_application_by_request_no(self, request_no):
        conn = self.db_manager.get_connection()

        row = conn.execute("""
            SELECT *
            FROM applications
            WHERE request_no = ?
        """, (request_no,)).fetchone()

        conn.close()
        return row

    def get_attachments_by_request_no(self, request_no):
        conn = self.db_manager.get_connection()

        rows = conn.execute("""
            SELECT *
            FROM attachments
            WHERE request_no = ?
            ORDER BY image_no
        """, (request_no,)).fetchall()

        conn.close()
        return rows