#!/usr/bin/python3

import subprocess
import sys
import re
import random
import time
from collections import Counter, defaultdict
import json
from os import path, scandir
from Code.TypeErrors.TypeAnnotationCounter import count_type_annotations

import config

repos_base_dir = config.ROOT_DIR + "/GitHub/"
results_base_dir = config.ROOT_DIR + "/Resources/Output_typeErrors/"


def find_all_projects():
    projects = []
    for e in scandir(repos_base_dir):
        if e.is_dir():
            projects.append(e.name)
    return projects


projects = find_all_projects()


def init_pyre(repo_dir):
    if not path.isfile(repo_dir+"/.pyre_configuration"):
        print(f"Creating pyre configuration for {repo_dir}")
        subprocess.run(
            f"cp data/.pyre_configuration {repo_dir}".split(" "))
    else:
        print(f"Reusing existing pyre configuration for {repo_dir}")


def invoke_cmd(cmd, cwd):
    try:
        out = subprocess.check_output(
            cmd.split(" "), cwd=cwd)
        out = out.decode(sys.stdout.encoding)
    except subprocess.CalledProcessError as e:
        # handle exit codes, e.g., when type checker reports warnings
        out = e.output.decode(sys.stdout.encoding)
    return out

# Run pyre check here
def check_commit(repo_dir, commit):
    print("\n===========================================")
    print(f"Checking commit {commit} of {repo_dir}")

    # go to commit
    subprocess.run(f"git checkout {commit}".split(" "), cwd=repo_dir)

    # get date of commit
    out = subprocess.check_output(
        f"git show -s --format=%ci {commit}".split(" "), cwd=repo_dir)
    commit_date = out.decode(sys.stdout.encoding).rstrip()

    # count lines of code
    print("--- Counting lines of code")
    out = invoke_cmd(f"sloccount .", repo_dir)

    loc = 0
    for l in out.split("\n"):
        l_search = re.search(r"python:\s*(\d+) .*", l)
        if l_search is not None:
            loc = int(l_search.group(1))

    # count Python files
    out = invoke_cmd(f"find . -name *.py", repo_dir)
    nb_python_files = len(out.split("\n")) - 1  # last line is empty

    # type check
    print("--- Type checking")
    out = invoke_cmd("cp ../.pyre_configuration .", repo_dir)
    out = invoke_cmd("pyre check", repo_dir)

    warnings = out.split("\n")
    warnings = warnings[:-1]  # last line is empty
    print(f"Got {len(warnings)} warnings")

    # analyze warnings
    kind_to_nb = Counter()
    for w in warnings:
        w_search = re.search(r".*:\d+:\d+ (.*\[\d+\]):.*", w)
        if w_search is None:
            raise Exception(f"Warning: Could not parse warning -- {w}")
        warning_kind = w_search.group(1)
        kind_to_nb[warning_kind] += 1

    # count type annotations
    param_types, return_types, variable_types, _, _, _ = count_type_annotations(
        repo_dir)

    result = {
        "commit": commit,
        "commit_date": commit_date,
        "loc": loc,  # number line of code
        "nb_python_files": nb_python_files,
        "nb_param_types": param_types,
        "nb_return_types": return_types,
        "nb_variable_types": variable_types,
        "nb_warnings": len(warnings),
        "kind_to_nb": kind_to_nb
    }
    return result

def get_commit_type_error(repo_dir, commit): # repo_dir = /home/wai/hiwi/TypeAnnotation_Study/GitHub/Python
    print("\n===========================================")
    print(f"Checking commit {commit} of {repo_dir}")

    # go to commit
    subprocess.run(f"git checkout {commit}".split(" "), cwd=repo_dir)

    # get date of commit
    out = subprocess.check_output(
        f"git show -s --format=%ci {commit}".split(" "), cwd=repo_dir)
    commit_date = out.decode(sys.stdout.encoding).rstrip()

    # count lines of code
    print("--- Counting lines of code")
    out = invoke_cmd(f"sloccount .", repo_dir)

    loc = 0
    for l in out.split("\n"):
        l_search = re.search(r"python:\s*(\d+) .*", l)
        if l_search is not None:
            loc = int(l_search.group(1))

    # count Python files
    out = invoke_cmd(f"find . -name *.py", repo_dir)
    nb_python_files = len(out.split("\n")) - 1  # last line is empty

    # type check
    print("--- Type checking")
    # out = invoke_cmd("python --version", repo_dir)    
    # print(out)
    # out = invoke_cmd("pyre --version", repo_dir)
    # print(out)
    # out = invoke_cmd("pyre rage", repo_dir)
    # print(out)
    # out = invoke_cmd("git status", repo_dir)
    # print(out)
    # out = invoke_cmd("env", repo_dir)
    # print(out)
    # sys.exit()
    out = invoke_cmd("cp ../.pyre_configuration .", repo_dir)
    out = invoke_cmd("pyre check", repo_dir)
    
    warnings = out.split("\n")
    warnings = warnings[:-1]  # last line is empty
    print(f"Got {len(warnings)} warnings")

    warnings = [k for k in warnings if ' Could not find a module corresponding to import' not in k]
    print(f"Got {len(warnings)} warnings after removing import error")

    # analyze warnings
    kind_to_nb = Counter()
    file_to_count = defaultdict(lambda: 0)
    for w in warnings:
        w_search = re.search(r"(.*):-?\d+:-?\d+ (.*\[\d+\]):.*", w)
        if w_search is None:
            raise Exception(f"Warning: Could not parse warning -- {w}")
        filename = w_search.group(1)
        file_to_count[filename] += 1
        warning_kind = w_search.group(2)
        kind_to_nb[warning_kind] += 1

    # count type annotations
    # param_types, return_types, variable_types, _, _, _ = count_type_annotations(
    #     repo_dir)
    
    result = {
        "commit": commit,
        "commit_date": commit_date,
        "loc": loc,  # number line of code
        "nb_python_files": nb_python_files,
        # "nb_param_types": param_types,
        # "nb_return_types": return_types,
        # "nb_variable_types": variable_types,
        "nb_warnings": len(warnings),
        "kind_to_nb": kind_to_nb,
        "file_to_count": file_to_count,
        "all_warnings": warnings,
    }
    return result

