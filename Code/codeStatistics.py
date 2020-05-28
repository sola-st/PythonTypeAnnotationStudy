import multiprocessing
import platform


class CodeStatistics:
    """Code change class"""

    def __init__(self):
        self.execution_time = ''
        self.machine = {'OS': platform.platform(), 'CPU': platform.processor(), 'CORES': multiprocessing.cpu_count()}
        self.total_repositories = 0
        self.total_commits = 0

        # [RQ0]: How many types are used?
        self.RQ0 = 'How many types are used?'
        self.commits_with_typeChanges = 0
        self.percentage_commits_with_typeChanges = ''
        self.total_typeAnnotation_codeChanges = 0

        # [RQ1]: Are type annotation inserted, removed and changed?
        self.RQ1 = 'Are type annotation inserted, removed and changed?'
        self.insert_types = 0
        self.percentage_insert_types = ''
        self.remove_types = 0
        self.percentage_remove_types = ''
        self.modify_existing_types = 0
        self.percentage_modify_existing_types = ''

        # [RQ2]: What types are added (primitives, built-in classes, application-specific classes)?
        self.RQ2 = 'What types are added (primitives, built-in classes, application-specific classes)?'
        self.typeAdded_dict = {}
        self.primitiveTypes_added = 0
        self.buildinTypes_added = 0
        self.newTypes_added = 0
        self.total_added = 0

        # [RQ3]: What types are removed (primitives, built-in classes, application-specific classes)?
        self.RQ3 = 'What types are removed (primitives, built-in classes, application-specific classes)?'
        self.typeRemoved_dict = {}
        self.primitiveTypes_removed = 0
        self.buildinTypes_removed = 0
        self.newTypes_removed = 0
        self.total_removed = 0

    #################################################
    #################METHODS#########################
    #################################################

    # All statistics computation
    def statistics_computation(self):
        # [RQ1]: Are type annotation inserted, removed and changed?
        self.percentage_computation()

        # [RQ2]: What types are added (primitives, built-in classes, application-specific classes)?
        self.what_types_added()

        # [RQ3]: What types are removed (primitives, built-in classes, application-specific classes)?
        self.what_types_removed()

    # [RQ1]: Are type annotation inserted, removed and changed?
    def percentage_computation(self):
        self.total_typeAnnotation_codeChanges = self.insert_types + self.remove_types + self.modify_existing_types

        self.percentage_commits_with_typeChanges = str(
            round(self.commits_with_typeChanges / self.total_commits * 100, 2)) + ' %'
        self.percentage_insert_types = str(
            round(self.insert_types / self.total_typeAnnotation_codeChanges * 100, 1)) + ' %'
        self.percentage_remove_types = str(
            round(self.remove_types / self.total_typeAnnotation_codeChanges * 100, 1)) + ' %'
        self.percentage_modify_existing_types = str(
            round(self.modify_existing_types / self.total_typeAnnotation_codeChanges * 100, 1)) + ' %'

    # [RQ2]: What types are added (primitives, built-in classes, application-specific classes)?

    primitivesTypes_List = ['int', 'float', 'bool', 'str']  # Primitives types

    # Buil-in Types
    buildinTypes_List = ['None', 'Any',  # Generic types
                         'long', 'complex',  # Numeric Types
                         'unicode', 'byte', 'list', 'tuple', 'bytearray', 'memoryview', 'buffer', 'range',
                         'xrange'  # Sequence Types
                         'set', 'frozenset',  # Set Types
                         'dict']  # Mapping Types

    def what_types_added(self):

        for type in self.typeAdded_dict.keys():
            if type in self.primitivesTypes_List:
                self.primitiveTypes_added += self.typeAdded_dict[type]

        for type in self.typeAdded_dict.keys():
            if type in self.buildinTypes_List:
                self.buildinTypes_added += self.typeAdded_dict[type]

    # self.newTypes = self.total_typeAnnotation_codeChanges - self.primitiveTypes_added - self.buildinTypes_added

    # [RQ3]: What types are removed (primitives, built-in classes, application-specific classes)?
    def what_types_removed(self):

        for type in self.typeRemoved_dict.keys():
            if type in self.primitivesTypes_List:
                self.primitiveTypes_removed += self.typeRemoved_dict[type]

        for type in self.typeRemoved_dict.keys():
            if type in self.buildinTypes_List:
                self.buildinTypes_removed += self.typeRemoved_dict[type]

        # self.newTypes = self.total_typeAnnotation_codeChanges - self.primitiveTypes_added - self.buildinTypes_added
