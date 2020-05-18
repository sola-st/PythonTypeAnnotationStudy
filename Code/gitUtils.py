import json
import os

import pygit2 as git
from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE
from Code.codeChangeExtraction import TypeAnnotationExtraction, writeJSON


def repo_cloning(filenameInput, pathOutput):
    with open(filenameInput) as fh:
        articles = json.load(fh)

    article_urls = [article['html_url'] for article in articles]

    i = 0
    for link in article_urls:
        i +=1
        out = link.rsplit('/', 1)[-1].replace('.git', '')

        if os.path.isdir(pathOutput + '/'+ out):
            print(str(i) + ') Already cloned ' + link)
            continue

        else:
            print(str(i) + ') Cloning ' + link)
            #        command = "git clone " + link + " ./src/main/resources/GitHub/" + link.rsplit('/', 1)[-1].replace('.git', '')
            #       os.system(command)
            git.clone_repository(link, pathOutput + '/'+ out)


def query_repo_get_commits(repo_path, file_extension, statistics):
    statistics.total_repositories += 1
    code_changes = []

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
        statistics.total_commits += 1

        num_parents = len(
            commit.parents)  # Do not want to include merges for now, hence we check if the number of parents is 'one'
        if num_parents == 1:  # and commit_message_contains_query(commit.message, query_terms):
            # Diff between the current commit and its parent

            diff = repo.diff(commit.hex + '^', commit.hex)

            for patch in diff:
                if str(patch.delta.old_file.path)[-3:] != file_extension or str(patch.delta.new_file.path)[
                                                                            -3:] != file_extension:
                    continue

                temp_list = TypeAnnotationExtraction(repo_path, commit, patch,
                                                     remote_url + '/commit/' + commit.hex + '#diff-' + diff.patchid.hex + 'L',
                                                     statistics)

                if len(temp_list) > 0:
                    statistics.commits_with_typeChanges += 1
                    code_changes += temp_list

                    if len(code_changes) > 1:
                        json_file = json.dumps([change.__dict__ for change in code_changes], indent=4)
                    # print(json_file)

    return code_changes
