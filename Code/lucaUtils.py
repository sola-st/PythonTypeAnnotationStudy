"""
Author: Luca Di Grazia
My personal library with useful Python methods.
Last update: June-2020
"""

import json
import matplotlib.pyplot as plt
import matplotlib.style as style

"""
Methods for multi-threading.
"""


# Chunkify list
def chunkify(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


"""
Data conversion and manipulation
"""


# Convert list of variable, in list of dictionaries with variable name as key .
def convert_list_in_list_of_dicts(data: list) -> list:
    return [temp.__dict__ for temp in data]


"""
Methods for writing files.
"""


# Method that writes a list in a json file.
def write_in_json(outputFilePath: str, data: list) -> None:
    try:
        json_file = json.dumps(data, indent=4)
    except Exception as e:
        print(e)
        return

    if '.json' not in outputFilePath:
        outputFilePath += '.json'

    with open(outputFilePath, "w") as f:
        f.write(json_file)
    f.close()


"""
Method to build x-y graphs.
"""


def cartesian_graph_xy(outputFilePath, x, y, x_label, y_label, title=None, color = 'blue', xlim = None, ylim = None):
    style.use('seaborn-paper')  # sets the size of the charts

    plt.rc('xtick', labelsize=18)
    plt.rc('ytick', labelsize=18)

    axes = plt.gca()
    if ylim is not None:
        axes.set_ylim([0, ylim])

    if xlim is not None:
        axes.set_xlim([0, xlim])

    # use the plot function
    plt.plot(x, y, marker='', color=color, linewidth=2)

    plt.ylabel(y_label, fontsize=18)
    plt.xlabel(x_label, fontsize=18)

    if title != None:
        plt.title('title')

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()
