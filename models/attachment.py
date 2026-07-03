class Attachment:
    def __init__(
        self,
        request_no,
        section_name,
        attachment_no,
        file_path,
        original_file_name,
        file_type,
        remark
    ):
        self.request_no = request_no
        self.section_name = section_name
        self.attachment_no = attachment_no
        self.file_path = file_path
        self.original_file_name = original_file_name
        self.file_type = file_type
        self.remark = remark

    def to_tuple(self):
        return (
            self.request_no,
            self.section_name,
            self.attachment_no,
            self.file_path,
            self.original_file_name,
            self.file_type,
            self.remark
        )