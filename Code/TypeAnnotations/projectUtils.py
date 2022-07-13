import locale
import re
import statistics

import config
from Code.TypeAnnotations import codeStatistics
from Code.TypeAnnotations.codeStatistics import CodeStatistics
from Code.TypeAnnotations.Utils import *
import numpy as np
import pandas as pd
from lxml import html
from pyquery import PyQuery as pq, PyQuery
import json, requests


def write_results(statistics, code_changes, commit_statistics):
    write_in_json(config.ROOT_DIR + "/Resources/Output/typeAnnotationChanges.json",
                  convert_list_in_list_of_dicts(code_changes))

    print('\nCode changes with type annotations found: ' + str(len(code_changes)))

    write_in_json(config.ROOT_DIR + "/Resources/Output/typeAnnotationCommitStatistics.json",
                  convert_list_in_list_of_dicts(commit_statistics))

    #  "jsonify" np.arrays
    statistics.matrix_commits_stars_annotations = statistics.matrix_commits_stars_annotations.tolist()
    statistics.matrix_files_annotations = statistics.matrix_files_annotations.tolist()
    statistics.matrix_test_files_annotations = statistics.matrix_test_files_annotations.tolist()

    # "unjsonify" the array -> np.array(from_json)

    write_in_json(config.ROOT_DIR + "/Resources/Output/typeAnnotationAllStatisticsRAW.json",
                  convert_list_in_list_of_dicts([statistics]))


def compute_correlations(commits_stars_annotations):
    projects = pd.DataFrame(commits_stars_annotations)
    projects.columns = ["commits", "stars", "annotations", "n_forks", "n_issues", "n_test_files", "n_non_test_files",
                        "n_dev", "funct_type_avg", "fuct_no_type_avg"]
    projects_with_annotations = projects[projects.annotations > 0]
    print(f"Computing correlations across {len(projects)} projects, {len(projects_with_annotations)} with annotations ")
    print(f"  All projects:")
    print(f"    Correlation between annotations and commits: {projects['commits'].corr(projects['annotations'])}")
    print(f"    Correlation between annotations and stars: {projects['commits'].corr(projects['stars'])}")
    print(f"  Projects with annotations:")
    print(
        f"    Correlation between annotations and commits: {projects_with_annotations['commits'].corr(projects_with_annotations['annotations'])}")
    print(
        f"    Correlation between annotations and stars: {projects_with_annotations['stars'].corr(projects_with_annotations['annotations'])}")
    print(
        f"    Correlation between annotations and n_forks: {projects_with_annotations['n_forks'].corr(projects_with_annotations['annotations'])}")
    print(
        f"    Correlation between annotations and n_issues: {projects_with_annotations['annotations'].corr(projects_with_annotations['n_issues'])}")
    print(
        f"    Correlation between annotations and n_test_files: {projects_with_annotations['annotations'].corr(projects_with_annotations['n_test_files'])}")
    print(
        f"    Correlation between annotations and n_non_test_files: {projects_with_annotations['annotations'].corr(projects_with_annotations['n_non_test_files'])}")
    print(
        f"    Correlation between annotations and n_dev: {projects_with_annotations['annotations'].corr(projects_with_annotations['n_dev'])}")
    print(
        f"    Correlation between annotations and funct_type_avg: {projects_with_annotations['annotations'].corr(projects_with_annotations['funct_type_avg'])}")
    print(
        f"    Correlation between annotations and fuct_no_type_avg: {projects_with_annotations['annotations'].corr(projects_with_annotations['fuct_no_type_avg'])}")


def compute_correlations2(commits_stars_annotations):
    projects = pd.DataFrame(commits_stars_annotations)
    projects.columns = ["funct", "cov", "annotations"]
    projects_with_annotations = projects[projects.annotations > 0]
    print(f"Computing correlations across {len(projects)} projects, {len(projects_with_annotations)} with annotations ")
    print(f"  All projects:")
    print(f" no test   Correlation between annotations and funct: {projects['funct'].corr(projects['annotations'])}")
    print(f" no test    Correlation between cov and funct: {projects['funct'].corr(projects['cov'])}")
    print(f"  Projects with annotations:")
    print(
        f" no test    Correlation between annotations and funct: {projects_with_annotations['funct'].corr(projects_with_annotations['annotations'])}")
    print(
        f" no test    Correlation between cov and funct: {projects_with_annotations['funct'].corr(projects_with_annotations['cov'])}")


