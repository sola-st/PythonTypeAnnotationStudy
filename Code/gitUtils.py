import json
import os
import pygit2 as git
from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE
from Code.codeChangeExtraction import TypeAnnotationExtraction


def repo_cloning(filenameInput: str, pathOutput: str) -> None:
    with open(filenameInput) as fh:
        articles = json.load(fh)

    article_urls = [article['html_url'] for article in articles]

    i = 0
    for link in article_urls:
        i +=1
        out = link.rsplit('/', 1)[-1].replace('.git', '')

        if os.path.isdir(pathOutput + '/'+ out):
            print(str(i) + ') Already cloned' + link)
            continue

        else:
            print(str(i) + ') Cloning ' + link)
            git.clone_repository(link, pathOutput + '/'+ out)


def query_repo_get_changes(repo_path, file_extension, statistics, code_changes, lock):
    lock.acquire()
    statistics.total_repositories += 1
    lock.release()


    repo = git.Repository(repo_path)
    remote_url = None
    for r in repo.remotes:
        remote_url = r.url.split('.git')[0]

    last_commit = None

    for l in repo.head.log():
        last_commit = l.oid_new

    # Go through each commit starting from the most recent commit
    for commit in repo.walk(last_commit, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE):
        print(str(commit.hex))

        lock.acquire()
        statistics.total_commits += 1
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

                temp_list = TypeAnnotationExtraction(repo_path, commit, patch,
                                                     remote_url + '/commit/' + commit.hex + '#diff-' + diff.patchid.hex + 'L',
                                                     statistics, lock)

                if len(temp_list) > 0:
                    lock.acquire()
                    statistics.commits_with_typeChanges += 1

                    code_changes += temp_list

                    lock.release()

