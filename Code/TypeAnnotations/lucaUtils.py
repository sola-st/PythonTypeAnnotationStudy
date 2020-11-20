"""
Author: Luca Di Grazia
My personal library with useful Python methods.
Tested on Python 3.7
Last update: July-2020
"""
import difflib
import json
import os
import shutil
import sys

from io import StringIO
from collections import Counter
from scipy.interpolate import make_interp_spline, BSpline

import matplotlib.pyplot as plt
import matplotlib.style as style
import numpy

"""
Sorting algorithms
"""


def sort_dictionary(data: dict):
    return sorted(data.items(), key=lambda x: x[1], reverse=True)


def sort_dictionary_reverse(data: dict):
    return sorted(data.items(), key=lambda x: x[1], reverse=False)


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


# Convert list of lists in a dictionary.
def convert_list_in_dict(list_of_list):
    return dict(tuple(tuple(x) for x in list_of_list))


# Convert list of variable, in list of dictionaries with variable name as key .
def convert_list_in_list_of_dicts(data: list) -> list:
    return [temp.__dict__ for temp in data]


# Merge a list of dictionaries
def merge_dictionaries(input):
    return sum((Counter(dict(z)) for z in input), Counter())


"""
Methods for working on files.
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


def delete_all_files_in_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


"""
Method to build x-y graphs.
"""


def pie_chart(outputFilePath, labels, sizes):
    # Data to plot
    # labels = 'Python', 'C++', 'Ruby', 'Java'
    # sizes = [215, 130, 245, 210]
    colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    # explode = (0.1, 0, 0, 0)  # explode 1st slice

    # Plot
    # plt.pie(sizes, labels=labels, colors=colors,
    #        autopct='%1.1f%%', shadow=True, startangle=140)

    patches, texts = plt.pie(sizes, colors=colors, startangle=90)
    plt.legend(patches, labels, loc="best")
    # Set aspect ratio to be equal so that pie is drawn as a circle.

    plt.tight_layout()

    plt.axis('equal')

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()


def smooth_line_xy(outputFilePath, y, x_label=None, y_label=None, title=None, color1='blue', color2='red',
                   xlim=None,
                   ylim=None):
    y = sorted(y)
    x = list(range(len(y)))

    # Calculate the simple average of the data
    y_mean = [numpy.mean(y)] * len(x)

    fig, ax = plt.subplots()

    # Plot the data
    data_line = ax.plot(x, y, label='Data', color=color1)

    # Plot the average line
    mean_line = ax.plot(x, y_mean, label='Mean', linestyle='--', color=color2)

    # Make a legend
    legend = ax.legend(loc='upper left')

    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.xscale('log')

    # if title is not None:
    #    plt.title(title)

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()


def cartesian_plot_xy(outputFilePath, x, y, x_label, y_label, title=None, color='blue', xlim=None, ylim=None):
    axes = plt.gca()
    if ylim is not None:
        axes.set_ylim([0, ylim])

    if xlim is not None:
        axes.set_xlim([0, xlim])

    plt.yscale('log')

    # use the plot function
    plt.plot(x, y, marker='', color=color, linewidth=2)

    plt.ylabel(y_label)
    plt.xlabel(x_label)

    if title is not None:
        plt.title('title')

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()


def bar_plot_xy(outputFilePath, x, y, x_label, y_label, title=None, color='blue', xlim=None, ylim=None):
    axes = plt.gca()
    if ylim is not None:
        axes.set_ylim([0, ylim])

    # if xlim is not None:
    #    axes.set_xlim([0, xlim])

    # plt.yscale('log')

    plt.ylabel(y_label)
    plt.xlabel(x_label)

    plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='right')

    # y_pos = np.arange(len(x))
    plt.bar(x, y, color=(0.2, 0.4, 0.6, 0.6))

    if title is not None:
        plt.title(title)

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()


def bar_plot_double_xy(outputFilePath, x, y1, y2, x_label=None, y_label=None, title=None, color1='blue', color2='red',
                       xlim=None,
                       ylim=None):
    axes = plt.gca()
    if ylim is not None:
        axes.set_ylim([0, ylim])

    if xlim is not None:
        axes.set_xlim([0, xlim])

    plt.ylabel(y_label)
    plt.xlabel(x_label)

    plt.yscale('log')

    plt.bar(numpy.array(x) - 0.2, numpy.array(y1), width=0.4, align='center', color=color1,
            label='Commits with annotations')
    plt.bar(numpy.array(x) + 0.2, numpy.array(y2), width=0.4, align='center', color=color2,
            label='Commits without annotations')
    plt.legend(loc='upper right')

    if title is not None:
        plt.title(title)

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()


def histogram_plot_xy(outputFilePath, x, x_label, y_label, xscale, yscale, title=None, bins='auto'):
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    if len(x) == 0:
        print('[Empty x]', title)
        return

    if title is not None:
        plt.title(title)

    plt.yscale(yscale)

    if xscale == 'log':
        plt.xscale(xscale)

    plt.hist(x, bins=bins, range=[0, max(x)])

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()


def scatter_plot_xy(outputFilePath, x, y, x_label, y_label, xscale, yscale, title=None, color='blue', xlim=None,
                    ylim=None):
    axes = plt.gca()
    if ylim is not None:
        axes.set_ylim([0, ylim])

    if xlim is not None:
        axes.set_xlim([0, xlim])

    plt.yscale(yscale)
    plt.xscale(xscale)

    # use the plot function
    plt.scatter(x, y)

    plt.ylabel(y_label)
    plt.xlabel(x_label)

    if title is not None:
        plt.title('title')

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()


def histogram_2d_plot_xy(outputFilePath, x, y, x_label, y_label, title=None, color='blue', xlim=None, ylim=None):
    axes = plt.gca()
    if ylim is not None:
        axes.set_ylim([0, ylim])

    if xlim is not None:
        axes.set_xlim([0, xlim])

    plt.yscale('log')

    # use the plot function
    plt.hist2d(x, y, bins=100)

    plt.ylabel(y_label)
    plt.xlabel(x_label)

    cbar = plt.colorbar()
    cbar.ax.set_ylabel('Counts')

    if title is not None:
        plt.title('title')

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()


# Diff
def dif_wr(d):
    for i, line in enumerate(d):
        sys.stdout.write('{} {}\n'.format(i + 1, line))


def map_diff_number_lines():
    file1 = """User1 fdsfds
    User2 US
    User3 US"""

    file2 = """User1 US
    User2 US
    User3 NG"""

    dif2 = difflib.unified_diff(StringIO(file1).readlines(),
                                StringIO(file2).readlines(),
                                fromfile='File_1.txt',
                                tofile='File_2.txt',
                                n=0,
                                lineterm="")
    dif_wr(dif2)
