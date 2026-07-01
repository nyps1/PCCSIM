import os
from werkzeug.utils import secure_filename
from config import Config


class FileHelper:
    @staticmethod
    def get_extension(filename):
        if not filename or "." not in filename:
            return ""

        return filename.rsplit(".", 1)[1].lower()

    @staticmethod
    def allowed_attachment(filename):
        ext = FileHelper.get_extension(filename)
        return ext in Config.ALLOWED_ATTACHMENT_EXTENSIONS

    @staticmethod
    def is_image(filename):
        ext = FileHelper.get_extension(filename)
        return ext in Config.ALLOWED_IMAGE_EXTENSIONS

    @staticmethod
    def is_powerpoint(filename):
        ext = FileHelper.get_extension(filename)
        return ext in Config.ALLOWED_PPT_EXTENSIONS

    @staticmethod
    def save_attachment(file, request_no, attachment_no):
        original_filename = secure_filename(file.filename)
        filename = f"{request_no}_{attachment_no}_{original_filename}"
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)

        file.save(file_path)

        return filename