import difflib
import json
import os
import shutil
import sys

from io import StringIO
from collections import Counter

import numpy as np
from scipy.interpolate import make_interp_spline, BSpline

import matplotlib.pyplot as plt
import matplotlib.style as style

font_size = 12
plt.rcParams.update({'font.size': font_size})
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
        print("write_in_json error", e)

        with open(outputFilePath + '.txt', 'w') as f:
            for item in data:
                f.write("%s\n" % item)
        # print(data)
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


def pie_chart(outputFilePath, labels, sizes, title):
    # Data to plot
    # labels = 'Python', 'C++', 'Ruby', 'Java'
    # sizes = [215, 130, 245, 210]
    colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    explode = (0.1, 0, 0, 0, 0)  # explode 1st slice

    # Plot
    # plt.pie(sizes, labels=labels, colors=colors,
    #        autopct='%1.1f%%', shadow=True, startangle=140)

    # patches, texts, more = plt.pie(sizes, startangle=90, labels= labels, autopct='%1.0f%%')

    patches, texts, _ = plt.pie(sizes, shadow=True, explode=explode, startangle=140, autopct='%1.0f%%')

    plt.legend(patches, labels, loc="best")
    # Set aspect ratio to be equal so that pie is drawn as a circle.

    plt.tight_layout()

    plt.axis('equal')

    plt.title(title)

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()


def smooth_line_xy(outputFilePath, y, x_label=None, y_label=None, title=None, color1='blue', color2='red',
                   xlim=None,
                   ylim=None):
    plt.rcdefaults()
    plt.rcParams.update({'font.size': 15})
    y = sorted(y)
    x = list(range(len(y)))
    plt.yscale('log')

    # Calculate the simple average of the data
    y_mean = [numpy.mean(y)] * len(x)
    print(outputFilePath, "has a mean of", y_mean[0], "with len(x)=", len(x))

    fig, ax = plt.subplots()
    plt.xlim(min(x), max(x))
    pp = max(x)
    # plt.xticks(x)

    # Plot the data
    data_line = ax.plot(y, x, label='Repositories', color=(0.2, 0.4, 0.6, 0.6))

    # Plot the average line
    #mean_line = ax.plot(x, y_mean, label='Mean', linestyle='--', color='lightsalmon')

    # Make a legend
    legend = ax.legend(loc='upper left')

    plt.ylabel(y_label)
    plt.xlabel(x_label)
    # plt.xscale('log')

    # if title is not None:
    #    plt.title(title)

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()


def smooth_line_xy_multi(outputFilePath, dict, x_label=None, y_label=None, title=None, color1='blue', color2='red',
                         xlim=None,
                         ylim=None):
    plt.rcParams.update({'font.size': 14})

    x = []
    ret = []
    arg = []
    var = []

    for key in dict:
        x.append(str(int(key) + 1))
        arg.append(float(dict[key][0] / dict[key][1] * 100 if dict[key][1] else 0))
        ret.append(float(dict[key][2] / dict[key][3] * 100 if dict[key][3] else 0))
        var.append(float(dict[key][4] / dict[key][5] * 100 if dict[key][5] else 0))

    fig, ax = plt.subplots()

    ax.set_ylim([0, max(ret + arg + var)+2])

    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
    # Plot the data
    data_line = ax.plot(x, arg, label='Function arguments', marker='o', color=(0.2, 0.4, 0.6, 0.6))
    data_line = ax.plot(x, ret, label='Function returns', marker='x', color='lightsalmon')
    data_line = ax.plot(x, var, label='Variable assignments', marker='^', color='yellowgreen')

    # Make a legend
    legend = ax.legend(loc='upper left')

    plt.ylabel(y_label)
    plt.xlabel(x_label)
    # plt.xscale('log')

    # if title is not None:
    #    plt.title(title)

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()

