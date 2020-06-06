import json
import os
import pygit2 as git
from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE

import config
from Code.codeChangeExtraction import TypeAnnotationExtraction


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
    tot_this_repo_commit_with_annotations = 0
    commit_with_annotations_this_repo = 0
    at_least_one_type_change = 0

    lock.acquire()
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
        #    print(str(commit.hex))

        lock.acquire()
        statistics.total_commits += 1
        tot_this_repo_commit += 1
        lock.release()

        num_parents = len(
            commit.parents)  # Do not want to include merges for now, hence we check if the number of parents is 'one'
        if num_parents == 1:  # and commit_message_contains_query(commit.message, query_terms):
            # Diff between the current commit and its parent

            diff = repo.diff(commit.hex + '^', commit.hex)

            for patch in diff:
                if str(patch.delta.old_file.path)[-3:] != file_extension or \
                        str(patch.delta.new_file.path)[-3:] != file_extension:
                    continue

                temp_list = TypeAnnotationExtraction(config.ROOT_DIR + "/GitHub/" + repo_name, commit, patch,
                                                     remote_url + '/commit/' + commit.hex + '#diff-' + diff.patchid.hex + 'L',
                                                     statistics, lock, logging)

                if len(temp_list) > 0:
                    lock.acquire()
                    statistics.commits_with_typeChanges += 1
                    tot_this_repo_commit_with_annotations += 1
                    commit_with_annotations_this_repo += 1
                    at_least_one_type_change = 1

                    code_changes += temp_list

                    lock.release()

    lock.acquire()
    statistics.addRepo(repo_name, tot_this_repo_commit, tot_this_repo_commit_with_annotations)
    statistics.repo_with_types_changes += at_least_one_type_change
    print("[Finished]", repo_name, "with", commit_with_annotations_this_repo, '/', tot_this_repo_commit,
          "commits with Type annotations.")

    lock.release()