def myplot(statistics):

    count_optional = 0

    for x in statistics.typeChanged_dict_var:
        if "optional" in x:
            count_optional += statistics.typeChanged_dict_var[x]

    for x in statistics.typeChanged_dict_arg:
        if "optional" in x:
            count_optional += statistics.typeChanged_dict_arg[x]

    for x in statistics.typeChanged_dict_ret:
        if "optional" in x:
            count_optional += statistics.typeChanged_dict_ret[x]

    print(f"optional: {count_optional}")

    statistics.typeChanged_dict_var = sum_type_changes(statistics.typeChanged_dict_var)
    statistics.typeChanged_dict_arg = sum_type_changes(statistics.typeChanged_dict_arg)
    statistics.typeChanged_dict_ret = sum_type_changes(statistics.typeChanged_dict_ret)

    # RQ2.3
    bar_plot_xy(config.ROOT_DIR + "/Resources/Output/TopChanged_arg.pdf",
                list(statistics.typeChanged_dict_arg.keys())[:5],
                list(statistics.typeChanged_dict_arg.values())[:5], 'Type changes in function arguments',
                'Occurrences\n(log scale)', ylim=50000)

    # RQ2.3
    bar_plot_xy(config.ROOT_DIR + "/Resources/Output/TopChanged_ret.pdf",
                list(statistics.typeChanged_dict_ret.keys())[:5],
                list(statistics.typeChanged_dict_ret.values())[:5], 'Type changes in function return',
                'Occurrences\n(log scale)', ylim=50000)

    # RQ2.3
    bar_plot_xy(config.ROOT_DIR + "/Resources/Output/TopChanged_var.pdf",
                list(statistics.typeChanged_dict_var.keys())[:5],
                list(statistics.typeChanged_dict_var.values())[:5], 'Type changes in variable assignment',
                'Occurrences\n(log scale)', ylim=50000)


    smooth_line_xy_multi(config.ROOT_DIR + "/Resources/Output/elements_annotated.pdf",
                        statistics.annotation_coverage,
                       x_label="Year",
                      y_label="Type annotation coverage",
                     title="Presence of type annotations in\nthe last version of the repositories.",
                    color1='blue', color2='red',
                   xlim=None,
                 ylim=None)

    llll = []
    loc = []
    years = []
    for lll in statistics.annotation_coverage:
        years.append(str(int(lll)+1))
        llll.append(statistics.annotation_coverage[lll][0]+statistics.annotation_coverage[lll][2]+statistics.annotation_coverage[lll][4])
        loc.append((statistics.annotation_coverage[lll][0]+statistics.annotation_coverage[lll][2]+statistics.annotation_coverage[lll][4])/((statistics.annotation_coverage[lll][1]+statistics.annotation_coverage[lll][3]+statistics.annotation_coverage[lll][5]+1)/1000))

    smooth_line_xy_double(config.ROOT_DIR + "/Resources/Output/annotationsPerYear2.pdf",
                          years,
                          llll,
                          loc,
                          x_label="Year",
                          y_label="Type annotations",
                          color1='blue', color2='red',
                          xlim=None,
                          ylim=None)

    from collections import Counter
    A = Counter(statistics.insert_types)
    B = Counter(statistics.remove_types)
    C = Counter(statistics.modify_existing_types)
    merged = dict(A + B + C)

    A = Counter(merged)
    B = Counter(statistics.loc_year_edit)
    merged2 = dict({k: A[k] / (B[k]/1000) for k in A})

    merged = dict(sorted(merged.items()))
    merged2 = dict(sorted(merged2.items()))


    # Total number of commits in each year
    for key in list(statistics.commit_year_dict.keys()):
        if int(key) < 2010:
            del statistics.commit_year_dict[key]

    statistics.commit_year_dict = dict(sort_dictionary(statistics.commit_year_dict))

    list_top_1_developers = []
    list_link_repo = []

    i = -1
    for dictionary in statistics.list_dev_plot:
        dictionary2 = {}
        i += 1
        for key in dictionary:
            if dictionary[key] == 0:
                list_link_repo.append("https://api.github.com/repos/" + key.replace("-", "/", 1))

        total = sum(dictionary.values())
        if total == 0:
            continue

        for key in dictionary.keys():
            dict_temp = statistics.list_dev_dict_total[i]
            if dict_temp[key] > 0:
                dictionary2[key] = dictionary[key] / total * 100

        dictionary2 = dict(sort_dictionary(dictionary2)[:1])
        key = next(iter(dictionary2))

        list_top_1_developers.append(float(dictionary[key] / statistics.list_dev_dict_total[i][key] * 100))

    # RQ4
    #print("% type annotation only commits", sum(float(i) >= 95.0 for i in statistics.list_typeAnnotation_changed_per_commit)/len(statistics.list_typeAnnotation_changed_per_commit)*100)

    histogram_plot_xy2(config.ROOT_DIR + "/Resources/Output/perc_annotations_lines_per_commit.pdf",
                      statistics.list_typeAnnotation_changed_per_commit,
                      'Percentage of annotation-related lines among\nall inserted, removed and changed lines',
                      'Number of commits (log scale)', 'linear', 'log', bins=20)

    # RQ4.4
    list_ann = []
    list_err = []

    # RQ5
    list_2018_more_ann = []
    list_2018_more_comm = []
    list_2015_more_ann = []
    list_2015_more_comm = []

    for array in statistics.matrix_commits_stars_annotations:
        if int(array[3]) > 0:
            if int(array[0]) >= 2018:
                list_2018_more_ann.append(int(array[3]))
                list_2018_more_comm.append(int(array[1]))
            elif int(array[0]) >= 2015:
                list_2015_more_ann.append(int(array[3]))
                list_2015_more_comm.append(int(array[1]))


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
    file = open(config.ROOT_DIR + "/Resources/Output/typeAnnotationChanges.json")
    fh = file.read()
    list = re.findall(r'\'life_time\': \'[-0-9]+\'', fh)
    list2 = re.findall(r'\'change_num\': \'[-0-9]+\'', fh)
    list3 = re.findall(r'\'url_last_change\': \'(.*?)\'', fh)
   
    for s in file:
        list = re.findall(r'[a-z]+', s)

    n_changes2 = []
    for u in list3:
        if u == '':
            n_changes2.append(0)
        else:
            m = set(re.findall('/commit/(.+?)#diff', u))
            n_changes2.append(len(m))

    list_lifetime = []
    n_changes = []

    for item in list:
        list_lifetime.append(int(re.findall('[-0-9]+', item )[0]))

    for item in list2:
        n_changes.append(int(re.findall('[-0-9]+', item )[0]))

    list_lifetime = [x for x in list_lifetime if x != -1]
    tot_ch = 1414936
    n_changes = [x for x in n_changes2 if x > 0]
    #print(f"% never changed {100- len(n_changes)/tot_ch*100}")

    try: 
        print(
            f"Lifetime: mean {statistics.mean(list_lifetime)}, min {min(list_lifetime)}, max {max(list_lifetime)}, count {len(list_lifetime)}")

        print(
            f"# changes:  mean {statistics.mean(n_changes)}, min {min(n_changes)}, max {max(n_changes)}, count {len(n_changes)}")

        histogram_plot_xy(config.ROOT_DIR + "/Resources/Output/num_changes.pdf",
                          n_changes,
                          'Number of changes for a type annotation',
                          'Type annotations (log scale)', 'linear', 'log', bins=26)
    except:
        pass

    finalStatistics = CodeStatistics()

    with open(config.ROOT_DIR + "/Resources/Output/typeAnnotationAllStatisticsRAW.json") as fh:
        allStatistics = json.load(fh)

    finalStatistics.total_repositories = allStatistics[0]['total_repositories']
    finalStatistics.total_commits = allStatistics[0]['total_commits']
    finalStatistics.commit_year_dict = allStatistics[0]['commit_year_dict']
    finalStatistics.loc_year_edit = allStatistics[0]['loc_year_edit']

    # RQ0
    # code_changes = stat.code_changes
    # commit_statistics = stat.commit_statistics
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
    finalStatistics.typeChanged_dict_ret = dict(tuple(tuple(x) for x in allStatistics[0]['typeChanged_dict_ret']))
    finalStatistics.typeChanged_dict_var = dict(tuple(tuple(x) for x in allStatistics[0]['typeChanged_dict_var']))
    finalStatistics.typeChanged_dict_arg = dict(tuple(tuple(x) for x in allStatistics[0]['typeChanged_dict_arg']))

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
    finalStatistics.annotation_related_insertion_edits_vs_all_commit = allStatistics[0][
        'annotation_related_insertion_edits_vs_all_commit']

    # RQ 4.5
    finalStatistics.annotation_related_deletion_edits_vs_all_commit = allStatistics[0][
        'annotation_related_deletion_edits_vs_all_commit']

    # RQ 5
    finalStatistics.matrix_commits_stars_annotations = np.array(allStatistics[0]['matrix_commits_stars_annotations'])
    finalStatistics.matrix_files_annotations = np.array(allStatistics[0]['matrix_files_annotations'])
    finalStatistics.matrix_test_files_annotations = np.array(allStatistics[0]['matrix_test_files_annotations'])

    # RQ 6
    finalStatistics.number_type_annotations_per_repo = dict(
        tuple(tuple(x) for x in allStatistics[0]['number_type_annotations_per_repo']))

    # RQ 7
    finalStatistics.typeLastProjectVersion_total = allStatistics[0]['typeLastProjectVersion_total']
    finalStatistics.typeLastProjectVersion_percentage = allStatistics[0]['typeLastProjectVersion_percentage']
    finalStatistics.typeLastProjectVersion_dict = dict(
        tuple(tuple(x) for x in allStatistics[0]['typeLastProjectVersion_dict']))

    # RQ 8
    finalStatistics.typeAnnotation_year_analysis = allStatistics[0]['typeAnnotation_year_analysis']

    # RQ 9
    finalStatistics.typeAnnotation_commit_annotation_year_analysis = allStatistics[0][
        'typeAnnotation_commit_annotation_year_analysis']

    finalStatistics.typeAnnotation_commit_not_annotation_year_analysis = allStatistics[0][
        'typeAnnotation_commit_not_annotation_year_analysis']

    # RQ 10
    finalStatistics.annotation_coverage = allStatistics[0]['annotation_coverage']

    # RQ 11
    finalStatistics.list_dev_dict = allStatistics[0]['list_dev_dict']
    finalStatistics.list_dev_dict_total = allStatistics[0]['list_dev_dict_total']

    finalStatistics.list_dev_plot = allStatistics[0]['list_dev_dict']

    return finalStatistics

