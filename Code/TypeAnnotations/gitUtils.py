import csv
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import time
from collections import defaultdict
import numpy as np

import pygit2 as git
from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE
from typing import List

import config
from Code.TypeAnnotations.codeChange import CommitStatistics
from Code.TypeAnnotations.codeChangeExtraction import TypeAnnotationExtractionFirstCommit, \
    TypeAnnotationExtractionLast, type_annotation_in_last_version, last_version_analysis, \
    TypeAnnotationExtractionLast_life, extract_from_snippet
from Code.TypeAnnotations.codeStatistics import CodeStatistics
from Code.TypeAnnotations.Utils import write_in_json, convert_list_in_list_of_dicts
from Code.TypeErrors.TypeAnnotationCounter import count_type_annotations, extract_from_file


def repo_cloning(filenameInput: str, pathOutput: str, count: List[int]) -> None:
    with open(filenameInput) as fh:
        articles = json.load(fh)

    article_urls = [article['html_url'] for article in articles]

    i = 0
    for link in article_urls:
        i+=1
        #if i >50:
         #   print("new year")
          #  return

        count[0] += 1

        # out = link.rsplit('/', 1)[-1].replace('.git', '')
        out = re.sub('https://github.com/', '', link).replace('/', '-')

        if os.path.isdir(pathOutput + '/' + out):
            print(str(count) + ' Already cloned', link)

            continue

        else:
            print(str(count) + ' Cloning ' + link)
            try:
                git.clone_repository(link, pathOutput + '/' + out)
            except Exception as e:
                print('[Error] cloning repository:', str(e))
                continue


def repo_cloning_csv( pathOutput: str) -> None:
    columns = defaultdict(list)  # each value in each column is appended to a list

    with open(config.ROOT_DIR + '/Resources/Input/topJavaMavenProjects.csv') as f:
        reader = csv.DictReader(f)  # read rows into a dictionary format
        for row in reader:  # read a row as {column1: value1, column2: value2,...}
            for (k, v) in row.items():  # go over each column name and value
                columns[k].append(v)  # append the value into the appropriate list
                # based on column name k

    print(columns['repository_url'])

    i = 0
    for link in columns['repository_url']:
        i += 1

        # out = link.rsplit('/', 1)[-1].replace('.git', '')
        out = re.sub('https://github.com/', '', link).replace('/', '-')

        if os.path.isdir(pathOutput + '/' + out):
            print(str(i) + ') Already cloned', link)

            continue

        else:
            print(str(i) + ') Cloning ' + link)
            try:
                git.clone_repository(link, pathOutput + '/' + out)
            except Exception as e:
                print('[Error] cloning repository:', str(e))
                continue

