import json
import os
import time
import pygit2 as git
from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE
import config
from Code.codeChangeExtraction import TypeAnnotationExtraction, type_annotation_in_last_version, \
    TypeAnnotationExtractionFirstCommit
from Code.codeStatistics import CodeStatistics


def repo_cloning(filenameInput: str, pathOutput: str) -> None:
    with open(filenameInput) as fh:
        articles = json.load(fh)

    article_urls = [article['html_url'] for article in articles]

    i = 0
    for link in article_urls:
        i += 1
        out = link.rsplit('/', 1)[-1].replace('.git', '')

        if os.path.isdir(pathOutput + '/' + out):
            print(str(i) + ') Already cloned' + link)
            continue

        else:
            print(str(i) + ') Cloning ' + link)
            git.clone_repository(link, pathOutput + '/' + out)


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
    print("[Working]", repo_name)
    # lock.release()

    type_annotation_in_last_version(repo_name, statistics)

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
            #print(str(commit.hex))
      #      if commit.hex == '2e1d49e2fa30bb3ab953fd0e236d927b633538d2':
      #          iii = 0
            # start = time.time()
            commit_year = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(commit.commit_time))[:4]
      #      if commit_year != '2019':
      #         continue

            tot_line_inserted = 0
            tot_line_removed = 0
            typeannotation_line_inserted = [0]
            typeannotation_line_removed = [0]
            typeannotation_line_changed = [0]
            list_line_added = set()
            list_line_removed = set()
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
                elif num_parents == 0:
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

                    # RQ 4.1
                    try:
                        if typeannotation_line_inserted[0] - typeannotation_line_changed[0] > 0:
                            percentile = (typeannotation_line_inserted[0] - typeannotation_line_changed[0]) / (
                                    tot_line_inserted - typeannotation_line_changed[0]) * 100
                            # lock.acquire()
                            if percentile <= 100:
                                statistics.list_typeAnnotation_added_per_commit.append(percentile)
                            else:
                                print(repo_name, commit_year, str(commit.hex))
                            # lock.release()
                    except:
                        pass

                    # RQ 4.2
                    try:
                        if typeannotation_line_removed[0] - typeannotation_line_changed[0] > 0:
                            # lock.acquire()

                            percentile = (typeannotation_line_removed[0] - typeannotation_line_changed[0]) / (
                                    tot_line_removed - typeannotation_line_changed[0]) * 100
                            if percentile <= 100:
                                statistics.list_typeAnnotation_removed_per_commit.append(percentile)
                            else:
                                print(repo_name, commit_year, str(commit.hex))

                            # lock.release()
                    except:
                        pass

                    # RQ 4.3
                    try:
                        if typeannotation_line_changed[0] > 0:
                            percentile = (typeannotation_line_changed[0]) / (
                                    tot_line_removed + tot_line_inserted - typeannotation_line_changed[0]) * 100
                            # lock.acquire()
                            if percentile <= 100:
                                statistics.list_typeAnnotation_changed_per_commit.append(percentile)
                            # lock.release()
                    except:
                        pass

                    # RQ 4.4
                    try:
                        if len(list_line_added) > 0:
                            percentile_total_edits_inserted = ((len(list_line_added)) / (tot_line_inserted) * 100)

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
                        if len(list_line_removed) > 0:
                            percentile_total_edits_removed = (len(list_line_removed) /
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

                    if len(statistics.code_changes) > old_len:
                        # lock.acquire()
                        statistics.commits_with_typeChanges += 1

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
                    if str(patch.delta.old_file.path)[-3:] != file_extension or \
                            str(patch.delta.new_file.path)[-3:] != file_extension:
                        continue
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
                    TypeAnnotationExtraction(config.ROOT_DIR + "/GitHub/", repo_name, commit, patch,
                                             remote_url + '/commit/' + commit.hex + '#diff-' + diff.patchid.hex + 'L',
                                             statistics,  # lock, logging,
                                             at_least_one_type_change,
                                             statistics.code_changes, typeannotation_line_inserted,
                                             typeannotation_line_removed, typeannotation_line_changed, list_line_added,
                                             list_line_removed, commit_year)

            # RQ 4.1
            try:
                if typeannotation_line_inserted[0] - typeannotation_line_changed[0] > 0:
                    percentile = (typeannotation_line_inserted[0] - typeannotation_line_changed[0]) / (
                                tot_line_inserted - typeannotation_line_changed[0]) * 100
                    # lock.acquire()
                    if percentile <= 100:
                        statistics.list_typeAnnotation_added_per_commit.append(percentile)
                    else:
                        print(repo_name, commit_year,str(commit.hex))
                    # lock.release()
            except:
                pass

            # RQ 4.2
            try:
                if typeannotation_line_removed[0] - typeannotation_line_changed[0] > 0:
                    # lock.acquire()

                    percentile = (typeannotation_line_removed[0] - typeannotation_line_changed[0]) / (
                                tot_line_removed - typeannotation_line_changed[0]) * 100
                    if percentile <= 100:
                        statistics.list_typeAnnotation_removed_per_commit.append(percentile)
                    else:
                        print(repo_name, commit_year,str(commit.hex))

                    # lock.release()
            except:
                pass

            # RQ 4.3
            try:
                if typeannotation_line_changed[0] > 0:
                    percentile = (typeannotation_line_changed[0]) / (
                                tot_line_removed + tot_line_inserted - typeannotation_line_changed[0]) * 100
                    # lock.acquire()
                    if percentile <= 100:
                        statistics.list_typeAnnotation_changed_per_commit.append(percentile)
                    else:
                        print(repo_name, commit_year,str(commit.hex))
                    # lock.release()
            except:
                pass

            # RQ 4.4
            try:
                if len(list_line_added) > 0:
                    percentile_total_edits_inserted = ((len(list_line_added)) / (tot_line_inserted) * 100)

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
                if len(list_line_removed) > 0:
                    percentile_total_edits_removed = (len(list_line_removed) /
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

            if len(statistics.code_changes) > old_len:
                # lock.acquire()
                statistics.commits_with_typeChanges += 1

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
        for _ in repo.walk(last_commit, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE):

            statistics.total_commits += 1
            tot_this_repo_commit += 1

    # lock.acquire()
    statistics.addRepo(repo_name, tot_this_repo_commit, statistics.number_type_annotations_per_repo[repo_name])
    if at_least_one_type_change[0] > 0:
        statistics.repo_with_types_changes += 1

    """
    print(pointer[0], '/', dirlist_len)
    pointer[0] += 1
    """

    #process_queue.put(statistics)

    # Computational time
    end = time.time()
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)

    print("[Finished]", repo_name, "with", commit_with_annotations_this_repo, '/', tot_this_repo_commit,
          "commits with Type annotations", "in ", "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

    # lock.release()
    return statistics
