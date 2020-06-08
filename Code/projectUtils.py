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


    #RQ4.1
    histogram_plot_xy2(config.ROOT_DIR + "/Resources/Output/RQ4_1",
                      statistics.list_typeAnnotation_added_per_commit,
                      'Type Annotations Added per Commit')

    # RQ4.2
    histogram_plot_xy2(config.ROOT_DIR + "/Resources/Output/RQ4_2",
                      statistics.list_typeAnnotation_removed_per_commit,
                      'Type Annotations Removed per Commit', 'Are types removed along with other changes around this '
                                                             'code or in commits that only add types?')

    # Variables are cleaned to have a better output
    statistics.matrix_commits_stars_annotations = "See the plots."
    statistics.list_typeAnnotation_added_per_commit = "See the plot RQ4_1."
    statistics.list_typeAnnotation_removed_per_commit = "See the plot RQ4_2."

