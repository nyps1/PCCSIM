import os
from pptx import Presentation
from pptx.util import Inches, Pt
from config import Config

try:
    from PIL import Image
except ImportError:
    Image = None


class PowerPointExporter:
    IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
    PPT_EXTS = {".ppt", ".pptx"}

    SECTION_LABELS = {
        "problem": "Problem",
        "container": "Container",
        "root_cause": "Root Cause",
        "solution": "Solution",
        "implementation": "Implementation",
        "monitoring": "Monitoring"
    }

    def __init__(self, export_folder):
        self.export_folder = export_folder
        os.makedirs(self.export_folder, exist_ok=True)

    def export(self, application, attachments):
        template_path = getattr(Config, "PPT_TEMPLATE_PATH", "")

        if template_path and os.path.exists(template_path):
            prs = Presentation(template_path)
        else:
            prs = Presentation()
            prs.slide_width = Inches(13.333)
            prs.slide_height = Inches(7.5)

        attachments_by_section = self._group_attachments_by_section(attachments)

        mapping = self._build_placeholder_mapping(
            application=application,
            attachments_by_section=attachments_by_section
        )

        self._replace_placeholders_in_presentation(prs, mapping)

        self._add_image_attachment_slides(prs, attachments_by_section)
        self._add_file_attachment_summary_slide(prs, attachments)

        output_path = os.path.join(
            self.export_folder,
            f"{self._value(application, 'request_no')}.pptx"
        )

        prs.save(output_path)

        return output_path

    # --------------------------------------------------
    # Basic helpers
    # --------------------------------------------------

    def _value(self, row, key, default=""):
        try:
            value = row[key]
            return value if value is not None else default
        except Exception:
            return default

    def _get_safe_layout(self, prs):
        if len(prs.slide_layouts) == 0:
            return None

        if len(prs.slide_layouts) > 6:
            return prs.slide_layouts[6]

        return prs.slide_layouts[len(prs.slide_layouts) - 1]

    def _add_slide(self, prs):
        layout = self._get_safe_layout(prs)

        if layout is not None:
            return prs.slides.add_slide(layout)

        return prs.slides.add_slide(prs.slide_layouts[0])

    def _add_title(self, slide, title):
        title_box = slide.shapes.add_textbox(
            Inches(0.5),
            Inches(0.25),
            Inches(12.3),
            Inches(0.45)
        )

        frame = title_box.text_frame
        frame.text = title

        paragraph = frame.paragraphs[0]
        paragraph.font.size = Pt(24)
        paragraph.font.bold = True

    def _add_textbox(self, slide, text, left, top, width, height, font_size=14):
        box = slide.shapes.add_textbox(left, top, width, height)
        frame = box.text_frame
        frame.word_wrap = True
        frame.text = text or ""

        for paragraph in frame.paragraphs:
            paragraph.font.size = Pt(font_size)

        return box

    # --------------------------------------------------
    # Placeholder mapping
    # --------------------------------------------------

    def _build_placeholder_mapping(self, application, attachments_by_section):
        mapping = {
            "{{REQUEST_NO}}": self._value(application, "request_no"),
            "{{APPLY_DATE}}": self._value(application, "apply_date"),

            "{{TITLE}}": self._value(application, "title"),
            "{{IN_DN}}": self._value(application, "in_dn"),
            "{{CREATE_DATE}}": self._value(application, "create_date"),
            "{{CLOSE_DATE}}": self._value(application, "close_date"),
            "{{MACHINE_OR_TOOL}}": self._value(application, "machine_or_tool"),
            "{{MODULE_NAME}}": self._value(application, "module_name"),
            "{{DEPARTMENT}}": self._value(application, "department"),
            "{{AUTHOR}}": self._value(application, "author"),

            "{{PROBLEM_DESCRIPTION}}": self._value(application, "problem_description"),
            "{{PROBLEM_TIMELINE}}": self._value(application, "problem_timeline"),

            "{{ACTION_TAKEN}}": self._value(application, "action_taken"),

            "{{IMPACT}}": self._value(application, "impact"),

            "{{CONTAINER}}": self._value(application, "container"),

            "{{NEED_HELP}}": self._value(application, "need_help"),

            "{{ROOT_CAUSE_DESCRIPTION}}": self._value(application, "root_cause_description"),
            "{{ROOT_CAUSE_POSSIBLE_CAUSE}}": self._value(application, "root_cause_possible_cause"),
            "{{ROOT_CAUSE_TROUBLESHOOTING_TIMELINE}}": self._value(application, "root_cause_troubleshooting_timeline"),

            "{{SOLUTION}}": self._value(application, "solution"),

            "{{IMPLEMENTATION}}": self._value(application, "implementation"),

            "{{MONITORING}}": self._value(application, "monitoring")
        }

        for section_key, section_title in self.SECTION_LABELS.items():
            placeholder = "{{" + section_key.upper() + "_ATTACHMENT_LIST}}"
            mapping[placeholder] = self._build_attachment_text_list(
                attachments_by_section.get(section_key, [])
            )

        mapping["{{ALL_ATTACHMENT_LIST}}"] = self._build_all_attachment_text_list(
            attachments_by_section
        )

        return mapping

    def _build_attachment_text_list(self, attachments):
        if not attachments:
            return "No attachment."

        lines = []

        for attachment in attachments:
            attachment_no = self._value(attachment, "attachment_no")
            original_file_name = self._value(attachment, "original_file_name")
            file_path = self._value(attachment, "file_path")
            remark = self._value(attachment, "remark")

            lines.append(
                f"Attachment {attachment_no}: {original_file_name or file_path}\n"
                f"Remark: {remark or ''}"
            )

        return "\n\n".join(lines)

    def _build_all_attachment_text_list(self, attachments_by_section):
        lines = []

        for section_key, attachments in attachments_by_section.items():
            section_title = self.SECTION_LABELS.get(section_key, section_key)

            if not attachments:
                continue

            lines.append(f"[{section_title}]")

            for attachment in attachments:
                attachment_no = self._value(attachment, "attachment_no")
                original_file_name = self._value(attachment, "original_file_name")
                file_path = self._value(attachment, "file_path")
                remark = self._value(attachment, "remark")

                lines.append(
                    f"Attachment {attachment_no}: {original_file_name or file_path}\n"
                    f"Remark: {remark or ''}"
                )

            lines.append("")

        if not lines:
            return "No attachment."

        return "\n".join(lines)

    # --------------------------------------------------
    # Replace placeholders in template
    # --------------------------------------------------

    def _replace_placeholders_in_presentation(self, prs, mapping):
        for slide in prs.slides:
            self._replace_placeholders_in_shapes(slide.shapes, mapping)

    def _replace_placeholders_in_shapes(self, shapes, mapping):
        for shape in shapes:
            if shape.has_text_frame:
                self._replace_placeholders_in_text_frame(shape.text_frame, mapping)

            if getattr(shape, "has_table", False):
                if shape.has_table:
                    self._replace_placeholders_in_table(shape.table, mapping)

            if hasattr(shape, "shapes"):
                self._replace_placeholders_in_shapes(shape.shapes, mapping)

    def _replace_placeholders_in_table(self, table, mapping):
        for row in table.rows:
            for cell in row.cells:
                self._replace_placeholders_in_text_frame(cell.text_frame, mapping)

    def _replace_placeholders_in_text_frame(self, text_frame, mapping):
        for paragraph in text_frame.paragraphs:
            replaced_by_run = False

            for run in paragraph.runs:
                original_text = run.text
                new_text = original_text

                for key, value in mapping.items():
                    if key in new_text:
                        new_text = new_text.replace(key, str(value or ""))

                if new_text != original_text:
                    run.text = new_text
                    replaced_by_run = True

            paragraph_text = paragraph.text
            new_paragraph_text = paragraph_text

            for key, value in mapping.items():
                if key in new_paragraph_text:
                    new_paragraph_text = new_paragraph_text.replace(key, str(value or ""))

            if new_paragraph_text != paragraph_text and not replaced_by_run:
                paragraph.text = new_paragraph_text

    # --------------------------------------------------
    # Attachment processing
    # --------------------------------------------------

    def _group_attachments_by_section(self, attachments):
        result = {}

        for section_key in self.SECTION_LABELS.keys():
            result[section_key] = []

        for attachment in attachments:
            section_name = self._value(attachment, "section_name", "others")

            if section_name not in result:
                result[section_name] = []

            result[section_name].append(attachment)

        return result

    def _is_image_attachment(self, attachment):
        file_path = self._value(attachment, "file_path").lower()
        return any(file_path.endswith(ext) for ext in self.IMAGE_EXTS)

    def _is_ppt_attachment(self, attachment):
        file_path = self._value(attachment, "file_path").lower()
        return any(file_path.endswith(ext) for ext in self.PPT_EXTS)

    def _get_attachment_full_path(self, attachment):
        return os.path.join(
            Config.UPLOAD_FOLDER,
            self._value(attachment, "file_path")
        )

    # --------------------------------------------------
    # Image attachment slides
    # --------------------------------------------------

    def _add_image_attachment_slides(self, prs, attachments_by_section):
        for section_key, attachments in attachments_by_section.items():
            image_attachments = [
                attachment for attachment in attachments
                if self._is_image_attachment(attachment)
            ]

            if not image_attachments:
                continue

            section_title = self.SECTION_LABELS.get(section_key, section_key)

            for i in range(0, len(image_attachments), 2):
                slide = self._add_slide(prs)
                self._add_title(slide, f"{section_title} Attachments")

                page_attachments = image_attachments[i:i + 2]

                positions = [
                    {
                        "img_left": Inches(0.7),
                        "img_top": Inches(1.05),
                        "img_width": Inches(5.7),
                        "img_height": Inches(4.45),
                        "text_left": Inches(0.7),
                        "text_top": Inches(5.6)
                    },
                    {
                        "img_left": Inches(6.9),
                        "img_top": Inches(1.05),
                        "img_width": Inches(5.7),
                        "img_height": Inches(4.45),
                        "text_left": Inches(6.9),
                        "text_top": Inches(5.6)
                    }
                ]

                for index, attachment in enumerate(page_attachments):
                    pos = positions[index]

                    image_path = self._get_attachment_full_path(attachment)

                    if os.path.exists(image_path):
                        self._add_picture_fit(
                            slide=slide,
                            image_path=image_path,
                            left=pos["img_left"],
                            top=pos["img_top"],
                            max_width=pos["img_width"],
                            max_height=pos["img_height"]
                        )

                    attachment_no = self._value(attachment, "attachment_no")
                    original_file_name = self._value(attachment, "original_file_name")
                    remark = self._value(attachment, "remark")

                    remark_text = (
                        f"Attachment {attachment_no}\n"
                        f"File: {original_file_name or self._value(attachment, 'file_path')}\n"
                        f"Remark: {remark or ''}"
                    )

                    self._add_textbox(
                        slide=slide,
                        text=remark_text,
                        left=pos["text_left"],
                        top=pos["text_top"],
                        width=Inches(5.7),
                        height=Inches(1.2),
                        font_size=11
                    )

    def _add_picture_fit(self, slide, image_path, left, top, max_width, max_height):
        if Image is None:
            slide.shapes.add_picture(
                image_path,
                left,
                top,
                width=max_width
            )
            return

        with Image.open(image_path) as img:
            img_width, img_height = img.size

        if img_width <= 0 or img_height <= 0:
            return

        max_w = int(max_width)
        max_h = int(max_height)

        image_ratio = img_width / img_height
        box_ratio = max_w / max_h

        if image_ratio >= box_ratio:
            display_width = max_w
            display_height = int(max_w / image_ratio)
        else:
            display_height = max_h
            display_width = int(max_h * image_ratio)

        slide.shapes.add_picture(
            image_path,
            left,
            top,
            width=display_width,
            height=display_height
        )

    # --------------------------------------------------
    # PPT / other attachment summary
    # --------------------------------------------------

    def _add_file_attachment_summary_slide(self, prs, attachments):
        file_attachments = [
            attachment for attachment in attachments
            if not self._is_image_attachment(attachment)
        ]

        if not file_attachments:
            return

        slide = self._add_slide(prs)
        self._add_title(slide, "File Attachments Summary")

        lines = []

        for attachment in file_attachments:
            section_name = self._value(attachment, "section_name")
            section_title = self.SECTION_LABELS.get(section_name, section_name)

            attachment_no = self._value(attachment, "attachment_no")
            original_file_name = self._value(attachment, "original_file_name")
            file_path = self._value(attachment, "file_path")
            file_type = self._value(attachment, "file_type")
            remark = self._value(attachment, "remark")

            lines.append(
                f"[{section_title}] Attachment {attachment_no}\n"
                f"File: {original_file_name or file_path}\n"
                f"Type: {file_type}\n"
                f"Remark: {remark or ''}\n"
            )

        self._add_textbox(
            slide=slide,
            text="\n".join(lines),
            left=Inches(0.7),
            top=Inches(1.1),
            width=Inches(12),
            height=Inches(5.9),
            font_size=13
        )