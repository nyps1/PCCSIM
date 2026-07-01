class Attachment:
    def __init__(self, request_no, image_no, file_path, remark):
        self.request_no = request_no
        self.image_no = image_no
        self.file_path = file_path
        self.remark = remark

    def to_tuple(self):
        return (
            self.request_no,
            self.image_no,
            self.file_path,
            self.remark
        )