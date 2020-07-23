import config
from Code.codeStatistics import CodeStatistics
from Code.lucaUtils import *
import numpy as np


def write_results(statistics, code_changes, commit_statistics):
    write_in_json(config.ROOT_DIR + "/Resources/Output/typeAnnotationChanges.json",
                  convert_list_in_list_of_dicts(code_changes))

    print('\nCode changes with type annotations found: ' + str(len(code_changes)))

    write_in_json(config.ROOT_DIR + "/Resources/Output/typeAnnotationCommitStatistics.json",
                  convert_list_in_list_of_dicts(commit_statistics))

    #  "jsonify" np.arrays
    statistics.matrix_commits_stars_annotations = statistics.matrix_commits_stars_annotations.tolist()

    # "unjsonify" the array -> np.array(from_json)

    write_in_json(config.ROOT_DIR + "/Resources/Output/typeAnnotationAllStatisticsRAW.json",
                  convert_list_in_list_of_dicts([statistics]))


def myplot(statistics):
    # RQ2.2
    bar_plot_xy(config.ROOT_DIR + "/Resources/Output/RQ2_2",
                statistics.typeAdded_dict.keys(),
                statistics.typeAdded_dict.values(), 'Top types added',
                'Occurrences',
                title='What are the top 5 types added?')

    # RQ2.4
    bar_plot_xy(config.ROOT_DIR + "/Resources/Output/RQ2_4",
                statistics.typeRemoved_dict.keys(),
                statistics.typeRemoved_dict.values(), 'Top types removed',
                'Occurrences',
                title='What are the top 5 types removed?')

    # RQ4.1
    histogram_plot_xy(config.ROOT_DIR + "/Resources/Output/RQ4_1",
                      statistics.list_typeAnnotation_added_per_commit,
                      'Percentage (%)', 'Occurrences', 'linear', 'log', 'Are types added along with other changes '
                                                                        'around this code or in commits that only add'
                                                                        ' types?' )

    # RQ4.2
    histogram_plot_xy(config.ROOT_DIR + "/Resources/Output/RQ4_2",
                      statistics.list_typeAnnotation_removed_per_commit,
                      'Percentage (%)', 'Occurrences', 'linear', 'log',
                      'Are types removed along with other changes around this code or in commits that only add types?'
                      )

    # RQ4.3
    histogram_plot_xy(config.ROOT_DIR + "/Resources/Output/RQ4_3",
                      statistics.list_typeAnnotation_changed_per_commit,
                      'Percentage (%)', 'Occurrences',  'linear', 'log',
                      'Are types changed along with other changes around this '
                      'code or in commits that only add types?')

    # RQ4.4
    #histogram_plot_xy(config.ROOT_DIR + "/Resources/Output/RQ4_4",
    #                  statistics.annotation_related_insertion_edits_vs_all_commit,
    #                  'Percentage (%)', 'Occurrences', 'linear', 'log',
    #                  'Percentage of annotation-related insertions to all edits per commit')

    # RQ4.5
    #histogram_plot_xy(config.ROOT_DIR + "/Resources/Output/RQ4_5",
    #                  statistics.annotation_related_deletion_edits_vs_all_commit,
    #                  'Percentage (%)', 'Occurrences', 'linear', 'log', 'Percentage of annotation-related deletions to '
    #                                                                    'all edits per commit')

    # RQ5
    scatter_plot_xy(config.ROOT_DIR + "/Resources/Output/RQ5_stars",
                    [row[1] for row in statistics.matrix_commits_stars_annotations],
                    [row[2] for row in statistics.matrix_commits_stars_annotations],
                    'GitHub Stars', 'Annotations Changes', 'log', 'log')

    scatter_plot_xy(config.ROOT_DIR + "/Resources/Output/RQ5_commits",
                    [row[0] for row in statistics.matrix_commits_stars_annotations],
                    [row[2] for row in statistics.matrix_commits_stars_annotations],
                    '# Commits', '# Annotations Changes', 'log', 'log')

    # RQ8
    bar_plot_xy(config.ROOT_DIR + "/Resources/Output/RQ8", [int(k) for k in statistics.typeAnnotation_year_analysis.keys()],
                [int(v) for v in statistics.typeAnnotation_year_analysis.values()], 'Type annotations per Year', 'Count',
                title='Total number of annotations over time, across all projects')

    # RQ9
    bar_plot_double_xy(config.ROOT_DIR + "/Resources/Output/RQ9",
                       [int(k) for k in statistics.typeAnnotation_commit_annotation_year_analysis.keys()],
                       [int(v) for v in statistics.typeAnnotation_commit_annotation_year_analysis.values()],
                       [int(v) for v in statistics.typeAnnotation_commit_not_annotation_year_analysis.values()], 'Annotation-relate commit',
                'Count', title='Total number of annotation-relate commit over time, across all project')

    # Variables are cleaned to have a better output
    statistics.matrix_commits_stars_annotations = "See the plots RQ5_commits and RQ5_stars."
    statistics.list_typeAnnotation_added_per_commit = "See the plot RQ4_1."
    statistics.list_typeAnnotation_removed_per_commit = "See the plot RQ4_2."
    statistics.list_typeAnnotation_changed_per_commit = "See the plot RQ4_3."
    statistics.annotation_related_insertion_edits_vs_all_commit = "See the plot RQ4_4."
    statistics.annotation_related_deletion_edits_vs_all_commit = "See the plot RQ4_5."
    statistics.typeAnnotation_year_analysis = "See the plot RQ8."
    statistics.typeAnnotation_commit_annotation_year_analysis = "See the plot RQ9."
    statistics.typeAnnotation_commit_not_annotation_year_analysis = "See the plot RQ9."

