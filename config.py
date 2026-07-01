import os


class Config:
    SECRET_KEY = "pccim-secret-key"

    DB_PATH = "pccim.db"

    UPLOAD_FOLDER = "uploads"
    EXPORT_FOLDER = "exports"

    MAX_IMAGE_COUNT = 10

    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}
    ALLOWED_PPT_EXTENSIONS = {"ppt", "pptx"}

    ALLOWED_ATTACHMENT_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_PPT_EXTENSIONS

    @staticmethod
    def init_folders():
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.EXPORT_FOLDER, exist_ok=True)