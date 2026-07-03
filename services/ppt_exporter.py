import os
from pptx import Presentation
from pptx.util import Inches, Pt
from config import Config


class PowerPointExporter:
    def __init__(self, export_folder):
        self.export_folder = export_folder
        os.makedirs(self.export_folder, exist_ok=True)

    def export(self, application, attachments):
        prs = Presentation(Config.PPT_TEMPLATE_PATH)
        
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

        self._add_basic_info_slide(prs, application)
        self._add_detail_slide(prs, application)
        self._add_attachment_slides(prs, attachments)

        output_path = os.path.join(
            self.export_folder,
            f"{application['request_no']}.pptx"
        )

        prs.save(output_path)

        return output_path

    def _add_title(self, slide, title):
        title_box = slide.shapes.add_textbox(
            Inches(0.5),
            Inches(0.3),
            Inches(12),
            Inches(0.5)
        )

        frame = title_box.text_frame
        frame.text = title

        paragraph = frame.paragraphs[0]
        paragraph.font.size = Pt(26)
        paragraph.font.bold = True

    def _add_basic_info_slide(self, prs, application):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_title(slide, "PCCIM Application Report")

        info_text = f"""
            Request No: {application['request_no']}
            Apply Date: {application['apply_date']}
            Title: {application['title']}
            IN/DN: {application['in_dn']}
            Create Date: {application['create_date']}
            Close Date: {application['close_date']}
            Machine/Tool: {application['machine']}
            TMN: {application['tmn']}
            Module Name: {application['module_name']}
            Department: {application['department']}
            Author: {application['author']}
            """

        box = slide.shapes.add_textbox(
            Inches(0.7),
            Inches(1.1),
            Inches(12),
            Inches(5.8)
        )

        frame = box.text_frame
        frame.word_wrap = True
        frame.text = info_text

        for paragraph in frame.paragraphs:
            paragraph.font.size = Pt(18)

    def _add_detail_slide(self, prs, application):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_title(slide, "PCCIM Detail")

        detail_text = f"""
Problem Description:
{application['problem_description'] or ''}

Action Taken:
{application['action_taken'] or ''}

Impact Container:
{application['impact_container'] or ''}

Need Help From PE/DE:
{application['need_help'] or ''}

Root Cause:
{application['root_cause'] or ''}

Solution:
{application['solution'] or ''}
"""

        box = slide.shapes.add_textbox(
            Inches(0.7),
            Inches(1.0),
            Inches(12),
            Inches(6.2)
        )

        frame = box.text_frame
        frame.word_wrap = True
        frame.text = detail_text

        for paragraph in frame.paragraphs:
            paragraph.font.size = Pt(13)

    def _add_attachment_slides(self, prs, attachments):
        if not attachments:
            return

        image_attachments = []
        ppt_attachments = []

        image_exts = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
        ppt_exts = {".ppt", ".pptx"}

        for attachment in attachments:
            filename = attachment["file_path"].lower()

            if any(filename.endswith(ext) for ext in image_exts):
                image_attachments.append(attachment)
            elif any(filename.endswith(ext) for ext in ppt_exts):
                ppt_attachments.append(attachment)

        for i in range(0, len(image_attachments), 2):
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            self._add_title(slide, "Attachment Images")

            page_attachments = image_attachments[i:i + 2]

            positions = [
                {
                    "img_left": Inches(0.7),
                    "img_top": Inches(1.1),
                    "img_width": Inches(5.7),
                    "remark_left": Inches(0.7),
                    "remark_top": Inches(5.8)
                },
                {
                    "img_left": Inches(6.9),
                    "img_top": Inches(1.1),
                    "img_width": Inches(5.7),
                    "remark_left": Inches(6.9),
                    "remark_top": Inches(5.8)
                }
            ]

            for index, attachment in enumerate(page_attachments):
                pos = positions[index]

                image_path = os.path.join(
                    Config.UPLOAD_FOLDER,
                    attachment["file_path"]
                )

                if os.path.exists(image_path):
                    slide.shapes.add_picture(
                        image_path,
                        pos["img_left"],
                        pos["img_top"],
                        width=pos["img_width"]
                    )

                remark_box = slide.shapes.add_textbox(
                    pos["remark_left"],
                    pos["remark_top"],
                    Inches(5.7),
                    Inches(1.1)
                )

                remark_frame = remark_box.text_frame
                remark_frame.word_wrap = True
                remark_frame.text = (
                    f"Attachment {attachment['image_no']} Remark: "
                    f"{attachment['remark'] or ''}"
                )

                for paragraph in remark_frame.paragraphs:
                    paragraph.font.size = Pt(13)

        if ppt_attachments:
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            self._add_title(slide, "PowerPoint Attachments")

            text_lines = []

            for attachment in ppt_attachments:
                text_lines.append(
                    f"Attachment {attachment['image_no']}: {attachment['file_path']}\n"
                    f"Remark: {attachment['remark'] or ''}\n"
                )

            box = slide.shapes.add_textbox(
                Inches(0.7),
                Inches(1.1),
                Inches(12),
                Inches(5.8)
            )

            frame = box.text_frame
            frame.word_wrap = True
            frame.text = "\n".join(text_lines)

            for paragraph in frame.paragraphs:
                paragraph.font.size = Pt(16)