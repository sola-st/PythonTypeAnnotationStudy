class CodeChange:
    """Code change class"""

    def __init__(self, url, commit_year, old_file, old_line, old_code, new_file, new_line, new_code):
        self.url = url
        self.commit_year = commit_year

        self.old_file = old_file
        self.old_line = old_line
        self.old_code = old_code

        self.new_line = new_line
        self.new_file = new_file
        self.new_code = new_code

    def __members(self):
        return self.url, self.commit_year, self.old_file, self.old_line, self.old_code, self.new_file, self.new_line, self.new_code

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__members() == other.__members()
        else:
            return False

    def __hash__(self):
        return hash(self.__members())
