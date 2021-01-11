class CodeChange:
    """Code change class"""

    def __init__(self, url_creation, url_deletion, url_last_change, commit_year, creation_date, elimination_date, life_time, change_num, where, type, variable, old_file, old_annotation, old_line,  new_file, new_annotation, new_line):
        self.url_creation = url_creation
        self.url_last_change = url_last_change
        self.url_deletion = url_deletion

        self.commit_year = commit_year
        self.creation_date = creation_date
        self.elimination_date = elimination_date
        self.life_time = life_time
        self.change_num = change_num
        self.type = type
        self.where = where
        self.variable = variable

        self.old_file = old_file
        self.old_annotation = old_annotation
        self.old_line = old_line

        self.new_file = new_file
        self.new_annotation = new_annotation
        self.new_line = new_line

    def __members(self):
        return self.url, self.commit_year, self.old_file, self.where, self.old_annotation, self.type, self.new_file, self.new_annotation, self.new_line

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__members() == other.__members()
        else:
            return False

    def __hash__(self):
        return hash(self.__members())


class CommitStatistics:
    """CommitStatistics class"""

    def __init__(self, url, commit_year, number_type_annotations_code_changes, added_per_commit_percentage,
                 removed_per_commit_percentage, changed_per_commit_percentage, typeannotation_line_inserted,
                 typeannotation_line_removed, typeannotation_line_changed):
        self.url = url
        self.commit_year = commit_year
        self.number_type_annotations_code_changes = number_type_annotations_code_changes

        self.added_per_commit_percentage = added_per_commit_percentage
        self.removed_per_commit_percentage = removed_per_commit_percentage
        self.changed_per_commit_percentage = changed_per_commit_percentage

        self.typeannotation_line_inserted = typeannotation_line_inserted
        self.typeannotation_line_removed = typeannotation_line_removed
        self.typeannotation_line_changed = typeannotation_line_changed

    def __members(self):
        return self.url, self.commit_year, self.number_type_annotations_code_changes, self.added_per_commit_percentage, self.removed_per_commit_percentage, self.changed_per_commit_percentage, self.typeannotation_line_inserted, self.typeannotation_line_removed, self.typeannotation_line_changed

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__members() == other.__members()
        else:
            return False

    def __hash__(self):
        return hash(self.__members())


class SingleDiffChange:
    """Single Diff class"""

    def __init__(self, type, old_or_new, filename, variable, annotation, line):
        self.type = type
        self.old_or_new = old_or_new
        self.filename = filename
        self.variable = variable

        self.annotation = annotation
        self.line = line

    def __members(self):
        return self.type, self.old_or_new, self.variable, self.annotation, self.line

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__members() == other.__members()
        else:
            return False

    def __hash__(self):
        return hash(self.__members())
