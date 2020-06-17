import json
import os
import threading

import pygit2 as git
from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE

import config
from Code.codeChangeExtraction import TypeAnnotationExtraction, type_annotation_in_last_version, \
    TypeAnnotationExtractionFirstCommit


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


def query_repo_get_changes(repo_name, file_extension, statistics, code_changes, lock, logging):
    tot_this_repo_commit = 0
    tot_this_repo_commit_with_annotations = [0]
    commit_with_annotations_this_repo = [0]
    at_least_one_type_change = [0]

    lock.acquire()
    statistics.number_type_annotations_per_repo[repo_name] = 0
    statistics.total_repositories += 1
    print("[Working]", repo_name)
    lock.release()

    repo = git.Repository(config.ROOT_DIR + "/GitHub/" + repo_name)
    remote_url = None
    for r in repo.remotes:
        remote_url = r.url.split('.git')[0]

    last_commit = None

    for l in repo.head.log():
        last_commit = l.oid_new

    # Go through each commit starting from the most recent commit
    for commit in repo.walk(last_commit, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE):
        #print(str(commit.hex))
        tot_line_inserted = 0
        tot_line_removed = 0
        typeannotation_line_inserted = [0]
        typeannotation_line_removed = [0]
        typeannotation_line_changed = [0]
        old_len = len(code_changes)

        lock.acquire()
        statistics.total_commits += 1
        tot_this_repo_commit += 1
        lock.release()

        num_parents = len(
            commit.parents)  # Do not want to include merges for now, hence we check if the number of parents is 'one'
        if num_parents >= 0:  # and commit_message_contains_query(commit.message, query_terms):
        # Diff between the current commit and its parent
            threads: list = []
            diff = []
            if num_parents == 1:
                diff = repo.diff(commit.hex + '^', commit.hex)
                tot_line_removed += diff.stats.deletions
                tot_line_inserted += diff.stats.insertions
            elif num_parents == 0:
                diff = repo.diff(commit.hex)
                for patch in diff:
                    if str(patch.delta.old_file.path)[-3:] != file_extension or \
                            str(patch.delta.new_file.path)[-3:] != file_extension:
                        continue
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

                lock.acquire()
                if typeannotation_line_inserted[0] - typeannotation_line_changed[0] > 0:
                    statistics.list_typeAnnotation_added_per_commit.append(
                        typeannotation_line_inserted[0] - typeannotation_line_changed[0])
                if typeannotation_line_removed[0] - typeannotation_line_changed[0] > 0:
                    statistics.list_typeAnnotation_removed_per_commit.append(
                        typeannotation_line_removed[0] - typeannotation_line_changed[0])

                if typeannotation_line_changed[0] > 0:
                    statistics.list_typeAnnotation_changed_per_commit.append(typeannotation_line_changed[0])

                if tot_line_inserted + tot_line_removed > 0 and typeannotation_line_inserted[0] + \
                        typeannotation_line_removed[0] > 0:
                    percentile_total_edits = ((typeannotation_line_inserted[0] + typeannotation_line_removed[0]) /
                                              (tot_line_inserted + tot_line_removed) * 100)
                    statistics.annotation_related_edits_vs_all_commit.append(percentile_total_edits)

                if len(code_changes) > old_len:
                    statistics.commits_with_typeChanges += 1
                    commit_with_annotations_this_repo[0] += 1
                lock.release()
                continue

            #threads: list = []
            for patch in diff:
                if str(patch.delta.old_file.path)[-3:] != file_extension or \
                        str(patch.delta.new_file.path)[-3:] != file_extension:
                    continue

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

        lock.acquire()
        if typeannotation_line_inserted[0] - typeannotation_line_changed[0] > 0:
            statistics.list_typeAnnotation_added_per_commit.append( typeannotation_line_inserted[0] - typeannotation_line_changed[0])
        if typeannotation_line_removed[0] - typeannotation_line_changed[0] > 0:
            statistics.list_typeAnnotation_removed_per_commit.append(typeannotation_line_removed[0] - typeannotation_line_changed[0])

        if typeannotation_line_changed[0] > 0:
            statistics.list_typeAnnotation_changed_per_commit.append(typeannotation_line_changed[0])

        if tot_line_inserted + tot_line_removed > 0 and typeannotation_line_inserted[0] + typeannotation_line_removed[0] > 0:
            percentile_total_edits = ((typeannotation_line_inserted[0] + typeannotation_line_removed[0])/
                                            (tot_line_inserted + tot_line_removed)* 100)
            statistics.annotation_related_edits_vs_all_commit.append(percentile_total_edits)

        if len(code_changes) > old_len:
            statistics.commits_with_typeChanges += 1
            commit_with_annotations_this_repo[0] += 1
        lock.release()
    type_annotation_in_last_version(repo_name, statistics, lock)

    lock.acquire()
    statistics.addRepo(repo_name, tot_this_repo_commit, statistics.number_type_annotations_per_repo[repo_name])
    if at_least_one_type_change[0] > 0:
        statistics.repo_with_types_changes += 1
    print("[Finished]", repo_name, "with", commit_with_annotations_this_repo, '/', tot_this_repo_commit,
          "commits with Type annotations.")

    lock.release()
