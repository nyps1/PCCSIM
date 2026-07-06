class Application:
    def __init__(
        self,
        request_no,
        apply_date,
        title,
        in_dn,
        create_date,
        close_date,
        machine_or_tool,
        module_name,
        department,
        author,

        content_input_mode,

        problem_description,
        problem_timeline,

        action_taken,

        impact,

        container,

        need_help,

        root_cause_description,
        root_cause_possible_cause,
        root_cause_troubleshooting_timeline,

        solution,

        implementation,

        monitoring
    ):
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

        self.monitoring = monitoring

    def to_tuple(self):
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