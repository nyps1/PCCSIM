import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from config import Config
from typing import Any

class FileHelper:
    """
    檔案處理工具類別
    
    [設計模式約束]
    本類別採用 Static Method (靜態方法) 模式設計，用於封裝與狀態無關的純邏輯運算（Pure Functions）。
    """
    @staticmethod
    def get_extension(filename: str) -> str:
        if not filename or "." not in filename:
            return ""

        return filename.rsplit(".", 1)[1].lower()

    @staticmethod
    def allowed_attachment(filename: str) -> bool:
        ext = FileHelper.get_extension(filename)
        return ext in Config.ALLOWED_ATTACHMENT_EXTENSIONS

    @staticmethod
    def is_image(filename: str) -> bool:
        ext = FileHelper.get_extension(filename)
        return ext in Config.ALLOWED_IMAGE_EXTENSIONS

    @staticmethod
    def is_powerpoint(filename: str) -> bool:
        ext = FileHelper.get_extension(filename)
        return ext in Config.ALLOWED_PPT_EXTENSIONS

    @staticmethod
    def save_attachment(file: Any, request_no: str, section_name: str, attachment_no: int) -> str:
        original_filename = secure_filename(file.filename)

        filename = f"{request_no}_{section_name}_{attachment_no}_{original_filename}"

        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)

        file.save(file_path)

        return filename