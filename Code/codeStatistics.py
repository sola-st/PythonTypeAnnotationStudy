import json
import multiprocessing
import platform
import re
import numpy as np
import config
from Code.lucaUtils import sort_dictionary


class CodeStatistics:
    """Code change class"""

    def __init__(self):
        self.execution_time = ''
        self.machine = {'OS': platform.platform(), 'CPU': platform.processor(), 'CORES': multiprocessing.cpu_count()}
        self.total_repositories = 0
        self.total_commits = 0
        self.s1 = "------------------------------------------------------------------------"

        # [RQ0]: How many types are used?
        self.RQ0 = 'How many types are used?'
        self.repo_with_types_changes = 0
        self.percentage_repo_with_typeChanges = ''
        self.commits_with_typeChanges = 0
        self.percentage_commits_with_typeChanges = ''
        self.total_typeAnnotation_codeChanges = 0
        self.s2 = "------------------------------------------------------------------------"

        # [RQ1]: Are type annotation inserted, removed and changed?
        self.RQ1 = 'Are type annotation inserted, removed and changed?'
        self.insert_types = 0
        self.percentage_insert_types = ''
        self.remove_types = 0
        self.percentage_remove_types = ''
        self.modify_existing_types = 0
        self.percentage_modify_existing_types = ''

        self.s3 = "------------------------------------------------------------------------"
        # [RQ2.1]: What types are added (generic, numeric, ...)?
        self.RQ2_1 = 'What types are added (generic, numeric, ...)?'
        self.genericType_added = 0
        self.numericType_added = 0
        self.binarySequenceType_added = 0
        self.textSequenceType_added = 0
        self.mappingTypes_added = 0
        self.setTypes_added = 0
        self.sequenceType_added = 0
        self.newType_added = 0
        self.total_added = 0

        # [RQ2.2]: What are the top 5 types added?
        self.RQ2_2 = 'What are the top 5 types added?'
        self.typeAdded_dict = {}

        # [RQ2.3]: What types are removed (generic, numeric, ...)?
        self.RQ2_3 = 'What types are removed (generic, numeric, ...)?'
        self.genericType_removed = 0
        self.numericType_removed = 0
        self.binarySequenceType_removed = 0
        self.textSequenceType_removed = 0
        self.mappingTypes_removed = 0
        self.setTypes_removed = 0
        self.sequenceType_removed = 0
        self.newType_removed = 0
        self.total_removed = 0
        self.newType_removed = 0
        self.total_removed = 0

        # [RQ2.4]: What are the top 5 types removed?
        self.RQ2_4 = 'What are the top 5 types removed?'
        self.typeRemoved_dict = {}

        # [RQ2.5]: What types are changed?
        self.RQ2_5 = 'What types are changed (primitives, built-in classes, application-specific classes)?'
        self.total_changed = 0
        self.typeChanged_dict = {}
        self.s4 = "------------------------------------------------------------------------"

        # [RQ3.1]: Where are types added (function args, function returns, variables, fields)?
        self.RQ3_1 = 'Where are types added (function args, function returns, variables, fields)?'
        self.functionArgsType_added = 0
        self.functionReturnsType_added = 0
        self.variableType_added = 0
        self.fieldType_added = 0
        # TODO: [RQ3.1]: variable types and field type

        # [RQ3.2]: Where are types removed (function args, function returns, variables, fields)?
        self.RQ3_2 = 'Where are types removed (function args, function returns, variables, fields)?'
        self.functionArgsType_removed = 0
        self.functionReturnsType_removed = 0
        self.variableType_removed = 0
        self.fieldType_removed = 0

        # [RQ3.3]: Where are types changed (function args, function returns, variables, fields)?
        self.RQ3_3 = 'Where are types changed (function args, function returns, variables, fields)?'
        self.functionArgsType_changed = 0
        self.functionReturnsType_changed = 0
        self.variableType_changed = 0
        self.fieldType_changed = 0
        self.s5 = "------------------------------------------------------------------------"

        # TODO: [RQ3.2]: variable types and field type

        # [RQ4.1]: Are many types added at once or rather a few types here and there?
        self.RQ4_1 = 'Are types added along with other changes around this code or in commits that only add types?'
        self.typeAnnotation_added_per_commit = 0
        self.list_typeAnnotation_added_per_commit = []

        # [RQ4.2]: Are many types removed at once or rather a few types here and there?
        self.RQ4_2 = 'Are types removed along with other changes around this code or in commits that only add types?'
        self.typeAnnotation_removed_per_commit = 0
        self.list_typeAnnotation_removed_per_commit = []

        # [RQ4.3]: Are many types changed at once or rather a few types here and there?
        self.RQ4_3 = 'Are types changed along with other changes around this code or in commits that only add types?'
        self.typeAnnotation_changed_per_commit = 0
        self.list_typeAnnotation_changed_per_commit = []
        self.s6 = "------------------------------------------------------------------------"

        # [RQ5]: Relation of properties of projects vs. properties of type changes
        # E.g., nb of stars/developers/overall commits vs. nb of added annotations
        self.RQ5 = 'Relation of properties of projects vs. properties of type changes.'
        self.matrix_commits_stars_annotations = np.array([[0, 0, 0]])
        self.s7 = "------------------------------------------------------------------------"

        # [RQ6]: Which are the top 10 repository with the highest number of type annotations
        self.RQ6 = 'Which are the top 10 repository with the highest number of type annotations.'
        self.number_type_annotations_per_repo = {}

    #################################################
    #################METHODS#########################
    #################################################

    # All statistics computation
    def statistics_computation(self):
        # [RQ1]: Are type annotation inserted, removed and changed?
        self.percentage_computation()

        # [RQ2.1]: What types are added (primitives, built-in classes, application-specific classes)?
        self.what_types_added()

        # [RQ2.2]: What are the top 5 types added?
        self.typeAdded_dict = sort_dictionary(self.typeAdded_dict)[:2]

        # [RQ2.3]: What types are removed (primitives, built-in classes, application-specific classes)?
        self.what_types_removed()

        # [RQ2.4]: What are the top 5 types removed?
        self.typeRemoved_dict = sort_dictionary(self.typeRemoved_dict)[:2]

        # [RQ2.5]: What are the types changed?
        self.typeChanged_dict = sort_dictionary(self.typeChanged_dict)

        # [RQ4]: Are many types added at once or rather a few types here and there?
        self.rate_annotation_commit()

        # [RQ6]: Which are the top 10 repository with the highest number of type annotations
        self.number_type_annotations_per_repo = sort_dictionary(self.number_type_annotations_per_repo)[:3]

    # [RQ1]: Are type annotation inserted, removed and changed?
    def percentage_computation(self):
        self.total_typeAnnotation_codeChanges = self.insert_types + self.remove_types + self.modify_existing_types

        self.percentage_repo_with_typeChanges = str(
            round(self.repo_with_types_changes / self.total_repositories * 100, 2)) + ' %'
        self.percentage_commits_with_typeChanges = str(
            round(self.commits_with_typeChanges / self.total_commits * 100, 2)) + ' %'
        self.percentage_insert_types = str(
            round(self.insert_types / self.total_typeAnnotation_codeChanges * 100, 1)) + ' %'
        self.percentage_remove_types = str(
            round(self.remove_types / self.total_typeAnnotation_codeChanges * 100, 1)) + ' %'
        self.percentage_modify_existing_types = str(
            round(self.modify_existing_types / self.total_typeAnnotation_codeChanges * 100, 1)) + ' %'

    # [RQ2.1]: What types are added (generic, numeric, ...)?

    # https://docs.python.org/3/library/stdtypes.html
    genericType_list = ['none', 'any']
    numericType_list = ['int', 'float', 'complex']
    sequenceType_list = ['list', 'tuple', 'range']
    textSequenceType_list = ['str']
    binarySequenceType_list = ['bytes', 'bytearray', 'memoryview']
    setTypes_list = ['set', 'frozenset']
    mappingTypes_list = ['dict']

    def what_types_added(self):

        # Generic types
        for type in self.typeAdded_dict.keys():
            if type in self.genericType_list:
                self.genericType_added += self.typeAdded_dict[type]

        # Numeric types
        for type in self.typeAdded_dict.keys():
            if type in self.numericType_list:
                self.numericType_added += self.typeAdded_dict[type]

        # Sequence types
        for type in self.typeAdded_dict.keys():
            if type in self.sequenceType_list:
                self.sequenceType_added += self.typeAdded_dict[type]

        # Text types
        for type in self.typeAdded_dict.keys():
            if type in self.textSequenceType_list:
                self.textSequenceType_added += self.typeAdded_dict[type]

        # Binary Sequence types
        for type in self.typeAdded_dict.keys():
            if type in self.binarySequenceType_list:
                self.binarySequenceType_added += self.typeAdded_dict[type]

        # Set types
        for type in self.typeAdded_dict.keys():
            if type in self.setTypes_list:
                self.setTypes_added += self.typeAdded_dict[type]

        # Mapping types
        for type in self.typeAdded_dict.keys():
            if type in self.mappingTypes_list:
                self.mappingTypes_added += self.typeAdded_dict[type]

        self.newType_added = self.total_added - self.genericType_added - self.numericType_added - self.sequenceType_added \
                             - self.textSequenceType_added - self.binarySequenceType_added \
                             - self.setTypes_added - self.mappingTypes_added

    # [RQ2.2]: What types are removed (generic, numeric, ...)?
    def what_types_removed(self):

        # Generic types
        for type in self.typeRemoved_dict.keys():
            if type in self.genericType_list:
                self.genericType_removed += self.typeRemoved_dict[type]

        # Numeric types
        for type in self.typeRemoved_dict.keys():
            if type in self.numericType_list:
                self.numericType_removed += self.typeRemoved_dict[type]

        # Sequence types
        for type in self.typeRemoved_dict.keys():
            if type in self.sequenceType_list:
                self.sequenceType_removed += self.typeRemoved_dict[type]

        # Text types
        for type in self.typeRemoved_dict.keys():
            if type in self.textSequenceType_list:
                self.textSequenceType_removed += self.typeRemoved_dict[type]

        # Binary Sequence types
        for type in self.typeRemoved_dict.keys():
            if type in self.binarySequenceType_list:
                self.binarySequenceType_removed += self.typeRemoved_dict[type]

        # Set types
        for type in self.typeRemoved_dict.keys():
            if type in self.setTypes_list:
                self.setTypes_removed += self.typeRemoved_dict[type]

        # Mapping types
        for type in self.typeRemoved_dict.keys():
            if type in self.mappingTypes_list:
                self.mappingTypes_removed += self.typeRemoved_dict[type]

        self.newType_removed = self.total_removed - self.genericType_removed - self.numericType_removed - self.sequenceType_removed \
                               - self.textSequenceType_removed - self.binarySequenceType_removed \
                               - self.setTypes_removed - self.mappingTypes_removed

    # [RQ4]: Are many types added at once or rather a few types here and there?
    def rate_annotation_commit(self):
        self.typeAnnotation_added_per_commit = str(
            round(self.total_added / self.commits_with_typeChanges, 2)) + ' Type annotations ' \
                                                                                               'changes per commit '

        self.typeAnnotation_removed_per_commit = str(
            round(self.total_removed / self.commits_with_typeChanges, 2)) + ' Type annotations ' \
                                                                                               'changes per commit '

        self.typeAnnotation_changed_per_commit = str(
            round(self.total_changed / self.commits_with_typeChanges, 2)) + ' Type annotations ' \
                                                                                               'changes per commit '
    # [RQ5]: Relation of properties of projects vs. properties of type changes
    # E.g., nb of stars/developers/overall commits vs. nb of added annotations
    def addRepo(self, name, n_commits, n_annotations):
        input_file = open(config.REPO_LIST, 'r')
        json_decode = json.load(input_file)

        for item in json_decode:
            if item.get('name') == name:
                self.matrix_commits_stars_annotations = \
                    np.append(self.matrix_commits_stars_annotations,
                              np.array([[n_commits, item.get('stargazers_count'), n_annotations]]), axis=0)
                break
