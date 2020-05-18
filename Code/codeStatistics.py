class CodeStatistics:
    """Code change class"""

    def __init__(self):
        self.execution_time = ''
        self.total_repositories = 0
        self.total_commits = 0
        self.commits_with_typeChanges = 0
        self.percentage_commits_with_typeChanges = ''

        self.total_typeAnnotation_codeChanges = 0

        self.insert_types = 0
        self.percentage_insert_types = ''
        self.remove_types = 0
        self.percentage_remove_types = ''
        self.modify_existing_types = 0
        self.percentage_modify_existing_types = ''

    def percentageComputation(self):
        self.total_typeAnnotation_codeChanges = self.insert_types + self.remove_types + self.modify_existing_types

        self.percentage_commits_with_typeChanges = str(self.commits_with_typeChanges/self.total_commits*100) + ' %'
        self.percentage_insert_types = str(round(self.insert_types/self.total_typeAnnotation_codeChanges*100,1)) + ' %'
        self.percentage_remove_types = str(round(self.remove_types / self.total_typeAnnotation_codeChanges*100,1)) + ' %'
        self.percentage_modify_existing_types = str(round(self.modify_existing_types / self.total_typeAnnotation_codeChanges*100,1)) + ' %'