def nb_types(r):
    return r["nb_param_types"] + r["nb_variable_types"] + r["nb_return_types"]


def get_all_commits(repo_dir):
    out = invoke_cmd("git log --all --oneline", repo_dir)
    lines = out.split("\n")
    lines = lines[:-1]  # last line is empty
    commits = [l.split(" ")[0] for l in lines]
    print(f"Found {len(commits)} commits")
    return commits


def write_results(name, results):
    with open(results_base_dir+name+".json", "w") as fp:
        fp.write(json.dumps(results, indent=2))


def sample_commits(all_commits, max_commits_per_project):
    if len(all_commits) <= max_commits_per_project:
        commits = all_commits
    else:
        stride = int(round(len(all_commits) /
                           float(max_commits_per_project - 1)))
        commits = [all_commits[i]
                   for i in range(0, len(all_commits), stride)]
    return commits


def analyze_histories(projects, max_commits_per_project):
    for p in projects:
        try:
            repo_dir = repos_base_dir+p
            init_pyre(repo_dir)
            all_commits = get_all_commits(repo_dir)
            commits = sample_commits(all_commits, max_commits_per_project)
            #commits = all_commits
            project_results = []
            for c in commits:
                r = check_commit(repo_dir, c)
                project_results.append(r)
            write_results("history_"+p, project_results)
        except Exception as e:
            print(f"WARNING: Some problem with {p} -- skipping this project")
            print(e)

def analyze_typeAnnotation_output(projects, max_commits_per_project, commits=None):
    for p in projects:
        try:
            repo_dir = repos_base_dir+p
            init_pyre(repo_dir)
            if commits is None:
                all_commits = get_all_commits(repo_dir)
                commits = sample_commits(all_commits, max_commits_per_project)
                #commits = all_commits
            project_results = []
            for c in commits:
                parent_commit = get_parent_commit(repo_dir, c)
                r = get_commit_type_error(repo_dir, parent_commit)
                project_results.append(r)
            write_results("history_"+p, project_results)
        except Exception as e:
            print(f"WARNING: Some problem with {p} -- skipping this project")
            print(e)

def get_type_warning_removed_output(projects, max_commits_per_project):
    for p in projects:
        try:
            repo_dir = repos_base_dir+p
            init_pyre(repo_dir)            
            all_commits = get_all_commits(repo_dir)
            commits = sample_commits(all_commits, max_commits_per_project)
            project_results = []
            for c in commits:
                try:
                    parent_commit = get_parent_commit(repo_dir, c)
                    parent_res = get_commit_type_error(repo_dir, parent_commit)
                    res = get_commit_type_error(repo_dir, c)
                    if res['nb_warnings'] < parent_res['nb_warnings']:
                        out = {
                            'project': p,
                            'commit': c, 
                            'parent_commit': parent_commit, 
                            'warning_removed': parent_res['nb_warnings'] - res['nb_warnings'],
                            'parent_warnings': [],
                            'warnings': []
                        }
                        parent_files = parent_res['file_to_count']
                        files = res['file_to_count']
                        for f, count in parent_files.items():
                            if f in files and files[f] < count:
                                out['parent_warnings'].append([i for i in parent_res['all_warnings'] if i.split(':')[0] in f])
                                out['warnings'].append([i for i in res['all_warnings'] if i.split(':')[0] in f])
                            elif f not in files:
                                out['parent_warnings'].append([i for i in parent_res['all_warnings'] if i.split(':')[0] in f])
                        project_results.append(out)
                        # The following is not accurate as line/column/identifier might change
                        # for pw in parent_res['all_warnings']:
                        #     if pw not in res['all_warnings']:
                        #         project_results.append({'commit': c, 'warning_removed': pw})
                except Exception as e:
                    print(f"WARNING: Some problem with commit {c} of {p} -- skipping this commit")
                    print(e)
            # Get commits randomly from each repo
            random.Random(2021).shuffle(project_results)
            # project_results = project_results[:num_commit]
            write_results("history_warning_removed_"+p, project_results)
        except Exception as e:
            print(f"WARNING: Some problem with {p} -- skipping this project")
            print(e)