def query_repo_get_changes(repo_name):  # statistics, pointer, dirlist_len):
    start = time.time()
    file_extension = '.py'
    statistics = CodeStatistics()

    try:
        tot_this_repo_commit = 0
        statistics.dev_dict[repo_name] = 0
        statistics.dev_dict_total[repo_name] = 0
        # tot_this_repo_commit_with_annotations = [0]
        commit_with_annotations_this_repo = [0]
        at_least_one_type_change = [0]
        commit_set = set()
        n_test_files = 0
        n_non_test_files = 0

        # lock.acquire()
        statistics.number_type_annotations_per_repo[repo_name] = 0
        statistics.total_repositories += 1

        if config.NORMAL_PRINT:
            print("[Working]", repo_name)
        # lock.release()

        if not config.TEST:
            type_annotation_in_last_version(repo_name, statistics)
            #last_version_analysis(repo_name, statistics)
        else:
            statistics.typeLastProjectVersion_total = 1

        try:
            repo = git.Repository(config.ROOT_DIR + "/GitHub/" + repo_name)
        except:
            return

        remote_url = None
        for r in repo.remotes:
            remote_url = r.url.split('.git')[0]

        last_commit = None

        for l in repo.head.log():
            last_commit = l.oid_new

        if statistics.typeLastProjectVersion_total > 0:
            # Go through each commit starting from the most recent commit
            commit_temp = 'e0'
            for commit in repo.walk(last_commit, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE):
                try:
                    #print(str(commit.hex))
                    #if commit.hex != '0d2f5f328ce14fcaed450ee218d44aa0eb32fe4a' and commit.hex != '304de58f8db607913feb326e89243082e27c4c50':  # b86598886ea50c5259982ac18a692748bd3ba402
                     #   continue
                    commit_year = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(commit.commit_time))[:4]
                    commit_month = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(commit.commit_time))[5:7]
                    commit_day = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(commit.commit_time))[8:10]

                    if  int(commit_year) < 2014 or int(commit_year) > 2020:
                        continue

                    #if int(commit_month) <= 12:
                    if commit_year not in statistics.commit_year_dict:
                        statistics.commit_year_dict[str(commit_year)] = 1
                    else:
                        statistics.commit_year_dict[str(commit_year)] += 1


                    if int(commit_month) < 9:
                        commit_temp = commit.hex
                    else:
                        if commit_temp != 'e0':
                            commit_set.add(commit_year + commit_temp)

                    tot_line_inserted = 0
                    tot_line_removed = 0
                    typeannotation_line_inserted = [0]
                    typeannotation_line_removed = [0]
                    typeannotation_line_changed = [0]
                    list_line_added = [0]
                    list_line_removed = [0]
                    old_len = len(statistics.code_changes)

                    # lock.acquire()
                    statistics.total_commits += 1
                    # lock.release()

                    tot_this_repo_commit += 1

                    try:
                        if commit.author.email not in statistics.dev_dict_total:
                            statistics.dev_dict_total[str(commit.author.email)] = 1
                        else:
                            statistics.dev_dict_total[str(commit.author.email)] += 1
                    except:
                        pass

                    num_parents = len(
                        commit.parents)  # Do not want to include merges for now, hence we check if the number of parents is 'one'
                    if num_parents >= 0:  # and commit_message_contains_query(commit.message, query_terms):
                        # Diff between the current commit and its parent
                        # threads: list = []
                        diff = []

                        if num_parents == 1:
                            diff = repo.diff(commit.hex + '^', commit.hex)


                            tot_line_removed += diff.stats.deletions
                            tot_line_inserted += diff.stats.insertions

                            try:
                                if commit_year not in statistics.loc_year_edit:
                                    statistics.loc_year_edit[commit_year] = diff.stats.deletions + diff.stats.insertions
                                else:
                                    statistics.loc_year_edit[commit_year] += diff.stats.deletions + diff.stats.insertions
                            except:
                                pass

                        elif num_parents == 0: # First commit
                            diff = repo.diff(commit.hex)
                            tot_line_inserted += diff.stats.insertions

                            try:
                                if commit_year not in statistics.loc_year_edit:
                                    statistics.loc_year_edit[commit_year] = diff.stats.insertions
                                else:
                                    statistics.loc_year_edit[commit_year] += diff.stats.insertions
                            except:
                                pass


                        for patch in diff:
                            try:
                                if str(patch.delta.old_file.path)[-3:] != file_extension or \
                                        str(patch.delta.new_file.path)[-3:] != file_extension:
                                    continue
                            except Exception as e:
                                return

                            if not hasattr(diff,"patchid"):
                                continue

                            try:
                                if "test" in str(patch.delta.old_file.path) != file_extension or \
                                        "test" in str(patch.delta.new_file.path) != file_extension:
                                    n_test_files += 1
                                else:
                                    n_non_test_files += 1
                            except Exception as e:
                                return

                            TypeAnnotationExtractionLast_life(config.ROOT_DIR + "/GitHub/", repo_name, commit, patch,
                                                        remote_url + '/commit/' + commit.hex + '#diff-' + diff.patchid.hex,
                                                        statistics,  # lock, logging,
                                                        at_least_one_type_change,
                                                        statistics.code_changes, typeannotation_line_inserted,
                                                        typeannotation_line_removed, typeannotation_line_changed,
                                                        list_line_added,
                                                        list_line_removed, commit_year, commit_month, commit_day)

                    added_per_commit_percentage = 0
                    removed_per_commit_percentage = 0
                    changed_per_commit_percentage = 0
                    # RQ 4.1
                    try:
                        if typeannotation_line_inserted[0] - typeannotation_line_changed[0] > 0:
                            added_per_commit_percentage = (typeannotation_line_inserted[0] - typeannotation_line_changed[0]) / (
                                    tot_line_inserted - typeannotation_line_changed[0]) * 100

                            if added_per_commit_percentage <= 100:
                                statistics.list_typeAnnotation_changed_per_commit.append(added_per_commit_percentage)
                            else:
                                print(repo_name, commit_year, str(commit.hex))

                    except:
                        pass

                    # RQ 4.2
                    try:
                        if typeannotation_line_removed[0] - typeannotation_line_changed[0] > 0:

                            removed_per_commit_percentage = (typeannotation_line_removed[0] - typeannotation_line_changed[
                                0]) / (
                                                                    tot_line_removed - typeannotation_line_changed[0]) * 100
                            if removed_per_commit_percentage <= 100:
                                statistics.list_typeAnnotation_changed_per_commit.append(removed_per_commit_percentage)
                            else:
                                print(repo_name, commit_year, str(commit.hex))

                    except:
                        pass

                    # RQ 4.3
                    try:
                        if typeannotation_line_changed[0] > 0:
                            changed_per_commit_percentage = (typeannotation_line_changed[0]) / (
                                    tot_line_removed + tot_line_inserted - typeannotation_line_changed[0]) * 100

                            if changed_per_commit_percentage <= 100:
                                statistics.list_typeAnnotation_changed_per_commit.append(changed_per_commit_percentage)
                            else:
                                print(repo_name, commit_year, str(commit.hex))

                    except:
                        pass

                    if len(statistics.code_changes) > old_len:
                        # lock.acquire()
                        statistics.commits_with_typeChanges += 1

                        try:
                            if commit.author.email not in statistics.dev_dict:
                                statistics.dev_dict[str(commit.author.email)] = 1
                            else:
                                statistics.dev_dict[str(commit.author.email)] += 1
                        except:
                            pass

                        if added_per_commit_percentage <= 100 and removed_per_commit_percentage <= 100 and changed_per_commit_percentage <= 100:
                            try:
                                temp = CommitStatistics(str(remote_url + '/commit/' + commit.hex), str(commit_year),
                                                        str(len(statistics.code_changes) - old_len),
                                                        str(round(added_per_commit_percentage, 1)) + ' %',
                                                        str(round(removed_per_commit_percentage, 1)) + ' %',
                                                        str(round(changed_per_commit_percentage, 1)) + ' %',
                                                        str(typeannotation_line_inserted[0] - typeannotation_line_changed[0]),
                                                        str(typeannotation_line_removed[0] - typeannotation_line_changed[0]),
                                                        str(typeannotation_line_changed[0]))
                                statistics.commit_statistics.append(temp)
                            except Exception as e:
                                print('Error appending commit stat: ' + str(e))

                        # RQ9
                        if commit_year not in statistics.typeAnnotation_commit_annotation_year_analysis:
                            statistics.typeAnnotation_commit_annotation_year_analysis[commit_year] = 1
                        else:
                            statistics.typeAnnotation_commit_annotation_year_analysis[commit_year] += 1

                        if commit_year not in statistics.typeAnnotation_commit_not_annotation_year_analysis:
                            statistics.typeAnnotation_commit_not_annotation_year_analysis[commit_year] = 0

                        # RQ8
                        if commit_year not in statistics.typeAnnotation_year_analysis:
                            statistics.typeAnnotation_year_analysis[commit_year] = len(statistics.code_changes) - old_len
                        else:
                            statistics.typeAnnotation_year_analysis[commit_year] += len(statistics.code_changes) - old_len
                        # lock.release()
                        commit_with_annotations_this_repo[0] += 1
                    else:
                        if commit_year in statistics.typeAnnotation_commit_not_annotation_year_analysis:
                            statistics.typeAnnotation_commit_not_annotation_year_analysis[commit_year] += 1
                except:
                    continue
        else:
            # Go through each commit starting from the most recent commit
            for commit in repo.walk(last_commit, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE):
                commit_year = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(commit.commit_time))[:4]
                if int(commit_year) < 2015:
                    continue

                statistics.total_commits += 1
                tot_this_repo_commit += 1

        #function_size_correlation(config.ROOT_DIR + "/GitHub/" + repo_name, statistics)

        try:
            if len(statistics.dict_funct_call_no_types) > 0:

                fuct_no_type_avg = np.array(list(statistics.dict_funct_call_no_types.values())).mean()
            else:
                fuct_no_type_avg = 0

            if len(statistics.dict_funct_call_types) > 0:
                fuct_type_avg = np.array(list(statistics.dict_funct_call_types.values())).mean()
            else:
                fuct_type_avg = 0
        except Exception as e:
            fuct_no_type_avg = -1
            fuct_type_avg = -1

        statistics.addRepo(repo_name, tot_this_repo_commit, statistics.number_type_annotations_per_repo[repo_name], n_test_files, n_non_test_files, len(statistics.dev_dict_total), fuct_no_type_avg, fuct_type_avg)
        if at_least_one_type_change[0] > 0:
            statistics.repo_with_types_changes += 1

        try:
            if statistics.total_typeAnnotation_codeChanges > 0:
                statistics.typeLastProjectVersion_percentage.append(round(statistics.typeLastProjectVersion_total / sum(statistics.insert_types.values()) * 100, 2))

                git_checkout(config.ROOT_DIR + "/GitHub/" + repo_name, commit_set, statistics)

        except Exception as e:
            print("[GIT UTILS]", str(e))

        """
        print(pointer[0], '/', dirlist_len)
        pointer[0] += 1
        """

        # process_queue.put(statistics)

        code_changes: list = []
        commit_statistics: list = []

        # The statistics are merged from the processes
        statistics_final: CodeStatistics = CodeStatistics()

        statistics_final.merge_results([statistics], code_changes, commit_statistics)

        statistics_final.matrix_commits_stars_annotations = statistics.matrix_commits_stars_annotations.tolist()
        statistics_final.matrix_files_annotations = statistics.matrix_files_annotations.tolist()
        statistics_final.matrix_test_files_annotations = statistics.matrix_test_files_annotations.tolist()

        write_in_json(config.ROOT_DIR + f"/Resources/log/RAW_{repo_name}.json",
                      convert_list_in_list_of_dicts([statistics_final]))

        write_in_json(config.ROOT_DIR + f"/Resources/Output/typeAnnotationChanges_{repo_name}.json",
                      convert_list_in_list_of_dicts(code_changes))


        write_in_json(config.ROOT_DIR + f"/Resources/Output/typeAnnotationCommitStatistics_{repo_name}.json",
                      convert_list_in_list_of_dicts(commit_statistics))

        # Computational time
        end = time.time()
        hours, rem = divmod(end - start, 3600)
        minutes, seconds = divmod(rem, 60)

        if config.NORMAL_PRINT:
            print("[Finished]", repo_name, "with", commit_with_annotations_this_repo, '/', tot_this_repo_commit,
                  "commits with Type annotations", "in ",
                  "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

    except Exception as e:
        print('[Error gitUtils] ' + str(e))

    # lock.release()
    return statistics


def git_checkout(repo_dir, commit_set,statistics):

    for commit in commit_set:
        try:
            subprocess.run(f"git checkout {commit[4:]} --quiet".split(" "), cwd=repo_dir)

            param_types, return_types, variable_types, non_param_types, non_return_types, non_variable_types = count_type_annotations(
               repo_dir)

            #print(param_types, return_types, variable_types)

            statistics.annotation_coverage[str(commit[:4])][0] += param_types
            statistics.annotation_coverage[str(commit[:4])][1] += non_param_types
            statistics.annotation_coverage[str(commit[:4])][2] += return_types
            statistics.annotation_coverage[str(commit[:4])][3] += non_return_types
            statistics.annotation_coverage[str(commit[:4])][4] += variable_types
            statistics.annotation_coverage[str(commit[:4])][5] += non_variable_types

        except Exception as e:
            #print(repo_dir,str(e))
            continue


def function_size_correlation(repo_dir, statistics):
        try:
            for filepath in pathlib.Path(repo_dir).glob('**/*'):
                if str(filepath).endswith(".py"):

                    try:
                        param_types, return_types, variable_types, non_param_types, non_return_types, non_variable_types = extract_from_file(
                            str(filepath))

                        for key in non_return_types:
                            statistics.dict_funct_call_no_types[key] = function_call_count(repo_dir, str(key[-1]))

                        for key in return_types:
                            statistics.dict_funct_call_types[key] = function_call_count(repo_dir, str(key[-1]))

                        with open(str(filepath), 'r') as file:
                            src = file.read()

                        func_list = body_fuct_extraction(src.strip())

                        for func in func_list:
                            func_name = ""
                            m = re.search(r'def (.*?)\(', func)

                            if m:
                                func_name = m.group(1)
                            else:
                                continue

                            param_types, return_types, variable_types, non_param_types, non_return_types, non_variable_types = extract_from_snippet(
                                str(func))

                            tot_types = len(param_types) + len(return_types) + len(variable_types)
                            tot_non_types = len(non_return_types) + len(non_variable_types) + len(non_param_types)

                            if tot_types + tot_non_types == 0:
                                continue

                            coverage = tot_types / (tot_types + tot_non_types)

                            fuct_count = function_call_count(repo_dir, func_name)

                            statistics.matrix_files_annotations = np.append(statistics.matrix_files_annotations,
                                                                            np.array([[fuct_count,
                                                                                       coverage * 100,
                                                                                       tot_types]]), axis=0)

                    except Exception as e:
                        print("[FUNCTION SIZE]",str(e))
                        continue

        except Exception as e:
            if len(statistics.dict_funct_call_no_types) == 0:
                statistics.dict_funct_call_no_types['key']=0
            if len(statistics.dict_funct_call_types) == 0:
                statistics.dict_funct_call_types['key'] = 0
            return

def function_call_count(directory, function_name):

    count = -1
    for filename in pathlib.Path(directory).glob('**/*'):
        try:
            if str(filename).endswith(".py"):
                filepath = os.path.join(directory, filename)

                with open(filepath, 'r') as fp:
                    for line in fp:
                        # String to search for:
                        if function_name in line:
                            count += 1
        except Exception as e:
            continue

    return count


def body_fuct_extraction(code_string):
    global c2
    code_string += '\n'

    func_list = []
    func = ''
    tab = ''
    brackets = {'(': 0, '[': 0, '{': 0}
    close = {')': '(', ']': '[', '}': '{'}
    string = ''
    tab_f = ''
    c1 = ''
    multiline = False
    check = False
    for line in code_string.split('\n'):
        tab = re.findall(r'^\s*', line)[0]
        if re.findall(r'^\s*def', line) and not string and not multiline:
            func += line + '\n'
            tab_f = tab
            check = True
        if func:
            if not check:
                if sum(brackets.values()) == 0 and not string and not multiline:
                    if len(tab) <= len(tab_f):
                        func_list.append(func)
                        func = ''
                        c1 = ''
                        c2 = ''
                        continue
                func += line + '\n'
            check = False
        for c0 in line:
            if c0 == '#' and not string and not multiline:
                break
            if c1 != '\\':
                if c0 in ['"', "'"]:
                    if c2 == c1 == c0 == '"' and string != "'":
                        multiline = not multiline
                        string = ''
                        continue
                    if not multiline:
                        if c0 in string:
                            string = ''
                        else:
                            if not string:
                                string = c0
                if not string and not multiline:
                    if c0 in brackets:
                        brackets[c0] += 1
                    if c0 in close:
                        b = close[c0]
                        brackets[b] -= 1
            c2 = c1
            c1 = c0

    return func_list


def error_check():
    import os
    my_list = os.listdir(config.ROOT_DIR + '/GitHub/')

    dict_new = {}

    i = 0
    for folder in my_list:
        i += 1
        if folder == '.pyre_configuration':
            continue
        print(str(i) + '\n')
        result = subprocess.run(['flake8', config.ROOT_DIR + '/GitHub/' + folder, '--count'], stdout=subprocess.PIPE)

        last = io.StringIO(result.stdout.decode('utf-8')).readlines()[-1]

        result2 = subprocess.run(['git', '--git-dir='+ config.ROOT_DIR + '/GitHub/'+ folder +'/.git','config' , '--get', 'remote.origin.url'], stdout=subprocess.PIPE)

        if i == 93:
            print('ok')

        last2 = io.StringIO(result2.stdout.decode('utf-8')).readlines()[-1]


        dict_new[last2.replace('\n','')] = int(last)

    print('ok')

    write_in_json(config.ROOT_DIR + "/Resources/Output/error_check_flake8.json",
                  dict_new)