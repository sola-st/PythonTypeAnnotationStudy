import json
import multiprocessing
import platform
import numpy as np
import config
from Code.TypeAnnotations.lucaUtils import sort_dictionary, merge_dictionaries


class CodeStatistics:
    """Code change class"""

    def __init__(self):
        self.execution_time = ''
        self.machine = {'OS': platform.platform(), 'CPU': platform.processor(), 'CORES': multiprocessing.cpu_count()}
        self.total_repositories = 0
        self.total_commits = 0
        self.commit_year_dict = {}
        self.s0 = "------------------------------------------------------------------------"

        # [RQ0]: How many types are used?
        self.RQ0 = 'How many types are used?'
        self.code_changes: list = []
        self.commit_statistics: list = []
        self.repo_with_types_changes = 0
        self.percentage_repo_with_typeChanges = ''
        self.commits_with_typeChanges = 0
        self.percentage_commits_with_typeChanges = ''
        self.total_typeAnnotation_codeChanges = 0
        self.s1 = "------------------------------------------------------------------------"

        # [RQ1]: Are type annotation inserted, removed and changed?
        self.RQ1 = 'Are type annotation inserted, removed and changed?'
        self.insert_types = {}
        self.percentage_insert_types = ''
        self.remove_types = {}
        self.percentage_remove_types = ''
        self.modify_existing_types = {}
        self.percentage_modify_existing_types = ''

        self.s2 = "------------------------------------------------------------------------"
        # [RQ2.1]: What types are added (generic, numeric, ...)?
        self.RQ2_1 = 'What types are added (generic, numeric, ...)?'
        self.anyType_added = 0
        self.noneType_added = 0
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
        self.anyType_removed = 0
        self.noneType_removed = 0
        self.numericType_removed = 0
        self.binarySequenceType_removed = 0
        self.textSequenceType_removed = 0
        self.mappingTypes_removed = 0
        self.setTypes_removed = 0
        self.sequenceType_removed = 0
        self.newType_removed = 0
        self.total_removed = 0
        self.newType_removed = 0

        # [RQ2.4]: What are the top 5 types removed?
        self.RQ2_4 = 'What are the top 5 types removed?'
        self.typeRemoved_dict = {}

        # [RQ2.5]: What types are the top 10 changed?
        self.RQ2_5 = 'What types are the top 10 changed ?'
        self.total_changed = 0
        self.typeChanged_dict_var = {}
        self.typeChanged_dict_arg = {}
        self.typeChanged_dict_ret = {}
        self.s3 = "------------------------------------------------------------------------"

        # [RQ3.1]: Where are types added (function args, function returns, variables)?
        self.RQ3_1 = 'Where are types added (function args, function returns, variables)?'
        self.functionArgsType_added = 0
        self.functionReturnsType_added = 0
        self.variableType_added = 0

        # [RQ3.2]: Where are types removed (function args, function returns, variables)?
        self.RQ3_2 = 'Where are types removed (function args, function returns, variables)?'
        self.functionArgsType_removed = 0
        self.functionReturnsType_removed = 0
        self.variableType_removed = 0

        # [RQ3.3]: Where are types changed (function args, function returns, variables)?
        self.RQ3_3 = 'Where are types changed (function args, function returns, variables?'
        self.functionArgsType_changed = 0
        self.functionReturnsType_changed = 0
        self.variableType_changed = 0
        self.s4 = "------------------------------------------------------------------------"

        # [RQ4.1]: Are many types added at once or rather a few types here and there?
        self.RQ4_1 = 'Are types added along with other changes around this code or in commits that only add types?'
        self.typeAnnotation_added_per_commit = 0
        self.list_typeAnnotation_added_per_commit = []

        # [RQ4.2]: Are many types removed at once or rather a few types here and there?
        self.RQ4_2 = 'Are types removed along with other changes around this code or in commits that only add types?'
        self.typeAnnotation_removed_per_commit = 0
        self.list_typeAnnotation_removed_per_commit = []

        # [RQ4]: Are many types changed at once or rather a few types here and there?
        self.RQ4_3 = 'Are types changed along with other changes around this code or in commits that only add types?'
        self.typeAnnotation_changed_per_commit = 0
        self.list_typeAnnotation_changed_per_commit = []

        # [RQ4.4]: Computation percentage of annotation-related insertion to all edits per each commit
        self.annotation_related_insertion_edits_vs_all_commit = []

        # [RQ4.5]: Computation percentage of annotation-related deletions to all edits per each commit
        self.annotation_related_deletion_edits_vs_all_commit = []
        self.s5 = "------------------------------------------------------------------------"

        # [RQ5]: Relation of properties of projects vs. properties of type changes
        # E.g., nb of stars/developers/overall commits vs. nb of added annotations
        self.RQ5 = 'Relation of properties of projects vs. properties of type changes.'
        self.matrix_commits_stars_annotations = np.empty((0, 11), int)
        self.matrix_files_annotations = np.empty((0, 3), int)
        self.matrix_test_files_annotations = np.empty((0, 3), int)
        self.dict_funct_call_no_types = {}
        self.dict_funct_call_types = {}
        self.s6 = "------------------------------------------------------------------------"

        # [RQ6]: Which are the top 10 repository with the highest number of type annotations
        self.RQ6 = 'Which are the top 10 repository with the highest number of type annotations.'
        self.number_type_annotations_per_repo = {}
        self.s7 = "------------------------------------------------------------------------"

        # [RQ7]: How many of all types are annotated in the last version of the code?
        self.RQ7 = 'How many of all types are annotated in the last version of the code?'
        self.typeLastProjectVersion_total = 0
        self.typeLastProjectVersion_average = 0
        self.typeLastProjectVersion_percentage = []
        self.typeLastProjectVersion_dict = {}

        # [RQ8]: Computation percentage of annotation-related edits to all edits per each commit
        # self.RQ8 = 'Computation percentage of annotation-related edits to all edits per each commit'
        # self.annotation_related_insertion_edits_vs_all_commit = []
        # self.annotation_related_deletion_edits_vs_all_commit = []

        # [RQ8]: Total number of annotations over time, across all projects
        self.RQ8 = 'Total number of annotations over time, across all projects'
        self.typeAnnotation_year_analysis = {}

        # [RQ9]: Total number of annotation-related commit over time, across all projects
        self.RQ9 = 'Total number of annotation-related commit over time, across all projects'
        self.typeAnnotation_commit_annotation_year_analysis = {}
        self.typeAnnotation_commit_not_annotation_year_analysis = {}

        # RQ 10: Coverage
        self.RQ10 = 'Type annotation coverage for each each'
        self.annotation_coverage = {'2014': [0, 0, 0, 0, 0, 0],
                               '2015': [0, 0, 0, 0, 0, 0],
                               '2016': [0, 0, 0, 0, 0, 0],
                               '2017': [0, 0, 0, 0, 0, 0],
                               '2018': [0, 0, 0, 0, 0, 0],
                               '2019': [0, 0, 0, 0, 0, 0],
                               '2020': [0, 0, 0, 0, 0, 0], }

        #RQ11: Developers study
        self.RQ11 = 'Developers statistics'
        self.list_dev_dict = []
        self.dev_dict = {}
        self.dev_dict_total = {}
        self.list_dev_plot = []


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
        self.typeAdded_dict = sort_dictionary(self.typeAdded_dict)[:5]

        # [RQ2.3]: What types are removed (primitives, built-in classes, application-specific classes)?
        self.what_types_removed()

        # [RQ2.4]: What are the top 5 types removed?
        self.typeRemoved_dict = sort_dictionary(self.typeRemoved_dict)[:5]

        # [RQ2.5]: What are the top 10 types changed?
        #self.typeChanged_dict = sort_dictionary(self.typeChanged_dict)[:10]
        self.typeChanged_dict_var = sort_dictionary(self.typeChanged_dict_var)[:10]
        self.typeChanged_dict_arg = sort_dictionary(self.typeChanged_dict_arg)[:10]
        self.typeChanged_dict_ret = sort_dictionary(self.typeChanged_dict_ret)[:10]

        # [RQ4]: Are many types added at once or rather a few types here and there?
        self.rate_annotation_commit()

        # [RQ6]: Which are the top 10 repository with the highest number of type annotations
        self.number_type_annotations_per_repo = sort_dictionary(self.number_type_annotations_per_repo)[:10]

        # [RQ7]: How many of all types are annotated in the last verison of the code?
        if self.total_typeAnnotation_codeChanges > 0:
            self.typeLastProjectVersion_average = sum(self.typeLastProjectVersion_percentage) / len(
                self.typeLastProjectVersion_percentage)

        #   self.typeLastProjectVersion_percentage.append(
        #      round(self.typeLastProjectVersion_total / self.insert_types * 100, 2))

        self.typeLastProjectVersion_dict = sort_dictionary(self.typeLastProjectVersion_dict)

    # [RQ1]: Are type annotation inserted, removed and changed?
    def percentage_computation(self):
        self.total_typeAnnotation_codeChanges = sum(self.insert_types.values()) + sum(self.remove_types.values()) + sum(
            self.modify_existing_types.values())

        self.percentage_repo_with_typeChanges = str(
            round(self.repo_with_types_changes / self.total_repositories * 100, 2)) + ' %'
        self.percentage_commits_with_typeChanges = str(
            round(self.commits_with_typeChanges / self.total_commits * 100, 2)) + ' %'
        self.percentage_insert_types = str(
            round(sum(self.insert_types.values()) / self.total_typeAnnotation_codeChanges * 100, 1)) + ' %'
        self.percentage_remove_types = str(
            round(sum(self.remove_types.values()) / self.total_typeAnnotation_codeChanges * 100, 1)) + ' %'
        self.percentage_modify_existing_types = str(
            round(sum(self.modify_existing_types.values()) / self.total_typeAnnotation_codeChanges * 100, 1)) + ' %'

    # [RQ2.1]: What types are added (generic, numeric, ...)?

    # https://docs.python.org/3/library/stdtypes.html
    anyType_list = ['any']
    noneType_list = ['none']
    numericType_list = ['int', 'float', 'complex']
    sequenceType_list = ['list', 'tuple', 'range']
    textSequenceType_list = ['str']
    binarySequenceType_list = ['bytes', 'bytearray', 'memoryview']
    setTypes_list = ['set', 'frozenset']
    mappingType_list = ['dict']

    def what_types_added(self):

        # Any types
        for type in self.typeAdded_dict.keys():
            if type in self.anyType_list:
                self.anyType_added += self.typeAdded_dict[type]

        # None types
        for type in self.typeAdded_dict.keys():
            if type in self.noneType_list:
                self.noneType_added += self.typeAdded_dict[type]

        # Numeric types
        for type in self.typeAdded_dict.keys():
            if type in self.numericType_list:
                self.numericType_added += self.typeAdded_dict[type]

        # Sequence types
        for type in self.typeAdded_dict.keys():
            if any(x in type for x in self.sequenceType_list) and '->' not in type:
                self.sequenceType_added += self.typeAdded_dict[type]

        # Text types
        for type in self.typeAdded_dict.keys():
            if type in self.textSequenceType_list:
                self.textSequenceType_added += self.typeAdded_dict[type]

        # Binary Sequence types
        for type in self.typeAdded_dict.keys():
            if any(x in type for x in self.binarySequenceType_list) and '->' not in type:
                self.binarySequenceType_added += self.typeAdded_dict[type]

        # Set types
        for type in self.typeAdded_dict.keys():
            if any(x in type for x in self.setTypes_list) and '->' not in type:
                self.setTypes_added += self.typeAdded_dict[type]

        # Mapping types
        for type in self.typeAdded_dict.keys():
            if any(x in type for x in self.mappingType_list) and '->' not in type:
                self.mappingTypes_added += self.typeAdded_dict[type]

        self.newType_added = self.total_added - self.anyType_added - self.noneType_added - self.numericType_added - self.sequenceType_added \
                             - self.textSequenceType_added - self.binarySequenceType_added \
                             - self.setTypes_added - self.mappingTypes_added

    # [RQ2.2]: What types are removed (generic, numeric, ...)?
    def what_types_removed(self):

        # Any types
        for type in self.typeRemoved_dict.keys():
            if type in self.anyType_list:
                self.anyType_removed += self.typeRemoved_dict[type]

        # None types
        for type in self.typeRemoved_dict.keys():
            if type in self.noneType_list:
                self.noneType_removed += self.typeRemoved_dict[type]

        # Numeric types
        for type in self.typeRemoved_dict.keys():
            if type in self.numericType_list:
                self.numericType_removed += self.typeRemoved_dict[type]

        # Sequence types
        for type in self.typeRemoved_dict.keys():
            if any(x in type for x in self.sequenceType_list) and '->' not in type:
                self.sequenceType_removed += self.typeRemoved_dict[type]

        # Text types
        for type in self.typeRemoved_dict.keys():
            if type in self.textSequenceType_list:
                self.textSequenceType_removed += self.typeRemoved_dict[type]

        # Binary Sequence types
        for type in self.typeRemoved_dict.keys():
            if any(x in type for x in self.binarySequenceType_list) and '->' not in type:
                self.binarySequenceType_removed += self.typeRemoved_dict[type]

        # Set types
        for type in self.typeRemoved_dict.keys():
            if any(x in type for x in self.setTypes_list) and '->' not in type:
                self.setTypes_removed += self.typeRemoved_dict[type]

        # Mapping types
        for type in self.typeRemoved_dict.keys():
            if any(x in type for x in self.mappingType_list) and '->' not in type:
                self.mappingTypes_removed += self.typeRemoved_dict[type]

        self.newType_removed = self.total_removed - self.anyType_removed - self.noneType_removed - self.numericType_removed - self.sequenceType_removed \
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
    def addRepo(self, name, n_commits, n_annotations, n_test_files, n_non_test_files, n_dev, funct_type_avg, fuct_no_type_avg):
        i = 0
        while i < 10:
            input_file = open(config.ROOT_DIR + "/Resources/Input/Top1000_Python201" + str(i) + "_Complete.json", 'r')
            #input_file = open(config.ROOT_DIR + "/Resources/Input/repositories_TOP100_2020.json", 'r')
            i += 1
            json_decode = json.load(input_file)

            for item in json_decode:
                if item.get('full_name').replace('/', '-') == name:
                    self.number_type_annotations_per_repo[item.get('html_url')] = self.number_type_annotations_per_repo[
                        name]
                    del self.number_type_annotations_per_repo[name]

                    if name in self.typeLastProjectVersion_dict:
                        self.typeLastProjectVersion_dict[item.get('html_url')] = self.typeLastProjectVersion_dict[name]
                        del self.typeLastProjectVersion_dict[name]

                    n_stars = item.get('stargazers_count')
                    n_forks = item.get('forks_count')
                    n_issues = item.get('open_issues')
                    creation_date = item.get('created_at')[:4]

                    self.matrix_commits_stars_annotations = \
                        np.append(self.matrix_commits_stars_annotations,
                                  np.array([[creation_date, n_commits, n_stars, n_annotations, n_forks, n_issues, n_test_files, n_non_test_files, n_dev, funct_type_avg, fuct_no_type_avg]]), axis=0)
                    return

    def merge_results(self, process_statistics, code_changes, commit_statistics):

        for stat in process_statistics:
            try:
                self.total_repositories += stat.total_repositories
                self.total_commits += stat.total_commits

                # RQ0
                code_changes += stat.code_changes
                commit_statistics += stat.commit_statistics
                self.repo_with_types_changes += stat.repo_with_types_changes
                self.commits_with_typeChanges += stat.commits_with_typeChanges
                self.total_typeAnnotation_codeChanges += stat.total_typeAnnotation_codeChanges
                self.commit_year_dict = dict(
                    merge_dictionaries([dict(self.commit_year_dict), dict(stat.commit_year_dict)]))

                # RQ1
                self.insert_types = dict(merge_dictionaries([dict(self.insert_types), dict(stat.insert_types)]))
                self.remove_types = dict(merge_dictionaries([dict(self.remove_types), dict(stat.remove_types)]))
                self.modify_existing_types = dict(
                    merge_dictionaries([dict(self.modify_existing_types), dict(stat.modify_existing_types)]))

                # RQ2.1
                self.anyType_added += stat.anyType_added
                self.noneType_added += stat.noneType_added
                self.numericType_added += stat.numericType_added
                self.binarySequenceType_added += stat.binarySequenceType_added
                self.textSequenceType_added += stat.textSequenceType_added
                self.mappingTypes_added += stat.mappingTypes_added
                self.setTypes_added += stat.setTypes_added
                self.sequenceType_added += stat.sequenceType_added
                self.newType_added += stat.newType_added
                self.total_added += stat.total_added

                # RQ2.2
                self.typeAdded_dict = merge_dictionaries([self.typeAdded_dict, stat.typeAdded_dict])

                # RQ2.3
                self.anyType_removed += stat.anyType_removed
                self.noneType_removed += stat.noneType_removed
                self.numericType_removed += stat.numericType_removed
                self.binarySequenceType_removed += stat.binarySequenceType_removed
                self.textSequenceType_removed += stat.textSequenceType_removed
                self.mappingTypes_removed += stat.mappingTypes_removed
                self.setTypes_removed += stat.setTypes_removed
                self.sequenceType_removed += stat.sequenceType_removed
                self.newType_removed += stat.newType_removed
                self.total_removed += stat.total_removed

                # RQ2.4
                self.typeRemoved_dict = merge_dictionaries([self.typeRemoved_dict, stat.typeRemoved_dict])

                # RQ2.5
                self.total_changed += stat.total_changed
                self.typeChanged_dict_arg = merge_dictionaries([self.typeChanged_dict_arg, stat.typeChanged_dict_arg])
                self.typeChanged_dict_var = merge_dictionaries([self.typeChanged_dict_var, stat.typeChanged_dict_var])
                self.typeChanged_dict_ret = merge_dictionaries([self.typeChanged_dict_ret, stat.typeChanged_dict_ret])

                # RQ 3.1
                self.functionArgsType_added += stat.functionArgsType_added
                self.functionReturnsType_added += stat.functionReturnsType_added
                self.variableType_added += stat.variableType_added

                # RQ 3.2
                self.functionArgsType_removed += stat.functionArgsType_removed
                self.functionReturnsType_removed += stat.functionReturnsType_removed
                self.variableType_removed += stat.variableType_removed

                # RQ 3.3
                self.functionArgsType_changed += stat.functionArgsType_changed
                self.functionReturnsType_changed += stat.functionReturnsType_changed
                self.variableType_changed += stat.variableType_changed

                # RQ 4.1
                self.typeAnnotation_added_per_commit += stat.typeAnnotation_added_per_commit
                self.list_typeAnnotation_added_per_commit += stat.list_typeAnnotation_added_per_commit

                # RQ 4.2
                self.typeAnnotation_removed_per_commit += stat.typeAnnotation_removed_per_commit
                self.list_typeAnnotation_removed_per_commit += stat.list_typeAnnotation_removed_per_commit

                # RQ 4.3
                self.typeAnnotation_changed_per_commit += stat.typeAnnotation_changed_per_commit
                self.list_typeAnnotation_changed_per_commit += stat.list_typeAnnotation_changed_per_commit

                # RQ 4.4
                self.annotation_related_insertion_edits_vs_all_commit += stat.annotation_related_insertion_edits_vs_all_commit

                # RQ 4.5
                self.annotation_related_deletion_edits_vs_all_commit += stat.annotation_related_deletion_edits_vs_all_commit

                # RQ 5
                self.matrix_commits_stars_annotations = np.concatenate((self.matrix_commits_stars_annotations,
                                                                        stat.matrix_commits_stars_annotations), axis=0)
                self.matrix_test_files_annotations = np.concatenate((self.matrix_test_files_annotations,
                                                                        stat.matrix_test_files_annotations), axis=0)
                self.matrix_files_annotations = np.concatenate((self.matrix_files_annotations,
                                                                        stat.matrix_files_annotations), axis=0)
                # RQ 6
                self.number_type_annotations_per_repo = merge_dictionaries(
                    [self.number_type_annotations_per_repo, stat.number_type_annotations_per_repo])

                # RQ 7
                self.typeLastProjectVersion_total += stat.typeLastProjectVersion_total
                self.typeLastProjectVersion_percentage += stat.typeLastProjectVersion_percentage
                self.typeLastProjectVersion_dict = merge_dictionaries(
                    [self.typeLastProjectVersion_dict, stat.typeLastProjectVersion_dict])

                # RQ 8
                self.typeAnnotation_year_analysis = merge_dictionaries(
                    [self.typeAnnotation_year_analysis, stat.typeAnnotation_year_analysis])

                # RQ 9
                self.typeAnnotation_commit_annotation_year_analysis = merge_dictionaries(
                    [self.typeAnnotation_commit_annotation_year_analysis,
                     stat.typeAnnotation_commit_annotation_year_analysis])

                self.typeAnnotation_commit_not_annotation_year_analysis = merge_dictionaries(
                    [self.typeAnnotation_commit_not_annotation_year_analysis,
                     stat.typeAnnotation_commit_not_annotation_year_analysis])

                #RQ 10
                year = 2014

                while year < 2021:
                    self.annotation_coverage[str(year)][0] += stat.annotation_coverage[str(year)][0]
                    self.annotation_coverage[str(year)][1] += stat.annotation_coverage[str(year)][1]
                    self.annotation_coverage[str(year)][2] += stat.annotation_coverage[str(year)][2]
                    self.annotation_coverage[str(year)][3] += stat.annotation_coverage[str(year)][3]
                    self.annotation_coverage[str(year)][4] += stat.annotation_coverage[str(year)][4]
                    self.annotation_coverage[str(year)][5] += stat.annotation_coverage[str(year)][5]
                    year += 1

                # RQ 11
                self.list_dev_dict.append(stat.dev_dict)

            except Exception as e:
                print('[Merging Error]', str(e))
                continue
