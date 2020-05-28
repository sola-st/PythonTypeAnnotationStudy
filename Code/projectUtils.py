import config
from Code.lucaUtils import *


def write_results(statistics, code_changes):
    write_in_json(config.ROOT_DIR + "/Resources/Output/typeAnnotationChanges.json",
                  convert_list_in_list_of_dicts(code_changes))

    print('\nCode changes with type annotations found: ' + str(len(code_changes)))

    write_in_json(config.ROOT_DIR + "/Resources/Output/typeAnnotationStatistics.json",
                  convert_list_in_list_of_dicts([statistics]))
