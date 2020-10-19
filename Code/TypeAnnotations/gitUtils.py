import csv
import json
import os
import re
import time
from collections import defaultdict

import pygit2 as git
from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE
import config
from Code.TypeAnnotations.codeChange import CommitStatistics
from Code.TypeAnnotations.codeChangeExtraction import TypeAnnotationExtractionFirstCommit, TypeAnnotationExtractionNew, \
    TypeAnnotationExtractionLast, type_annotation_in_last_version
from Code.TypeAnnotations.codeStatistics import CodeStatistics


def repo_cloning(filenameInput: str, pathOutput: str, count: int) -> None:
    with open(filenameInput) as fh:
        articles = json.load(fh)

    article_urls = [article['html_url'] for article in articles]

    #i = 0
    for link in article_urls:
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
    tot_this_repo_commit = 0
    # tot_this_repo_commit_with_annotations = [0]
    commit_with_annotations_this_repo = [0]
    at_least_one_type_change = [0]

    # lock.acquire()
    statistics.number_type_annotations_per_repo[repo_name] = 0
    statistics.total_repositories += 1

    if config.NORMAL_PRINT:
        print("[Working]", repo_name)
    # lock.release()

    type_annotation_in_last_version(repo_name, statistics)
    #statistics.typeLastProjectVersion_total = 1

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
        for commit in repo.walk(last_commit, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE):
            # print(str(commit.hex))
            #if commit.hex != 'a34b3d9d87fdfdf5695d8e4278277fd74374abcf':  # 6e1a31c3dfc4c574d8bbd61f768e35a2edd9b378
            #    continue
            start = time.time()
            commit_year = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(commit.commit_time))[:4]
            if int(commit_year) < 2015:
                continue

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
                elif num_parents == -1: # First commit
                    diff = repo.diff(commit.hex)
                    tot_line_inserted += diff.stats.insertions
                    for patch in diff:
                        if str(patch.delta.old_file.path)[-3:] != file_extension or \
                                str(patch.delta.new_file.path)[-3:] != file_extension:
                            continue
                        """
                        thread = threading.Thread(target=TypeAnnotationExtractionFirstCommit,
                                                  args=(config.ROOT_DIR + "/GitHub/", repo_name, commit, patch,
                                                        remote_url + '/commit/' + commit.hex + '#diff-' + diff.patchid.hex + 'L',
                                                        statistics, lock, logging, at_least_one_type_change,
                                                        code_changes, typeannotation_line_inserted,
                                                        typeannotation_line_removed, typeannotation_line_changed))
                        threads.append(thread)
    
                    for thread in threads:
                        thread.start()
    
                    for thread in threads:
                        thread.join()
                    """
                        TypeAnnotationExtractionFirstCommit(config.ROOT_DIR + "/GitHub/", repo_name, commit, patch,
                                                            remote_url + '/commit/' + commit.hex + '#diff-' + diff.patchid.hex + 'L',
                                                            statistics,  # lock, logging,
                                                            at_least_one_type_change,
                                                            statistics.code_changes, typeannotation_line_inserted,
                                                            typeannotation_line_removed, typeannotation_line_changed,
                                                            list_line_added, commit_year)

                    added_per_commit_percentage = 0
                    removed_per_commit_percentage = 0
                    changed_per_commit_percentage = 0
                    # RQ 4.1
                    try:
                        if typeannotation_line_inserted[0] - typeannotation_line_changed[0] > 0:
                            added_per_commit_percentage = (typeannotation_line_inserted[0] -
                                                           typeannotation_line_changed[0]) / (
                                                                  tot_line_inserted - typeannotation_line_changed[
                                                              0]) * 100
                            # lock.acquire()
                            if added_per_commit_percentage <= 100:
                                statistics.list_typeAnnotation_changed_per_commit.append(added_per_commit_percentage)
                            else:
                                print(repo_name, commit_year, str(commit.hex))
                            # lock.release()
                    except:
                        pass

                    # RQ 4.2
                    try:
                        if typeannotation_line_removed[0] - typeannotation_line_changed[0] > 0:
                            # lock.acquire()

                            removed_per_commit_percentage = (typeannotation_line_removed[0] -
                                                             typeannotation_line_changed[0]) / (
                                                                    tot_line_removed - typeannotation_line_changed[
                                                                0]) * 100
                            if removed_per_commit_percentage <= 100:
                                statistics.list_typeAnnotation_changed_per_commit.append(removed_per_commit_percentage)
                            else:
                                print(repo_name, commit_year, str(commit.hex))

                            # lock.release()
                    except:
                        pass

                    # RQ 4.3
                    try:
                        if typeannotation_line_changed[0] > 0:
                            changed_per_commit_percentage = (typeannotation_line_changed[0]) / (
                                    tot_line_removed + tot_line_inserted - typeannotation_line_changed[0]) * 100
                            # lock.acquire()
                            if changed_per_commit_percentage <= 100:
                                statistics.list_typeAnnotation_changed_per_commit.append(changed_per_commit_percentage)
                            else:
                                print(repo_name, commit_year, str(commit.hex))
                            # lock.release()
                    except:
                        pass
                    """
                    # RQ 4.4
                    try:
                        if list_line_added[0] > 0:
                            percentile_total_edits_inserted = ((list_line_added[0]) / (tot_line_inserted) * 100)

                            if percentile_total_edits_inserted <= 100:
                                # lock.acquire()
                                statistics.annotation_related_insertion_edits_vs_all_commit.append(
                                    percentile_total_edits_inserted)
                                # lock.release()
                            else:
                                print(repo_name, commit_year, str(commit.hex))
                    except:
                        pass

                    # RQ 4.5
                    try:
                        if list_line_removed[0] > 0:
                            percentile_total_edits_removed = (list_line_removed[0] /
                                                              (tot_line_removed) * 100)

                            if percentile_total_edits_removed <= 100:
                                # lock.acquire()
                                statistics.annotation_related_deletion_edits_vs_all_commit.append(
                                    percentile_total_edits_removed)
                            else:
                                print(repo_name, commit_year, str(commit.hex))
                                # lock.release()
                    except:
                        pass
                    """
                    if len(statistics.code_changes) > old_len:
                        # lock.acquire()
                        statistics.commits_with_typeChanges += 1

                        if added_per_commit_percentage <= 100 and removed_per_commit_percentage <= 100 and changed_per_commit_percentage <= 100:
                            try:
                                temp = CommitStatistics(str(remote_url + '/commit/' + commit.hex),
                                                        str(commit_year),
                                                        str(len(
                                                            statistics.code_changes) - old_len),
                                                        str(round(added_per_commit_percentage, 1)) + ' %',
                                                        str(round(removed_per_commit_percentage, 1)) + ' %',
                                                        str(round(changed_per_commit_percentage, 1)) + ' %',
                                                        str(typeannotation_line_inserted[0] -
                                                            typeannotation_line_changed[0]),
                                                        str(typeannotation_line_removed[0] -
                                                            typeannotation_line_changed[0]),
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
                            statistics.typeAnnotation_year_analysis[commit_year] = len(
                                statistics.code_changes) - old_len
                        else:
                            statistics.typeAnnotation_year_analysis[commit_year] += len(
                                statistics.code_changes) - old_len
                        # lock.release()

                        commit_with_annotations_this_repo[0] += 1

                    else:
                        if commit_year in statistics.typeAnnotation_commit_not_annotation_year_analysis:
                            statistics.typeAnnotation_commit_not_annotation_year_analysis[commit_year] += 1

                    continue

                # threads: list = []
                for patch in diff:
                    try:
                        if str(patch.delta.old_file.path)[-3:] != file_extension or \
                                str(patch.delta.new_file.path)[-3:] != file_extension:
                            continue
                    except Exception as e:
                        return

                    """
                    thread = threading.Thread(target=TypeAnnotationExtraction,
                                              args=(config.ROOT_DIR + "/GitHub/", repo_name, commit, patch,
                                                    remote_url + '/commit/' + commit.hex + '#diff-' + diff.patchid.hex + 'L',
                                                    statistics, lock, logging, at_least_one_type_change,
                                                    code_changes, typeannotation_line_inserted,
                                                    typeannotation_line_removed, typeannotation_line_changed))
                    threads.append(thread)
                
                for thread in threads:
                    thread.start()
    
                for thread in threads:
                    thread.join()
                """
                    TypeAnnotationExtractionLast(config.ROOT_DIR + "/GitHub/", repo_name, commit, patch,
                                                remote_url + '/commit/' + commit.hex + '#diff-' + diff.patchid.hex,
                                                statistics,  # lock, logging,
                                                at_least_one_type_change,
                                                statistics.code_changes, typeannotation_line_inserted,
                                                typeannotation_line_removed, typeannotation_line_changed,
                                                list_line_added,
                                                list_line_removed, commit_year)

            added_per_commit_percentage = 0
            removed_per_commit_percentage = 0
            changed_per_commit_percentage = 0
            # RQ 4.1
            try:
                if typeannotation_line_inserted[0] - typeannotation_line_changed[0] > 0:
                    added_per_commit_percentage = (typeannotation_line_inserted[0] - typeannotation_line_changed[0]) / (
                            tot_line_inserted - typeannotation_line_changed[0]) * 100
                    # lock.acquire()
                    if added_per_commit_percentage <= 100:
                        statistics.list_typeAnnotation_changed_per_commit.append(added_per_commit_percentage)
                    else:
                        print(repo_name, commit_year, str(commit.hex))
                    # lock.release()
            except:
                pass

            # RQ 4.2
            try:
                if typeannotation_line_removed[0] - typeannotation_line_changed[0] > 0:
                    # lock.acquire()

                    removed_per_commit_percentage = (typeannotation_line_removed[0] - typeannotation_line_changed[
                        0]) / (
                                                            tot_line_removed - typeannotation_line_changed[0]) * 100
                    if removed_per_commit_percentage <= 100:
                        statistics.list_typeAnnotation_changed_per_commit.append(removed_per_commit_percentage)
                    else:
                        print(repo_name, commit_year, str(commit.hex))

                    # lock.release()
            except:
                pass

            # RQ 4.3
            try:
                if typeannotation_line_changed[0] > 0:
                    changed_per_commit_percentage = (typeannotation_line_changed[0]) / (
                            tot_line_removed + tot_line_inserted - typeannotation_line_changed[0]) * 100
                    # lock.acquire()
                    if changed_per_commit_percentage <= 100:
                        statistics.list_typeAnnotation_changed_per_commit.append(changed_per_commit_percentage)
                    else:
                        print(repo_name, commit_year, str(commit.hex))
                    # lock.release()
            except:
                pass
            """
            # RQ 4.4
            try:
                if list_line_added[0] > 0:
                    percentile_total_edits_inserted = ((list_line_added[0]) / (tot_line_inserted) * 100)

                    if percentile_total_edits_inserted <= 100:
                        # lock.acquire()
                        statistics.annotation_related_insertion_edits_vs_all_commit.append(
                            percentile_total_edits_inserted)
                        # lock.release()
                    else:
                        print(repo_name, commit_year,str(commit.hex))
            except:
                pass

            # RQ 4.5
            try:
                if list_line_removed[0] > 0:
                    percentile_total_edits_removed = (list_line_removed[0] /
                                                      (tot_line_removed) * 100)

                    if percentile_total_edits_removed <= 100:
                        # lock.acquire()
                        statistics.annotation_related_deletion_edits_vs_all_commit.append(
                            percentile_total_edits_removed)
                    else:
                        print(repo_name, commit_year, str(commit.hex))
                        # lock.release()
            except:
                pass
            """
            if len(statistics.code_changes) > old_len:
                # lock.acquire()
                statistics.commits_with_typeChanges += 1

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

            """# Computational time
            end = time.time()
            hours, rem = divmod(end - start, 3600)
            minutes, seconds = divmod(rem, 60)
            if seconds > 1.0:
                print(str(commit.hex), "ends successfully in" , "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))
            """
    else:
        # Go through each commit starting from the most recent commit
        for commit in repo.walk(last_commit, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE):
            commit_year = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(commit.commit_time))[:4]
            if int(commit_year) < 2015:
                continue

            statistics.total_commits += 1
            tot_this_repo_commit += 1

    # git checkout `git rev-list -n 1 --first-parent --before="2013-09-25 5:00" master`
    # New plot with avg time ...

    # lock.acquire()
    statistics.addRepo(repo_name, tot_this_repo_commit, statistics.number_type_annotations_per_repo[repo_name])
    if at_least_one_type_change[0] > 0:
        statistics.repo_with_types_changes += 1

    """
    print(pointer[0], '/', dirlist_len)
    pointer[0] += 1
    """

    # process_queue.put(statistics)

    # Computational time
    end = time.time()
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)

    if config.NORMAL_PRINT:
        print("[Finished]", repo_name, "with", commit_with_annotations_this_repo, '/', tot_this_repo_commit,
              "commits with Type annotations", "in ",
              "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

    # lock.release()
    return statistics