def sum_type_changes(typeChanged_dict):
    dict_temp = {}
    anyType_list = ['any']
    noneType_list = ['none']
    numericType_list = ['int', 'float', 'complex', 'decimal', 'optional']
    textSequenceType_list = ['str']
    binarySequenceType_list = ['bytes', 'bytearray', 'memoryview']
    setTypes_list = ['set', 'frozenset']
    mappingType_list = ['dict', 'union']

    types = anyType_list + noneType_list + numericType_list + textSequenceType_list + binarySequenceType_list + setTypes_list + mappingType_list
    delete = []

    for x in typeChanged_dict:
        s = x.split(" -> ")
        old = s[0].replace(",", "[").split("[")
        new = s[1].replace(",", "[").split("[")
        b = False
        b2 = False
        temp = ''
        temp1 = []
        for t in old:
            for y in types:
                if t.replace(']', "").replace(' ', '') in y:
                    temp1.append(y)
                    break

        if len(old) > len(temp1):
            # temp1 = 'User Type'
            b = True

        temp2 = []
        for t in new:
            for y in types:
                if t.replace(']', "").replace(' ', '') in y:
                    temp2.append(y)
                    break

        if len(new) > len(temp2):
            # temp2 = 'User Type'
            b2 = True

        if b:
            temp = 'UserType' + ' -> '
        else:
            temp = s[0] + ' -> '

        if b2:
            temp += 'UserType'
        else:
            temp += s[1]

        if b or b2:
            delete.append(x)
            if temp not in dict_temp:
                dict_temp[temp] = typeChanged_dict[x]
            else:
                dict_temp[temp] = dict_temp[temp] + typeChanged_dict[x]

    for x in delete:
        del typeChanged_dict[x]

    for x in dict_temp:
        typeChanged_dict[x] = dict_temp[x]

    return dict(sort_dictionary(typeChanged_dict))
