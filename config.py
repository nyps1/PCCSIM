import os
import sys


def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "pccim-secret-key"

    BASE_DIR = get_base_dir()

    DB_PATH = os.path.join(BASE_DIR, "pccim.db")

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    EXPORT_FOLDER = os.path.join(BASE_DIR, "exports")

    PPT_TEMPLATE_FOLDER = os.path.join(BASE_DIR, "ppt_templates")
    PPT_TEMPLATE_PATH = os.path.join(PPT_TEMPLATE_FOLDER, "pccim_template.pptx")

    MAX_IMAGE_COUNT = 10

    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}
    ALLOWED_PPT_EXTENSIONS = {"ppt", "pptx"}
    ALLOWED_ATTACHMENT_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_PPT_EXTENSIONS

    @staticmethod
    def init_folders():
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.EXPORT_FOLDER, exist_ok=True)
        os.makedirs(Config.PPT_TEMPLATE_FOLDER, exist_ok=True)