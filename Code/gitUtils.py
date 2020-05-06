import pygit2 as git
from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE
from Code.codeChangeExtraction import TypeAnnotationExtraction, writeJSON


def query_repo_get_commits(repo_path, file_extension):
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

        num_parents = len(
            commit.parents)  # Do not want to include merges for now, hence we check if the number of parents is 'one'
        if num_parents == 1:  # and commit_message_contains_query(commit.message, query_terms):
            # Diff between the current commit and its parent

            diff = repo.diff(commit.hex + '^', commit.hex)

            for patch in diff:
                temp_list = TypeAnnotationExtraction(repo_path, commit, patch, remote_url + '/commit/' + commit.hex)

                if temp_list is not None:
                    code_changes += temp_list

    writeJSON("typeAnnotationChanges", code_changes)

