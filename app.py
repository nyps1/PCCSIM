import os
import sys
import socket
import threading
import webbrowser
import multiprocessing

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    send_from_directory,
    jsonify,
    flash,
)

from config import Config

from database.db_manager import DatabaseManager
from services.pccim_service import PCCIMService
from services.ppt_exporter import PowerPointExporter
from services.ppt_importer import ppt_importer
from models.application import Application
from models.attachment import Attachment
from utils.file_helper import FileHelper

"""
PCCSIM 應用程式主入口 (Controller Layer)

[設計模式約束]
本模組扮演 Controller 角色，負責接收 HTTP 請求與回傳回應。
同時展示了基礎的 Dependency Injection (依賴注入) 模式：
我們在此實例化 DatabaseManager，並將其注入至 PCCIMService 中。
這種設計降低了 Service 與具體 DB 實作之間的耦合度，便於未來測試與維護。
"""

# =========================
# Server Config
# =========================
HOST = "0.0.0.0"
PORT = 5005

APP_NAME = "PCCSIM"

# 如果你已經有申請好的內部網域，填在這裡
# 例如：
# INTERNAL_DOMAIN = "pccsim.xxx.com"
# 如果沒有，先留空字串
INTERNAL_DOMAIN = ""

BROWSER_DELAY_SECONDS = 1.5


