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


@app.route("/")
def index():
    return redirect(url_for("apply"))


@app.route("/apply", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        request_no = pccim_service.generate_request_no()
        apply_date = pccim_service.get_today()

        application = Application(
            request_no=request_no,
            apply_date=apply_date,
            title=request.form.get("title"),
            in_dn=request.form.get("in_dn"),
            create_date=request.form.get("create_date"),
            close_date=request.form.get("close_date"),
            machine=request.form.get("machine"),
            module_name=request.form.get("module_name"),
            department=request.form.get("department"),
            author=request.form.get("author"),
            problem_description=request.form.get("problem_description"),
            action_taken=request.form.get("action_taken"),
            impact_container=request.form.get("impact_container"),
            need_help=request.form.get("need_help"),
            root_cause=request.form.get("root_cause"),
            solution=request.form.get("solution")
        )

        pccim_service.create_application(application)

        for i in range(1, Config.MAX_IMAGE_COUNT + 1):
            file = request.files.get(f"attachment_{i}")
            remark = request.form.get(f"attachment_remark_{i}")

            if file and file.filename:
                if FileHelper.allowed_attachment(file.filename):
                    saved_filename = FileHelper.save_attachment(
                        file=file,
                        request_no=request_no,
                        attachment_no=i
                    )

                    attachment = Attachment(
                        request_no=request_no,
                        image_no=i,
                        file_path=saved_filename,
                        remark=remark
                    )

                    pccim_service.add_attachment(attachment)

    return render_template("apply.html", max_image_count=Config.MAX_IMAGE_COUNT)


@app.route("/search")
def search():
    filters = {
        "apply_date": request.args.get("apply_date", ""),
        "title": request.args.get("title", ""),
        "in_dn": request.args.get("in_dn", ""),
        "create_date": request.args.get("create_date", ""),
        "close_date": request.args.get("close_date", ""),
        "machine": request.args.get("machine", ""),
        "module_name": request.args.get("module_name", ""),
        "department": request.args.get("department", ""),
        "author": request.args.get("author", "")
    }

    rows = pccim_service.search_applications(filters)

    return render_template("search.html", rows=rows, filters=filters)


@app.route("/detail/<request_no>")
def detail(request_no):
    application = pccim_service.get_application_by_request_no(request_no)
    attachments = pccim_service.get_attachments_by_request_no(request_no)

    if application is None:
        return "找不到此申請單", 404

    return render_template(
        "detail.html",
        application=application,
        attachments=attachments
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