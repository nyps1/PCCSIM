from flask import Flask, render_template, request, redirect, url_for, send_file, send_from_directory
from config import Config

from database.db_manager import DatabaseManager
from services.pccim_service import PCCIMService
from services.ppt_exporter import PowerPointExporter
from models.application import Application
from models.attachment import Attachment
from utils.file_helper import FileHelper


app = Flask(__name__)
app.config.from_object(Config)

Config.init_folders()

db_manager = DatabaseManager(Config.DB_PATH)
db_manager.init_db()

pccim_service = PCCIMService(db_manager)
ppt_exporter = PowerPointExporter(Config.EXPORT_FOLDER)


ATTACHMENT_SECTIONS = [
    "problem",
    "action_taken",
    "container",
    "root_cause",
    "implementation",
    "monitoring",
    "solution"
]


SECTION_LABELS = {
    "problem": "Problem",
    "action_taken": "Action Taken",
    "container": "Container",
    "root_cause": "Root Cause",
    "implementation": "Implementation",
    "monitoring": "Monitoring",
    "solution": "Solution"
}


@app.route("/")
def index():
    return redirect(url_for("apply"))


@app.route("/apply", methods=["GET", "POST"])
def apply():
    if request.method == "POST":

        required_fields = [
            "title",
            "author",
            "problem_description",
            "action_taken",
            "impact",
            "container",
            "need_help",
            "root_cause_description",
            "solution",
        ]

        for field in required_fields:
            if not request.form.get(field, "").strip():
                return f"{field} 為必填欄位", 400

        request_no = pccim_service.generate_request_no()
        apply_date = pccim_service.get_today()

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

            monitoring=request.form.get("monitoring", "").strip()
        )

        pccim_service.create_application(application)

        for section in ATTACHMENT_SECTIONS:
            for i in range(1, Config.MAX_IMAGE_COUNT + 1):
                file = request.files.get(f"{section}_attachment_{i}")
                remark = request.form.get(f"{section}_attachment_remark_{i}", "").strip()

                if file and file.filename:
                    if FileHelper.allowed_attachment(file.filename):
                        saved_filename = FileHelper.save_attachment(
                            file=file,
                            request_no=request_no,
                            section_name=section,
                            attachment_no=i
                        )

                        attachment = Attachment(
                            request_no=request_no,
                            section_name=section,
                            attachment_no=i,
                            file_path=saved_filename,
                            original_file_name=file.filename,
                            file_type=FileHelper.get_extension(file.filename),
                            remark=remark
                        )

                        pccim_service.add_attachment(attachment)
                    else:
                        return f"{SECTION_LABELS.get(section, section)} 附件 {i} 檔案格式不支援，請上傳圖片或 PowerPoint。", 400

        return redirect(url_for("detail", request_no=request_no))

    return render_template(
        "apply.html",
        max_image_count=Config.MAX_IMAGE_COUNT,
        attachment_sections=ATTACHMENT_SECTIONS,
        section_labels=SECTION_LABELS
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
        "author": request.args.get("author", "")
    }

    rows = pccim_service.search_applications(filters)

    return render_template(
        "search.html",
        rows=rows,
        filters=filters
    )


@app.route("/detail/<request_no>")
def detail(request_no):
    application = pccim_service.get_application_by_request_no(request_no)
    attachments = pccim_service.get_attachments_by_request_no(request_no)

    if application is None:
        return "找不到此申請單", 404

    attachments_by_section = {}

    for section in ATTACHMENT_SECTIONS:
        attachments_by_section[section] = []

    for attachment in attachments:
        section_name = attachment["section_name"]

        if section_name not in attachments_by_section:
            attachments_by_section[section_name] = []

        attachments_by_section[section_name].append(attachment)

    return render_template(
        "detail.html",
        application=application,
        attachments=attachments,
        attachments_by_section=attachments_by_section,
        attachment_sections=ATTACHMENT_SECTIONS,
        section_labels=SECTION_LABELS
    )


@app.route("/export_ppt/<request_no>")
def export_ppt(request_no):
    application = pccim_service.get_application_by_request_no(request_no)
    attachments = pccim_service.get_attachments_by_request_no(request_no)

    if application is None:
        return "找不到此申請單", 404

    output_path = ppt_exporter.export(application, attachments)

    return send_file(
        output_path,
        as_attachment=True,
        download_name=f"{request_no}.pptx"
    )


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)


@app.route("/download_attachment/<filename>")
def download_attachment(filename):
    return send_from_directory(
        Config.UPLOAD_FOLDER,
        filename,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)