import json
import multiprocessing
import platform
import re
from collections import namedtuple
import numpy as np
import config


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

        # [RQ2.1]: What types are added (primitives, built-in classes, application-specific classes)?
        self.RQ2_1 = 'What types are added (primitives, built-in classes, application-specific classes)?'
        self.typeAdded_dict = {}
        self.primitiveType_added = 0
        self.buildinType_added = 0
        self.newType_added = 0
        self.total_added = 0

        # [RQ2.2]: What types are removed (primitives, built-in classes, application-specific classes)?
        self.RQ2_2 = 'What types are removed (primitives, built-in classes, application-specific classes)?'
        self.typeRemoved_dict = {}
        self.primitiveType_removed = 0
        self.buildinType_removed = 0
        self.newType_removed = 0
        self.total_removed = 0

        # [RQ3.1]: Where are types added (function args, function returns, variables, fields)?
        self.RQ3_1 = 'Where are types added (function args, function returns, variables, fields)?'
        self.functionArgsType_added = 0
        self.functionReturnsType_added = 0
        self.variableType_added = 0
        self.fieldType_added = 0

        # [RQ3.2]: Where are types removed (function args, function returns, variables, fields)?
        self.RQ3_2 = 'Where are types removed (function args, function returns, variables, fields)?'
        self.functionArgsType_removed = 0
        self.functionReturnsType_removed = 0
        self.variableType_removed = 0
        self.fieldType_removed = 0

        # [RQ4]: Are many types added at once or rather a few types here and there?
        self.RQ4 = 'Are types added along with other changes around this code or in commits that only add types?'
        self.typeAnnotation_per_commit = 0

        # [RQ5]: Are many types added at once or rather a few types here and there?
        self.RQ5 = 'Are types added along with other changes around this code or in commits that only add types?'

        # [RQ6]: Relation of properties of projects vs. properties of type changes
        # E.g., nb of stars/developers/overall commits vs. nb of added annotations
        self.RQ6 = 'Relation of properties of projects vs. properties of type changes.'
       # self.repoStruct = namedtuple("repoStruct", "name n_stars n_commit n_annotations")
       # self.repoList = []
        self.matrix_commits_stars_annotations = np.array([[0, 0, 0]])

    #################################################
    #################METHODS#########################
    #################################################

    # All statistics computation
    def statistics_computation(self):
        # [RQ1]: Are type annotation inserted, removed and changed?
        self.percentage_computation()

        # [RQ2.1]: What types are added (primitives, built-in classes, application-specific classes)?
        self.what_types_added()

        # [RQ2.2]: What types are removed (primitives, built-in classes, application-specific classes)?
        self.what_types_removed()

        # [RQ4]: Are many types added at once or rather a few types here and there?
        self.rate_annotation_commit()

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

    # [RQ2.1]: What types are added (primitives, built-in classes, application-specific classes)?

    primitivesTypes_List = ['int', 'float', 'bool', 'str']  # Primitives types

    # Buil-in Types
    buildinTypes_List = ['none', 'any',  # Generic types
                         'long', 'complex',  # Numeric Types
                         'unicode', 'byte', 'list', 'tuple', 'bytearray', 'memoryview', 'buffer', 'range',
                         'xrange'  # Sequence Types
                         'set', 'frozenset',  # Set Types
                         'dict']  # Mapping Types

    def what_types_added(self):

        for type in self.typeAdded_dict.keys():
            if type in self.primitivesTypes_List:
                self.primitiveType_added += self.typeAdded_dict[type]

        for type in self.typeAdded_dict.keys():
            type_clean = re.sub(r'\[[^)]*\]', '', type.lower())
            if type_clean in self.buildinTypes_List:
                self.buildinType_added += self.typeAdded_dict[type]

        self.newType_added = self.total_added  - self.buildinType_added  - self.primitiveType_added

    # [RQ2.2]: What types are removed (primitives, built-in classes, application-specific classes)?
    def what_types_removed(self):

        for type in self.typeRemoved_dict.keys():
            if type in self.primitivesTypes_List:
                self.primitiveType_removed += self.typeRemoved_dict[type]

        for type in self.typeRemoved_dict.keys():
            type_clean = re.sub(r'\[[^)]*\]', '', type.lower())
            if type_clean in self.buildinTypes_List:
                self.buildinType_removed += self.typeRemoved_dict[type]

        self.newType_removed = self.total_removed - self.buildinType_removed - self.primitiveType_removed

    # [RQ4]: Are many types added at once or rather a few types here and there?
    def rate_annotation_commit(self):
        self.typeAnnotation_per_commit = str(
            round(self.total_typeAnnotation_codeChanges / self.commits_with_typeChanges, 2)) + ' Type annotations ' \
                                                                                               'changes per commit '

    # [RQ6]: Relation of properties of projects vs. properties of type changes
    # E.g., nb of stars/developers/overall commits vs. nb of added annotations
    def addRepo(self, name, n_commits, n_annotations):
        input_file = open(config.REPO_LIST, 'r')
        json_decode = json.load(input_file)

        for item in json_decode:
            if item.get('name') == name:
               # self.repoList.append(self.repoStruct(item.get('html_url'), item.get('stars'), n_commits, n_annotations))
                self.matrix_commits_stars_annotations =\
                    np.append(self.matrix_commits_stars_annotations, np.array([[n_commits, item.get('stars'),  n_annotations]]), axis=0)
                break