def load_final_statistics():
    finalStatistics = CodeStatistics()

    with open(config.ROOT_DIR + "/Resources/Output/typeAnnotationAllStatisticsRAW.json") as fh:
        allStatistics = json.load(fh)

    finalStatistics.total_repositories = allStatistics[0]['total_repositories']
    finalStatistics.total_commits = allStatistics[0]['total_commits']

    # RQ0
    #code_changes = stat.code_changes
    #commit_statistics = stat.commit_statistics
    finalStatistics.repo_with_types_changes = allStatistics[0]['repo_with_types_changes']
    finalStatistics.commits_with_typeChanges = allStatistics[0]['commits_with_typeChanges']
    finalStatistics.total_typeAnnotation_codeChanges = allStatistics[0]['total_typeAnnotation_codeChanges']

    # RQ1
    finalStatistics.insert_types = allStatistics[0]['insert_types']
    finalStatistics.remove_types = allStatistics[0]['remove_types']
    finalStatistics.modify_existing_types = allStatistics[0]['modify_existing_types']

    # RQ2.1
    finalStatistics.anyType_added = allStatistics[0]['anyType_added']
    finalStatistics.noneType_added = allStatistics[0]['noneType_added']
    finalStatistics.numericType_added = allStatistics[0]['numericType_added']
    finalStatistics.binarySequenceType_added = allStatistics[0]['binarySequenceType_added']
    finalStatistics.textSequenceType_added = allStatistics[0]['textSequenceType_added']
    finalStatistics.mappingTypes_added = allStatistics[0]['mappingTypes_added']
    finalStatistics.setTypes_added = allStatistics[0]['setTypes_added']
    finalStatistics.sequenceType_added = allStatistics[0]['sequenceType_added']
    finalStatistics.newType_added = allStatistics[0]['newType_added']
    finalStatistics.total_added = allStatistics[0]['total_added']

    # RQ2.2
    finalStatistics.typeAdded_dict = dict(tuple(tuple(x) for x in allStatistics[0]['typeAdded_dict']))

    # RQ2.3
    finalStatistics.anyType_removed = allStatistics[0]['anyType_removed']
    finalStatistics.noneType_removed = allStatistics[0]['noneType_removed']
    finalStatistics.numericType_removed = allStatistics[0]['numericType_removed']
    finalStatistics.binarySequenceType_removed = allStatistics[0]['binarySequenceType_removed']
    finalStatistics.textSequenceType_removed = allStatistics[0]['textSequenceType_removed']
    finalStatistics.mappingTypes_removed = allStatistics[0]['mappingTypes_removed']
    finalStatistics.setTypes_removed = allStatistics[0]['setTypes_removed']
    finalStatistics.sequenceType_removed = allStatistics[0]['sequenceType_removed']
    finalStatistics.newType_removed = allStatistics[0]['newType_removed']
    finalStatistics.total_removed = allStatistics[0]['total_removed']

    # RQ2.4
    finalStatistics.typeRemoved_dict = dict(tuple(tuple(x) for x in allStatistics[0]['typeRemoved_dict']))

    # RQ2.5
    finalStatistics.total_changed = allStatistics[0]['total_changed']
    finalStatistics.typeChanged_dict = dict(tuple(tuple(x) for x in allStatistics[0]['typeChanged_dict']))

    # RQ 3.1
    finalStatistics.functionArgsType_added = allStatistics[0]['functionArgsType_added']
    finalStatistics.functionReturnsType_added = allStatistics[0]['functionReturnsType_added']
    finalStatistics.variableType_added = allStatistics[0]['variableType_added']

    # RQ 3.2
    finalStatistics.functionArgsType_removed = allStatistics[0]['functionArgsType_removed']
    finalStatistics.functionReturnsType_removed = allStatistics[0]['functionReturnsType_removed']
    finalStatistics.variableType_removed = allStatistics[0]['variableType_removed']

    # RQ 3.3
    finalStatistics.functionArgsType_changed = allStatistics[0]['functionArgsType_changed']
    finalStatistics.functionReturnsType_changed = allStatistics[0]['functionReturnsType_changed']
    finalStatistics.variableType_changed = allStatistics[0]['variableType_changed']

    # RQ 4.1
    finalStatistics.typeAnnotation_added_per_commit = allStatistics[0]['typeAnnotation_added_per_commit']
    finalStatistics.list_typeAnnotation_added_per_commit = allStatistics[0]['list_typeAnnotation_added_per_commit']

    # RQ 4.2
    finalStatistics.typeAnnotation_removed_per_commit = allStatistics[0]['typeAnnotation_removed_per_commit']
    finalStatistics.list_typeAnnotation_removed_per_commit = allStatistics[0]['list_typeAnnotation_removed_per_commit']

    # RQ 4.3
    finalStatistics.typeAnnotation_changed_per_commit = allStatistics[0]['typeAnnotation_changed_per_commit']
    finalStatistics.list_typeAnnotation_changed_per_commit = allStatistics[0]['list_typeAnnotation_changed_per_commit']

    # RQ 4.4
    finalStatistics.annotation_related_insertion_edits_vs_all_commit = allStatistics[0]['annotation_related_insertion_edits_vs_all_commit']

    # RQ 4.5
    finalStatistics.annotation_related_deletion_edits_vs_all_commit = allStatistics[0]['annotation_related_deletion_edits_vs_all_commit']

    # RQ 5
    finalStatistics.matrix_commits_stars_annotations = np.array(allStatistics[0]['matrix_commits_stars_annotations'])

    # RQ 6
    finalStatistics.number_type_annotations_per_repo = dict(tuple(tuple(x) for x in allStatistics[0]['number_type_annotations_per_repo']))

    # RQ 7
    finalStatistics.typeLastProjectVersion_total = allStatistics[0]['typeLastProjectVersion_total']
    finalStatistics.typeLastProjectVersion_dict = dict(tuple(tuple(x) for x in allStatistics[0]['typeLastProjectVersion_dict']))

    # RQ 8
    finalStatistics.typeAnnotation_year_analysis = allStatistics[0]['typeAnnotation_year_analysis']

    # RQ 9
    finalStatistics.typeAnnotation_commit_annotation_year_analysis = allStatistics[0]['typeAnnotation_commit_annotation_year_analysis']

    finalStatistics.typeAnnotation_commit_not_annotation_year_analysis = allStatistics[0]['typeAnnotation_commit_not_annotation_year_analysis']


    return finalStatistics