def smooth_line_xy_double(outputFilePath, x, y, yy, x_label=None, y_label=None, title=None, color1='blue', color2='red',
                   xlim=None,
                   ylim=None):
    plt.rcParams.update({'font.size': 16})

    # fig, ax = plt.subplots()
    #
    # # Plot the data
    # data_line = ax.plot(x, y, label='Type Annotations (left)', color=(0.2, 0.4, 0.6, 0.6))
    #
    # # Plot the average line
    # mean_line = ax.plot(xx, y, label='Type Annotations per 1000 LoC (right)', linestyle='--', color='lightsalmon')
    #
    # # Make a legend
    # legend = ax.legend(loc='upper left')
    #
    # plt.ylabel(y_label)
    # plt.xlabel(x_label)
    # plt.xscale('log')

    fig, ax1 = plt.subplots()
    yyy = [0, 11, 26, 842, 1007, 1452, 7374]


    ax1.set_xlabel('Year')
    ax1.set_ylabel('Type annotations', color= 'black')
    ax1.plot(x, y, label='Type annotations (left)', marker='o', color=(0.2, 0.4, 0.6, 0.6))
    ax1.plot(x, yyy, label='STUB annotations (left)', marker='', color='yellowgreen')
    ax1.tick_params(axis='y', color='black')

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    ax2.set_ylabel('Type annotations per 1000 LoC', color='black')  # we already handled the x-label with ax1
    ax2.plot(x, yy, label='Type annotations per 1000 LoC (right)', marker='X', color='lightsalmon')
    ax2.tick_params(axis='y', color='black')


    # if title is not None:
    #    plt.title(title)

    # Make a legend
    fig.legend(loc='upper center', bbox_to_anchor=(0.517,1.13))

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
    plt.rcParams.update({'font.size': 38})

    x = [w.replace('optional', 'Optional') for w in x]
    x = [w.replace('none', 'None') for w in x]
    x = [w.replace('any', 'Any') for w in x]
    #x = [ 'User Type -> User Type' if len(w) > 50 else w for w in x]

    axes = plt.gca()
    if ylim is not None:
        #

        #plt.yticks(np.arange(0, ylim + 1, 5000))
        plt.yscale('log')
        plt.ylim(1, ylim)


    # if xlim is not None:
    #    axes.set_xlim([0, xlim])

    #plt.yscale('log')


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
    plt.rcParams.update({'font.size': font_size})
    if ylim is not None:
        axes.set_ylim([0, ylim])

    if xlim is not None:
        axes.set_xlim([0, xlim])

    plt.ylabel(y_label)
    plt.xlabel(x_label)

    #plt.yscale('log')

    plt.bar(numpy.array(x) - 0.2, numpy.array(y1), width=0.4, align='center',
            label='With annotations', color=(0.2, 0.4, 0.6, 0.6))
    plt.bar(numpy.array(x) + 0.2, numpy.array(y2), width=0.4, align='center',
            label='Without annotations', color='lightsalmon')
    plt.legend(loc='upper left')

    if title is not None:
        plt.title(title)

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()


def histogram_plot_xy(outputFilePath, x, x_label, y_label, xscale, yscale, title=None, bins='auto'):
    plt.rcdefaults()
    plt.rcParams.update({'font.size': 15})

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

    if yscale == 'log':
        plt.yscale(yscale)

    plt.hist(x, bins=bins, color=(0.2, 0.4, 0.6, 0.6))
    #values, base = np.histogram(x, bins=40)
    #cumulative = np.cumsum(values)
    #plt.plot(base[:-1], len(x)-cumulative,  color=(0.2, 0.4, 0.6, 0.6))

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()
    
def histogram_plot_xy2(outputFilePath, x, x_label, y_label, xscale, yscale, title=None, bins='auto'):
    plt.rcdefaults()
    plt.rcParams.update({'font.size': 15})
    
    x = [y for y in x if y >= 0]

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

    if yscale == 'log':
        plt.yscale(yscale)

    plt.hist(x, bins=bins, color=(0.2, 0.4, 0.6, 0.6))
    #values, base = np.histogram(x, bins=40)
    #cumulative = np.cumsum(values)
    #plt.plot(base[:-1], len(x)-cumulative,  color=(0.2, 0.4, 0.6, 0.6))

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()


def scatter_plot_xy(outputFilePath, x, y, x_label, y_label, xscale, yscale, title=None, color='blue', xlim=None,
                    ylim=None):
    plt.rcParams.update({'font.size': font_size})

    axes = plt.gca()
    if ylim is not None:
        axes.set_ylim([0, ylim])

    if xlim is not None:
        axes.set_xlim([0, xlim])

    plt.yscale(yscale)
    plt.xscale(xscale)

    # use the plot function
    plt.scatter(x, y, color=(0.2, 0.4, 0.6, 0.6))

    plt.ylabel(y_label)
    plt.xlabel(x_label)

    if title is not None:
        plt.title('title')

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()


def scatter_plot_xy_multi(outputFilePath, x, y, xx, yy, x_label, y_label, xscale, yscale, title=None, color='blue',
                          xlim=None,
                          ylim=None):
    plt.rcParams.update({'font.size': font_size})

    axes = plt.gca()
    if ylim is not None:
        axes.set_ylim([0, ylim])

    if xlim is not None:
        axes.set_xlim([0, xlim])

    plt.yscale(yscale)
    plt.xscale(xscale)

    # use the plot function
    plt.scatter(x, y, label='After 2017', color=(0.2, 0.4, 0.6, 0.6))
    plt.scatter(xx, yy, label='Between 2015 and 2017', color=("lightsalmon"))

    plt.legend(loc='upper left')

    plt.ylabel(y_label)
    plt.xlabel(x_label)

    if title is not None:
        plt.title('title')

    plt.savefig(outputFilePath, bbox_inches='tight')

    plt.figure()


def scatter_plot_xyz(outputFilePath, x, y, z, x_label, y_label, xscale, yscale, title=None, color='blue', xlim=None,
                     ylim=None):
    plt.rcParams.update({'font.size': font_size})

    axes = plt.gca()
    if ylim is not None:
        axes.set_ylim([0, ylim])

    if xlim is not None:
        axes.set_xlim([0, xlim])

    plt.yscale(yscale)
    plt.xscale(xscale)

    # use the plot function
    plt.scatter(x, y, label='With annotations', color=(0.2, 0.4, 0.6, 0.6))
    plt.scatter(z, y, label='Without annotations', color='lightsalmon')
    plt.legend(loc='upper left')

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
