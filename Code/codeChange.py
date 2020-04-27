
class CodeChange:
    """Code change class"""

    def __init__(self, commit, line, old_code, new_code):
        self.commit = commit
        self.line = line
        self.old_code = old_code
        self.new_code = new_code



    def func(self):
        print('Hello')
