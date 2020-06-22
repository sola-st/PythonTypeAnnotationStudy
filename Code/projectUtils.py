import config
from Code.lucaUtils import *


def write_results(statistics, code_changes):
    write_in_json(config.ROOT_DIR + "/Resources/Output/typeAnnotationChanges.json",
                  convert_list_in_list_of_dicts(code_changes))

    print('\nCode changes with type annotations found: ' + str(len(code_changes)))

    write_in_json(config.ROOT_DIR + "/Resources/Output/typeAnnotationStatistics.json",
                  convert_list_in_list_of_dicts([statistics]))


def myplot(statistics):
    scatter_plot_xy(config.ROOT_DIR + "/Resources/Output/RQ5_stars",
                    [row[1] for row in statistics.matrix_commits_stars_annotations],
                    [row[2] for row in statistics.matrix_commits_stars_annotations],
                    'GitHub Stars', 'Annotations Changes')

    scatter_plot_xy(config.ROOT_DIR + "/Resources/Output/RQ5_commits",
                    [row[0] for row in statistics.matrix_commits_stars_annotations],
                    [row[2] for row in statistics.matrix_commits_stars_annotations],
                    '# Commits', '# Annotations Changes')

    # RQ4.1
    histogram_plot_xy(config.ROOT_DIR + "/Resources/Output/RQ4_1",
                      statistics.list_typeAnnotation_added_per_commit,
                      'Type Annotations Added per Commit')

    # RQ4.2
    histogram_plot_xy(config.ROOT_DIR + "/Resources/Output/RQ4_2",
                      statistics.list_typeAnnotation_removed_per_commit,
                      'Type Annotations Removed per Commit',
                      'Are types removed along with other changes around this code or in commits that only add types?'
                      )

    # RQ4.3
    histogram_plot_xy(config.ROOT_DIR + "/Resources/Output/RQ4_3",
                      statistics.list_typeAnnotation_changed_per_commit,
                      'Type Annotations Changed per Commit',
                      'Are types changed along with other changes around this '
                      'code or in commits that only add types?')

    # RQ8
    histogram_plot_xy(config.ROOT_DIR + "/Resources/Output/RQ8",
                      statistics.annotation_related_edits_vs_all_commit,
                      'Percentage of annotation-related edits to all edits per commit')

    # RQ9
    bar_plot_xy(config.ROOT_DIR + "/Resources/Output/RQ9", [int(k) for k in statistics.typeAnnotation_year_analysis.keys()],
                [int(v) for v in statistics.typeAnnotation_year_analysis.values()], 'Type annotations per Year', 'Count',
                title='Total number of annotations over time, across all projects')

    # RQ10
    bar_plot_double_xy(config.ROOT_DIR + "/Resources/Output/RQ10",
                       [int(k) for k in statistics.typeAnnotation_commit_annotation_year_analysis.keys()],
                       [int(v) for v in statistics.typeAnnotation_commit_annotation_year_analysis.values()],
                       [int(v) for v in statistics.typeAnnotation_commit_not_annotation_year_analysis.values()], 'Annotation-relate commit',
                'Count', title='Total number of annotation-relate commit over time, across all project')

    # Variables are cleaned to have a better output
    statistics.matrix_commits_stars_annotations = "See the plots RQ5_commits and RQ5_stars."
    statistics.list_typeAnnotation_added_per_commit = "See the plot RQ4_1."
    statistics.list_typeAnnotation_removed_per_commit = "See the plot RQ4_2."
    statistics.list_typeAnnotation_changed_per_commit = "See the plot RQ4_3."
    statistics.annotation_related_edits_vs_all_commit = "See the plot RQ8."
    statistics.typeAnnotation_year_analysis = "See the plot RQ9."
    statistics.typeAnnotation_commit_annotation_year_analysis = "See the plot RQ10."
    statistics.typeAnnotation_commit_not_annotation_year_analysis = "See the plot RQ10."
