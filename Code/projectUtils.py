import config
from Code.lucaUtils import write_in_json


def write_results(statistics, code_changes):
    write_in_json(config.ROOT_DIR + "/Resources/Output/typeAnnotationChanges.json", [change.__dict__ for change in code_changes])
    print('\nCode changes with type annotations found: ' + str(len(code_changes)))

    statistics_json = [[change.__dict__ for change in [statistics]], statistics.typeAdded_dict]
    write_in_json(config.ROOT_DIR + "/Resources/Output/typeAnnotationStatistics.json", statistics_json)
    print(statistics.typeAdded_dict)