def analyze_latest_commit(projects):
    results = []
    for p in projects:
        repo_dir = repos_base_dir+p
        init_pyre(repo_dir)
        all_commits = get_all_commits(repo_dir)
        latest_commit = all_commits[0]
        r = check_commit(repo_dir, latest_commit)
        r["project"] = p
        results.append(r)
    write_results("latest", results)


def get_parent_commit(repo_dir, commit):
    cmd = f"git log --pretty=%P -n 1 {commit}"
    out = invoke_cmd(cmd, repo_dir)
    return out.split("\n")[0]


def is_add_only_commit(c):
    return (c["added_per_commit_percentage"] == "100.0 %" and
            int(c["typeannotation_line_inserted"]) > 0 and
            int(c["typeannotation_line_removed"]) == 0 and
            int(c["typeannotation_line_changed"]) == 0)


def is_remove_only_commit(c):
    return (c["removed_per_commit_percentage"] == "100.0 %" and
            int(c["typeannotation_line_inserted"]) == 0 and
            int(c["typeannotation_line_removed"]) > 0 and
            int(c["typeannotation_line_changed"]) == 0)


def is_changed_only_commit(c):
    return (c["changed_per_commit_percentage"] == "100.0 %" and
            int(c["typeannotation_line_inserted"]) == 0 and
            int(c["typeannotation_line_removed"]) == 0 and
            int(c["typeannotation_line_changed"]) > 0)


def analyze_specific_commits(commits_file):
    with open(commits_file) as fp:
        commit_stats = json.load(fp)

    result = {
        "add_only_commits": {
            "same_nb_errors": 0,
            "more_errors": 0,
            "fewer_errors": 0,
        },
        "remove_only_commits": {
            "same_nb_errors": 0,
            "more_errors": 0,
            "fewer_errors": 0,
        },
        "change_only_commits": {
            "same_nb_errors": 0,
            "more_errors": 0,
            "fewer_errors": 0,
        },
    }
    commit_url_regexp = r"https.*github\.com\/(.*)\/(.*)\/commit\/(.*)"
    skipped = 0
    used = 0
    index = -1
    for c in commit_stats:
        try:

            add_only = is_add_only_commit(c)
            remove_only = is_remove_only_commit(c)
            change_only = is_changed_only_commit(c)

            if add_only or remove_only or change_only:
                commit_url = c["url"]
                match = re.match(commit_url_regexp, commit_url)
                project = match.group(1) + '-' + match.group(2)
                commit = match.group(3)
                if commit == 'fb96392e73d0d12b845dabea185cc9e2ffa4652a':
                    continue
                repo_dir = repos_base_dir+project
                parent_commit = get_parent_commit(repo_dir, commit)

                pre_change = check_commit(repo_dir, parent_commit)
                post_change = check_commit(repo_dir, commit)

                if add_only and not (nb_types(pre_change) < nb_types(post_change)):
                    skipped += 1
                    continue
                if remove_only and not (nb_types(pre_change) > nb_types(post_change)):
                    skipped += 1
                    continue
                if change_only and not (nb_types(pre_change) == nb_types(post_change)):
                    skipped += 1
                    continue

                # write result for this commit into overall stats
                if add_only:
                    relevant_result = result["add_only_commits"]
                elif remove_only:
                    relevant_result = result["remove_only_commits"]
                else:  # change-only
                    relevant_result = result["change_only_commits"]
                warnings_diff = post_change["nb_warnings"] - \
                    pre_change["nb_warnings"]
                if warnings_diff == 0:
                    relevant_result["same_nb_errors"] += 1
                elif warnings_diff > 0:
                    relevant_result["more_errors"] += 1
                elif warnings_diff < 0:
                    relevant_result["fewer_errors"] += 1

                used += 1
                if used % 10 == 0:
                    print(f"\nUsed {used}, skipped {skipped}")
                    print(f"{result}")
        except Exception as e:
            print(str(e))

    write_results("pure_commits_vs_errors.json", result)


#if __name__ == "__main__":
    #analyze_histories(projects, max_commits_per_project=11)
    # analyze_latest_commit(projects)  # TODO: still needed?
start = time.time()

# analyze_histories(projects, max_commits_per_project=5)

#analyze_specific_commits(
 #   config.ROOT_DIR + "/Resources/Output/typeAnnotationCommitStatistics.json")

# The output here will be used in script_typeAnnotation_analysis for matching pyre error msg
# analyze_typeAnnotation_output(['Python'], 1, ['cd987372e4c3a9f87d65b757ab46a48527fc9fa9'])
get_type_warning_removed_output(['Python'], 500)
repos = ['models', 'thefuck', 'keras', 'transformers', 
    'face_recognition','faceswap','fastapi','localstack', 'openpilot']
get_type_warning_removed_output(repos, 100)

end = time.time()
hours, rem = divmod(end - start, 3600)
minutes, seconds = divmod(rem, 60)

print("{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

