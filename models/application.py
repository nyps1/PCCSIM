from typing import Tuple

class Application:
    """
    Application 資料模型
    
    [設計模式約束]
    本類別實作了 Data Transfer Object (DTO) 模式。
    它負責封裝並攜帶表單提交的資料，從 Controller (app.py) 傳遞至 Service (pccim_service.py)。
    透過強制使用強型別 (Type Hints)，能大幅降低傳遞過程中的資料遺失與型別錯亂問題。
    """
    def __init__(
        self,
        request_no: str,
        apply_date: str,
        title: str,
        in_dn: str,
        create_date: str,
        close_date: str,
        machine_or_tool: str,
        module_name: str,
        department: str,
        author: str,

        content_input_mode: str,

        problem_description: str,
        problem_timeline: str,

        action_taken: str,

        impact: str,

        container: str,

        need_help: str,

        root_cause_description: str,
        root_cause_possible_cause: str,
        root_cause_troubleshooting_timeline: str,

        solution: str,

        implementation: str,

        monitoring: str
    ) -> None:
        self.request_no = request_no
        self.apply_date = apply_date

        self.title = title
        self.in_dn = in_dn
        self.create_date = create_date
        self.close_date = close_date
        self.machine_or_tool = machine_or_tool
        self.module_name = module_name
        self.department = department
        self.author = author

        self.content_input_mode = content_input_mode

        self.problem_description = problem_description
        self.problem_timeline = problem_timeline

        self.action_taken = action_taken

        self.impact = impact

        self.container = container

        self.need_help = need_help

        self.root_cause_description = root_cause_description
        self.root_cause_possible_cause = root_cause_possible_cause
        self.root_cause_troubleshooting_timeline = root_cause_troubleshooting_timeline

        self.solution = solution

        self.implementation = implementation

        self.monitoring: str = monitoring

    def to_tuple(self) -> Tuple[str, ...]:
        return (
            self.request_no,
            self.apply_date,

            self.title,
            self.in_dn,
            self.create_date,
            self.close_date,
            self.machine_or_tool,
            self.module_name,
            self.department,
            self.author,

            self.content_input_mode,

            self.problem_description,
            self.problem_timeline,

            self.action_taken,

            self.impact,

            self.container,

            self.need_help,

            self.root_cause_description,
            self.root_cause_possible_cause,
            self.root_cause_troubleshooting_timeline,

            self.solution,

            self.implementation,

            self.monitoring
        )