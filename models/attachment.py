from typing import Tuple, Optional

class Attachment:
    """
    Attachment 附件資料模型
    
    [設計模式約束]
    本類別實作了 Data Transfer Object (DTO) 模式。
    它負責封裝並攜帶每個上傳附件的詳細資訊，從 Controller (app.py) 傳遞至 Service (pccim_service.py) 與 PPT Exporter。
    透過強制使用強型別 (Type Hints)，能大幅降低傳遞過程中的資料遺失與型別錯亂問題。
    """
    def __init__(
        self,
        request_no: str,
        section_name: str,
        attachment_no: int,
        file_path: str,
        original_file_name: str,
        file_type: str,
        remark: Optional[str]
    ) -> None:
        self.request_no = request_no
        self.section_name = section_name
        self.attachment_no = attachment_no
        self.file_path = file_path
        self.original_file_name = original_file_name
        self.file_type = file_type
        self.remark = remark

    def to_tuple(self) -> Tuple[str, str, int, str, str, str, Optional[str]]:
        return (
            self.request_no,
            self.section_name,
            self.attachment_no,
            self.file_path,
            self.original_file_name,
            self.file_type,
            self.remark
        )