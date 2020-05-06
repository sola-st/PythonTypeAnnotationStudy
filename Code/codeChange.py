
class CodeChange:
    """Code change class"""

    def __init__(self, url, old_file, old_line, old_code, new_file, new_line, new_code):
        self.url = url

        self.old_file = old_file
        self.old_line = old_line
        self.old_code = old_code

        self.new_line = new_line
        self.new_file = new_file
        self.new_code = new_code

