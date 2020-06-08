"""
Author: Luca Di Grazia
My personal library with useful Python methods.
Last update: June-2020
"""

import json
import matplotlib.pyplot as plt
import matplotlib.style as style
from scipy.interpolate import make_interp_spline, BSpline
from scipy.interpolate import splrep, splev
import numpy as np
import seaborn as sns

"""
Sorting algorithms
"""


def sort_dictionary(data: dict):
    return sorted(data.items(), key=lambda x: x[1], reverse=True)


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


def cartesian_plot_xy(outputFilePath, x, y, x_label, y_label, title=None, color='blue', xlim=None, ylim=None):
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

    plt.ylabel(y_label, fontsize=10)
    plt.xlabel(x_label, fontsize=10)

    if title is not None:
        plt.title('title')

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()


def bar_plot_xy(outputFilePath, x, y, x_label, y_label, title=None, color='blue', xlim=None, ylim=None):
    style.use('seaborn-paper')  # sets the size of the charts

    plt.rc('xtick', labelsize=18)
    plt.rc('ytick', labelsize=18)

    axes = plt.gca()
    if ylim is not None:
        axes.set_ylim([0, ylim])

    if xlim is not None:
        axes.set_xlim([0, xlim])

    plt.ylabel(y_label, fontsize=10, fontweight='bold', color='black')
    plt.xlabel(x_label, fontsize=10, fontweight='bold', color='black', horizontalalignment='center')

    y_pos = np.arange(len(x))
    plt.bar(y_pos, y, color=(0.2, 0.4, 0.6, 0.6))

    if title is not None:
        plt.title(title)

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()


def histogram_plot_xy(outputFilePath, x, x_label, title=None):
    sns.set(color_codes=True)

    plt.xlabel(x_label, fontsize=18, fontweight='bold', color='black', horizontalalignment='center')

    if title is not None:
        plt.title(title)

    # TODO: remove float axis
    sns_plot = sns.distplot(x, bins=20, kde=False, rug=True)

    fig = sns_plot.get_figure()

    fig.savefig(outputFilePath, bbox_inches='tight')

    # fig.figure()


def histogram_plot_xy2(outputFilePath, x, x_label, title=None):
    plt.xlabel(x_label, fontsize=18, fontweight='bold', color='black', horizontalalignment='center')

    if title is not None:
        plt.title(title)

    plt.hist(x, bins=20)

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()


def scatter_plot_xy(outputFilePath, x, y, x_label, y_label, title=None, color='blue', xlim=None, ylim=None):
    style.use('seaborn-paper')  # sets the size of the charts

    plt.rc('xtick', labelsize=18)
    plt.rc('ytick', labelsize=18)

    axes = plt.gca()
    if ylim is not None:
        axes.set_ylim([0, ylim])

    if xlim is not None:
        axes.set_xlim([0, xlim])

    # use the plot function
    plt.scatter(x, y)

    plt.ylabel(y_label, fontsize=18)
    plt.xlabel(x_label, fontsize=18)

    if title is not None:
        plt.title('title')

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()


def histogram_2d_plot_xy(outputFilePath, x, y, x_label, y_label, title=None, color='blue', xlim=None, ylim=None):
    style.use('seaborn-paper')  # sets the size of the charts

    plt.rc('xtick', labelsize=18)
    plt.rc('ytick', labelsize=18)

    axes = plt.gca()
    if ylim is not None:
        axes.set_ylim([0, ylim])

    if xlim is not None:
        axes.set_xlim([0, xlim])

    # use the plot function
    plt.hist2d(x, y, bins=100)

    plt.ylabel(y_label, fontsize=18)
    plt.xlabel(x_label, fontsize=18)

    cbar = plt.colorbar()
    cbar.ax.set_ylabel('Counts')

    if title is not None:
        plt.title('title')

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()
