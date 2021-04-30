#!/usr/bin/python3

# Author: Michael Pradel
# Script to quickly find some commits that reduce type errors.
# Requires the history_*.json files that summarize the history of projects.

from os import listdir
import json

history_dir = "Resources/Output_typeErrors2"

ignored_warning_kinds = [
    "Undefined import [21]",
    "Undefined or invalid type [11]",
    "Undefined name [18]",
    "Undefined attribute [16]",
]


def compute_relevant_errors(commit):
    nb_errors = 0
    for kind, nb in commit["kind_to_nb"].items():
        if kind not in ignored_warning_kinds:
            nb_errors += nb
    return nb_errors


if __name__ == "__main__":
    nb_commits = 0
    for file in listdir(history_dir):
        if file.startswith("history") and file.endswith(".json"):
            with open(history_dir+"/"+file) as fp:
                history = json.load(fp)
                for commit_idx, commit in enumerate(history):
                    nb_commits += 1

                    if commit_idx < len(history) - 1:
                        current_errors = compute_relevant_errors(commit)
                        previous_errors = compute_relevant_errors(history[commit_idx +
                                                                          1])
                        if current_errors < previous_errors:
                            print()
                            print(
                                f"Commit {commit['commit']} of {file} reduced errors from {previous_errors} to {current_errors}")
                            current_kind_to_nb = commit["kind_to_nb"]
                            previous_kind_to_nb = history[commit_idx +
                                                          1]["kind_to_nb"]
                            print(f"Old: {previous_kind_to_nb}")
                            print(f"New: {current_kind_to_nb}")

    print(f"Analyzed {nb_commits} commits in histories")