def get_local_ip():
    """
    Get local LAN IP address.
    Other users in the same internal network can use this IP with the port.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


LOCAL_IP = get_local_ip()

LOCAL_URL = f"http://127.0.0.1:{PORT}/"
NETWORK_URL = f"http://{LOCAL_IP}:{PORT}/"

if INTERNAL_DOMAIN:
    DOMAIN_URL = f"http://{INTERNAL_DOMAIN}:{PORT}/"
else:
    DOMAIN_URL = ""


# =========================
# Flask App Initialization
# =========================
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback_secret_key_for_flash")

Config.init_folders()

db_manager = DatabaseManager(Config.DB_PATH)
db_manager.init_db()

pccim_service = PCCIMService(db_manager)
ppt_exporter = PowerPointExporter(Config.EXPORT_FOLDER)


# =========================
# Auto Open Browser
# =========================
def print_access_urls():
    print("")
    print("========================================")
    print(f"{APP_NAME} Web Server Started")
    print("========================================")
    print("Local access:")
    print(f"  {LOCAL_URL}")
    print("")
    print("Internal network access:")
    print(f"  {NETWORK_URL}")

    if DOMAIN_URL:
        print("")
        print("Domain access:")
        print(f"  {DOMAIN_URL}")

    print("========================================")
    print("")


def open_browser():
    try:
        # 自己這台筆電自動開本機網址
        webbrowser.open_new(LOCAL_URL)
    except Exception as exc:
        app.logger.exception(
            "Failed to open browser automatically: %s",
            exc,
        )


def schedule_browser_open():
    timer = threading.Timer(
        BROWSER_DELAY_SECONDS,
        open_browser,
    )
    timer.daemon = True
    timer.start()


def main():
    is_frozen = getattr(sys, "frozen", False)

    if is_frozen:
        # PyInstaller exe mode.
        # Do not use reloader to avoid duplicate process and duplicate browser tabs.
        print_access_urls()
        schedule_browser_open()

        app.run(
            host=HOST,
            port=PORT,
            debug=False,
            use_reloader=False,
        )

    else:
        # Development mode.
        # Werkzeug reloader starts parent and child process.
        # Only child process should open browser and print access URLs.
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            print_access_urls()
            schedule_browser_open()

        app.run(
            host=HOST,
            port=PORT,
            debug=True,
            use_reloader=True,
        )


# =========================
# Manual content sections attachments
# =========================
ATTACHMENT_SECTIONS = [
    "problem",
    "action_taken",
    "container",
    "root_cause",
    "implementation",
    "monitoring",
    "solution",
]


# =========================
# Display labels
# =========================
SECTION_LABELS = {
    "problem": "Problem",
    "action_taken": "Action Taken",
    "container": "Container",
    "root_cause": "Root Cause",
    "implementation": "Implementation",
    "monitoring": "Monitoring",
    "solution": "Solution",
    "content_ppt": "Completed PPT",
}


# =========================
# Helper Functions
# =========================
def normalize_extension(filename):
    """
    Normalize file extension to lowercase without dot.
    Example:
        test.pptx -> pptx
        test.PPT -> ppt
    """
    ext = FileHelper.get_extension(filename)
    return ext.lower().lstrip(".")


def is_ppt_file(filename):
    ext = normalize_extension(filename)
    return ext in ["ppt", "pptx"]


def build_attachments_by_section(attachments):
    attachments_by_section = {}

    for section in SECTION_LABELS.keys():
        attachments_by_section[section] = []

    for attachment in attachments:
        section_name = attachment["section_name"]

        if section_name not in attachments_by_section:
            attachments_by_section[section_name] = []

        attachments_by_section[section_name].append(attachment)

    return attachments_by_section


# =========================
# Routes
# =========================
@app.route("/")
def index():
    return redirect(url_for("apply"))

@app.route("/batch_import_page", methods=["GET", "POST"])
def batch_import_page():
    batch_results = None

    if request.method == "POST":
        files = request.files.getlist("batch_ppt_files")
        if not files or all(f.filename == '' for f in files):
            flash("No files selected for import.", "error")
            return redirect(request.url)
            
        success_count = 0
        error_count = 0
        skipped_count = 0
        details = []

        for file in files:
            if not file or not file.filename:
                continue

            # Check if extension is PPT/PPTX
            ext = FileHelper.get_extension(file.filename)
            base_filename = os.path.basename(file.filename)

            if ext not in ["ppt", "pptx"]:
                skipped_count += 1
                continue # Safely skip non-PPT files in folder

            try:
                request_no = pccim_service.generate_request_no()
                apply_date = pccim_service.get_today()
                
                application, attachments = ppt_importer.import_ppt(file, request_no, apply_date)
                application.content_input_mode = "ppt"
                
                pccim_service.create_application(application)
                
                for att in attachments:
                    pccim_service.add_attachment(att)
                    
                file.seek(0)
                file.filename = base_filename
                saved_filename = FileHelper.save_attachment(
                    file=file,
                    request_no=request_no,
                    section_name="content_ppt",
                    attachment_no=1,
                )
                
                ppt_attachment = Attachment(
                    request_no=request_no,
                    section_name="content_ppt",
                    attachment_no=1,
                    file_path=saved_filename,
                    original_file_name=base_filename,
                    file_type=ext,
                    remark="Uploaded content PPT (Batch Import)",
                )
                pccim_service.add_attachment(ppt_attachment)
                    
                success_count += 1
                details.append({
                    "filename": base_filename,
                    "status": "success",
                    "request_no": request_no,
                    "message": "Successfully imported"
                })
            except Exception as e:
                app.logger.exception("Failed to import PPT %s: %s", base_filename, e)
                error_count += 1
                details.append({
                    "filename": base_filename,
                    "status": "error",
                    "request_no": "-",
                    "message": str(e)
                })

        total_processed = success_count + error_count
        batch_results = {
            "success": True,
            "total": total_processed,
            "success_count": success_count,
            "error_count": error_count,
            "skipped_count": skipped_count,
            "details": details
        }

        if total_processed == 0:
            flash(f"No valid .ppt or .pptx files were found ({skipped_count} non-PPT file(s) skipped).", "error")
        elif error_count > 0:
            flash(f"Batch import completed: {success_count} succeeded, {error_count} failed ({skipped_count} non-PPT file(s) skipped).", "error")
        else:
            flash(f"Batch import completed successfully: {success_count} PPT file(s) imported ({skipped_count} non-PPT file(s) skipped).", "success")

        return render_template("batch_upload.html", batch_results=batch_results)
        
    return render_template("batch_upload.html", batch_results=batch_results)


@app.route("/api/labels", methods=["POST"])
def create_label_api():
    name = request.json.get("name", "").strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    label = pccim_service.create_label(name)

    if not label:
        return jsonify({"error": "Label already exists or could not be created"}), 400

    return jsonify(
        {
            "id": label["id"],
            "name": label["name"],
        }
    )


@app.route("/apply", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        detail_input_mode = request.form.get("detail_input_mode", "manual").strip()

        if detail_input_mode not in ["manual", "ppt"]:
            return "Invalid detail input mode.", 400

        # =========================
        # Basic Information Validation
        # Basic Information 永遠都要填
        # =========================
        basic_required_fields = [
            "title",
            "author",
        ]

        for field in basic_required_fields:
            if not request.form.get(field, "").strip():
                return f"{field} is required.", 400

        # =========================
        # Manual Mode Validation
        # 只有 manual 模式才檢查 Problem 到 Solution
        # =========================
        if detail_input_mode == "manual":
            manual_required_fields = [
                "problem_description",
                "action_taken",
                "impact",
                "container",
                "need_help",
                "root_cause_description",
                "solution",
            ]

            for field in manual_required_fields:
                if not request.form.get(field, "").strip():
                    return f"{field} is required.", 400

        # =========================
        # PPT Upload Mode Validation
        # 只有 ppt 模式才檢查 ppt_file
        # =========================
        if detail_input_mode == "ppt":
            ppt_file = request.files.get("ppt_file")

            if not ppt_file or not ppt_file.filename:
                return "PPT file is required.", 400

            if not is_ppt_file(ppt_file.filename):
                return "Only .ppt and .pptx files are allowed for PPT Upload mode.", 400

            if not FileHelper.allowed_attachment(ppt_file.filename):
                return "PPT file type is not supported.", 400

        request_no = pccim_service.generate_request_no()
        apply_date = pccim_service.get_today()

        # =========================
        # Build Application
        # Basic Information 永遠從表單取得
        # Detail content 依照 detail_input_mode 決定
        # =========================
        if detail_input_mode == "manual":
            application = Application(
                request_no=request_no,
                apply_date=apply_date,

                title=request.form.get("title", "").strip(),
                in_dn=request.form.get("in_dn", "").strip(),
                create_date=request.form.get("create_date", "").strip(),
                close_date=request.form.get("close_date", "").strip(),
                machine_or_tool=request.form.get("machine_or_tool", "").strip(),
                module_name=request.form.get("module_name", "").strip(),
                department=request.form.get("department", "").strip(),
                author=request.form.get("author", "").strip(),

                content_input_mode="manual",

                problem_description=request.form.get("problem_description", "").strip(),
                problem_timeline=request.form.get("problem_timeline", "").strip(),

                action_taken=request.form.get("action_taken", "").strip(),

                impact=request.form.get("impact", "").strip(),

                container=request.form.get("container", "").strip(),

                need_help=request.form.get("need_help", "").strip(),

                root_cause_description=request.form.get("root_cause_description", "").strip(),
                root_cause_possible_cause=request.form.get("root_cause_possible_cause", "").strip(),
                root_cause_troubleshooting_timeline=request.form.get("root_cause_troubleshooting_timeline", "").strip(),

                solution=request.form.get("solution", "").strip(),

                implementation=request.form.get("implementation", "").strip(),

                monitoring=request.form.get("monitoring", "").strip(),

                labels=request.form.getlist("labels"),
            )

        else:
            application = Application(
                request_no=request_no,
                apply_date=apply_date,

                title=request.form.get("title", "").strip(),
                in_dn=request.form.get("in_dn", "").strip(),
                create_date=request.form.get("create_date", "").strip(),
                close_date=request.form.get("close_date", "").strip(),
                machine_or_tool=request.form.get("machine_or_tool", "").strip(),
                module_name=request.form.get("module_name", "").strip(),
                department=request.form.get("department", "").strip(),
                author=request.form.get("author", "").strip(),

                content_input_mode="ppt",

                problem_description="",
                problem_timeline="",

                action_taken="",

                impact="",

                container="",

                need_help="",

                root_cause_description="",
                root_cause_possible_cause="",
                root_cause_troubleshooting_timeline="",

                solution="",

                implementation="",

                monitoring="",

                labels=request.form.getlist("labels"),
            )

        pccim_service.create_application(application)

        # =========================
        # Save Attachments
        # =========================
        if detail_input_mode == "manual":
            for section in ATTACHMENT_SECTIONS:
                for i in range(1, Config.MAX_IMAGE_COUNT + 1):
                    file = request.files.get(f"{section}_attachment_{i}")
                    remark = request.form.get(
                        f"{section}_attachment_remark_{i}",
                        "",
                    ).strip()

                    if file and file.filename:
                        if FileHelper.allowed_attachment(file.filename):
                            saved_filename = FileHelper.save_attachment(
                                file=file,
                                request_no=request_no,
                                section_name=section,
                                attachment_no=i,
                            )

                            attachment = Attachment(
                                request_no=request_no,
                                section_name=section,
                                attachment_no=i,
                                file_path=saved_filename,
                                original_file_name=file.filename,
                                file_type=FileHelper.get_extension(file.filename),
                                remark=remark,
                            )

                            pccim_service.add_attachment(attachment)
                        else:
                            return (
                                f"{SECTION_LABELS.get(section, section)} "
                                f"attachment {i} file type is not supported."
                            ), 400

        else:
            ppt_file = request.files.get("ppt_file")

            saved_filename = FileHelper.save_attachment(
                file=ppt_file,
                request_no=request_no,
                section_name="content_ppt",
                attachment_no=1,
            )

            attachment = Attachment(
                request_no=request_no,
                section_name="content_ppt",
                attachment_no=1,
                file_path=saved_filename,
                original_file_name=ppt_file.filename,
                file_type=FileHelper.get_extension(ppt_file.filename),
                remark="Uploaded content PPT",
            )

            pccim_service.add_attachment(attachment)

        return redirect(url_for("detail", request_no=request_no))

    return render_template(
        "apply.html",
        max_image_count=Config.MAX_IMAGE_COUNT,
        attachment_sections=ATTACHMENT_SECTIONS,
        section_labels=SECTION_LABELS,
        all_labels=pccim_service.get_all_labels(),
    )


@app.route("/search")
def search():
    filters = {
        "apply_date": request.args.get("apply_date", ""),
        "title": request.args.get("title", ""),
        "in_dn": request.args.get("in_dn", ""),
        "create_date": request.args.get("create_date", ""),
        "close_date": request.args.get("close_date", ""),
        "machine_or_tool": request.args.get("machine_or_tool", ""),
        "module_name": request.args.get("module_name", ""),
        "department": request.args.get("department", ""),
        "author": request.args.get("author", ""),
        "content_input_mode": request.args.get("content_input_mode", ""),
        "label_id": request.args.get("label_id", ""),
    }

    rows = pccim_service.search_applications(filters)

    return render_template(
        "search.html",
        rows=rows,
        filters=filters,
        all_labels=pccim_service.get_all_labels(),
    )


@app.route("/detail/<request_no>")
def detail(request_no):
    application = pccim_service.get_application_by_request_no(request_no)
    attachments = pccim_service.get_attachments_by_request_no(request_no)

    if application is None:
        return "Application not found.", 404

    attachments_by_section = build_attachments_by_section(attachments)

    edit_logs = pccim_service.get_edit_logs_by_request_no(request_no)

    return render_template(
        "detail.html",
        application=application,
        attachments=attachments,
        attachments_by_section=attachments_by_section,
        attachment_sections=ATTACHMENT_SECTIONS,
        section_labels=SECTION_LABELS,
        edit_logs=edit_logs,
    )


@app.route("/edit/<request_no>", methods=["GET", "POST"])
def edit(request_no):
    application = pccim_service.get_application_by_request_no(request_no)
    attachments = pccim_service.get_attachments_by_request_no(request_no)

    if application is None:
        return "Application not found.", 404

    attachments_by_section = build_attachments_by_section(attachments)

    if request.method == "POST":
        content_input_mode = application["content_input_mode"]

        modifier_department = request.form.get("modifier_department", "").strip()
        modifier_author = request.form.get("modifier_author", "").strip()
        edit_summary = request.form.get("edit_summary", "").strip()

        if not modifier_department:
            return "Modifier Department is required.", 400

        if not modifier_author:
            return "Modifier Author is required.", 400

        basic_required_fields = [
            "title",
            "author",
        ]

        for field in basic_required_fields:
            if not request.form.get(field, "").strip():
                return f"{field} is required.", 400

        if content_input_mode == "manual":
            manual_required_fields = [
                "problem_description",
                "action_taken",
                "impact",
                "container",
                "need_help",
                "root_cause_description",
                "solution",
            ]

            for field in manual_required_fields:
                if not request.form.get(field, "").strip():
                    return f"{field} is required.", 400

        if content_input_mode == "manual":
            update_data = {
                "title": request.form.get("title", "").strip(),
                "in_dn": request.form.get("in_dn", "").strip(),
                "create_date": request.form.get("create_date", "").strip(),
                "close_date": request.form.get("close_date", "").strip(),
                "machine_or_tool": request.form.get("machine_or_tool", "").strip(),
                "module_name": request.form.get("module_name", "").strip(),
                "department": request.form.get("department", "").strip(),
                "author": request.form.get("author", "").strip(),

                "problem_description": request.form.get("problem_description", "").strip(),
                "problem_timeline": request.form.get("problem_timeline", "").strip(),

                "action_taken": request.form.get("action_taken", "").strip(),

                "impact": request.form.get("impact", "").strip(),

                "container": request.form.get("container", "").strip(),

                "need_help": request.form.get("need_help", "").strip(),

                "root_cause_description": request.form.get("root_cause_description", "").strip(),
                "root_cause_possible_cause": request.form.get("root_cause_possible_cause", "").strip(),
                "root_cause_troubleshooting_timeline": request.form.get("root_cause_troubleshooting_timeline", "").strip(),

                "solution": request.form.get("solution", "").strip(),

                "implementation": request.form.get("implementation", "").strip(),

                "monitoring": request.form.get("monitoring", "").strip(),

                "labels": request.form.getlist("labels"),
            }

        else:
            # PPT mode edit:
            # 只更新 Basic Information，不覆蓋 Problem 到 Monitoring 欄位
            update_data = {
                "title": request.form.get("title", "").strip(),
                "in_dn": request.form.get("in_dn", "").strip(),
                "create_date": request.form.get("create_date", "").strip(),
                "close_date": request.form.get("close_date", "").strip(),
                "machine_or_tool": request.form.get("machine_or_tool", "").strip(),
                "module_name": request.form.get("module_name", "").strip(),
                "department": request.form.get("department", "").strip(),
                "author": request.form.get("author", "").strip(),

                "labels": request.form.getlist("labels"),
            }

        pccim_service.update_application(request_no, update_data)

        if content_input_mode == "manual":
            for section in ATTACHMENT_SECTIONS:
                for i in range(1, Config.MAX_IMAGE_COUNT + 1):
                    file = request.files.get(f"{section}_attachment_{i}")
                    remark = request.form.get(
                        f"{section}_attachment_remark_{i}",
                        "",
                    ).strip()

                    if file and file.filename:
                        if FileHelper.allowed_attachment(file.filename):
                            saved_filename = FileHelper.save_attachment(
                                file=file,
                                request_no=request_no,
                                section_name=section,
                                attachment_no=i,
                            )

                            attachment = Attachment(
                                request_no=request_no,
                                section_name=section,
                                attachment_no=i,
                                file_path=saved_filename,
                                original_file_name=file.filename,
                                file_type=FileHelper.get_extension(file.filename),
                                remark=remark,
                            )

                            pccim_service.add_attachment(attachment)
                        else:
                            return (
                                f"{SECTION_LABELS.get(section, section)} "
                                f"attachment {i} file type is not supported."
                            ), 400

        pccim_service.add_edit_log(
            request_no=request_no,
            modifier_department=modifier_department,
            modifier_author=modifier_author,
            edit_summary=edit_summary,
        )

        return redirect(url_for("detail", request_no=request_no))

    return render_template(
        "edit.html",
        application=application,
        attachments=attachments,
        attachments_by_section=attachments_by_section,
        attachment_sections=ATTACHMENT_SECTIONS,
        section_labels=SECTION_LABELS,
        max_image_count=Config.MAX_IMAGE_COUNT,
        all_labels=pccim_service.get_all_labels(),
    )


@app.route("/export_ppt/<request_no>")
def export_ppt(request_no):
    application = pccim_service.get_application_by_request_no(request_no)
    attachments = pccim_service.get_attachments_by_request_no(request_no)

    if application is None:
        return "Application not found.", 404

    output_path = ppt_exporter.export(application, attachments)

    return send_file(
        output_path,
        as_attachment=True,
        download_name=f"{request_no}.pptx",
    )


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)


@app.route("/download_attachment/<filename>")
def download_attachment(filename):
    return send_from_directory(
        Config.UPLOAD_FOLDER,
        filename,
        as_attachment=True,
    )


# =========================
# Entry Point
# =========================
if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()