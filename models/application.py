class Application:
    def __init__(
        self,
        request_no,
        apply_date,
        title,
        in_dn,
        create_date,
        close_date,
        machine,
        module_name,
        tmn,
        department,
        author,
        problem_description,
        action_taken,
        impact_container,
        need_help,
        root_cause,
        solution
    ):
        self.request_no = request_no
        self.apply_date = apply_date
        self.title = title
        self.in_dn = in_dn
        self.create_date = create_date
        self.close_date = close_date
        self.machine = machine
        self.module_name = module_name
        self.tmn = tmn
        self.department = department
        self.author = author
        self.problem_description = problem_description
        self.action_taken = action_taken
        self.impact_container = impact_container
        self.need_help = need_help
        self.root_cause = root_cause
        self.solution = solution

    def to_tuple(self):
        return (
            self.request_no,
            self.apply_date,
            self.title,
            self.in_dn,
            self.create_date,
            self.close_date,
            self.machine,
            self.module_name,
            self.tmn,
            self.department,
            self.author,
            self.problem_description,
            self.action_taken,
            self.impact_container,
            self.need_help,
            self.root_cause,
            self.solution
        )