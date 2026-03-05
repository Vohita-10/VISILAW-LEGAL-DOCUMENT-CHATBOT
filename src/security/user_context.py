class UserContext:
    def __init__(self, user_id, department, clearance, projects=None):
        self.user_id = user_id
        self.department = department
        self.clearance = clearance
        self.projects = projects or []

