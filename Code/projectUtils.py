import config
from Code.lucaUtils import *


def write_results(statistics, code_changes):
    write_in_json(config.ROOT_DIR + "/Resources/Output/typeAnnotationChanges.json",
                  convert_list_in_list_of_dicts(code_changes))

    print('\nCode changes with type annotations found: ' + str(len(code_changes)))

    write_in_json(config.ROOT_DIR + "/Resources/Output/typeAnnotationStatistics.json",
                  convert_list_in_list_of_dicts([statistics]))


def myplot(statistics):
    """
    cartesian_graph_xy(config.ROOT_DIR + "/Resources/Output/plot_relation_stars_annotations",
                                         [row[1] for row in statistics.matrix_commits_stars_annotations],
                       [row[2] for row in statistics.matrix_commits_stars_annotations],
                       'GitHub Stars', 'Annotations Changes')"""

    cartesian_graph_xy(config.ROOT_DIR + "/Resources/Output/plot_relation_commits_annotations",
                       [row[0] for row in statistics.matrix_commits_stars_annotations],
                       [row[2] for row in statistics.matrix_commits_stars_annotations],
                       '# Commits', '# Annotations Changes')

    statistics.matrix_commits_stars_annotations = "See the plots."
