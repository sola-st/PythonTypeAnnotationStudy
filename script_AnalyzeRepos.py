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
results_base_dir = config.ROOT_DIR + "/Resources/Output_type_fix_commits/"


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
    if not path.isfile(repo_dir+"/.pyre_configuration"):
        out = invoke_cmd("cp ../.pyre_configuration .", repo_dir)
    out = invoke_cmd("pyre check", repo_dir)
    
    warnings = out.split("\n")
    warnings = warnings[:-1]  # last line is empty
    print(f"Got {len(warnings)} warnings")

    warnings = [k for k in warnings if 'Could not find a module corresponding to import' not in k and 'Undefined import' not in k and 'Parsing failure' not in k]
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
            sys.version_info        
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

# Note: target_commits is a dictionary with project name as key, and a list of 7-character hex as value.
def get_type_warning_removed_output(projects, max_commits_per_project, target_commits=None):
    for p in projects:
        try:
            repo_dir = repos_base_dir+p
            init_pyre(repo_dir)            
            all_commits = get_all_commits(repo_dir)
            target_exist = target_commits is not None and target_commits[p] is not None
            if target_exist:
                commits = all_commits
            else:
                commits = sample_commits(all_commits, max_commits_per_project)
            project_results = []
            for c in commits:
                try:
                    if target_exist and c not in target_commits[p]:
                        continue
                    parent_commit = get_parent_commit(repo_dir, c).split()[0]                
                    # e.g. for ['75007332e4eddac6d67bcf9ad805a02972ef2caf aae156252f5d9a82b0a308ae3243755ee4d81bab'],
                    # parent_commit == '75007332e4eddac6d67bcf9ad805a02972ef2caf'
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
                                # Remove warnings if the same msg exist in both parent_warnings and warnings
                                for pw in list(out['parent_warnings'][-1]):
                                    pw_msg = pw.split(':')[-1]
                                    for w in list(out['warnings'][-1]):
                                        if pw_msg in w:
                                            if pw in out['parent_warnings'][-1]:
                                                out['parent_warnings'][-1].remove(pw)
                                            if w in out['warnings'][-1]:
                                                out['warnings'][-1].remove(w)
                                            break
                            elif f not in files:
                                out['parent_warnings'].append([i for i in parent_res['all_warnings'] if i.split(':')[0] in f])
                        project_results.append(out)
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

# b should be later than a
def compare_two_commits_warnings_output(p, a_commit, b_commit):
    try:
        repo_dir = repos_base_dir+p
        init_pyre(repo_dir)            
        project_results = []
        a_res = get_commit_type_error(repo_dir, a_commit)
        b_res = get_commit_type_error(repo_dir, b_commit)
        out = {
            'project': p,
            'a_commit': a_commit, 
            'b_commit': b_commit, 
            'warning_removed': a_res['nb_warnings'] - b_res['nb_warnings'],
            'parent_warnings': [],
            'warnings': []
        }
        parent_files = a_res['file_to_count']
        files = b_res['file_to_count']
        for f, count in parent_files.items():
            if f in files and files[f] < count:
                out['parent_warnings'].append([i for i in a_res['all_warnings'] if i.split(':')[0] in f])
                out['warnings'].append([i for i in b_res['all_warnings'] if i.split(':')[0] in f])
                # Remove warnings if the same msg exist in both parent_warnings and warnings
                for pw in list(out['parent_warnings'][-1]):
                    pw_msg = pw.split(':')[-1]
                    for w in list(out['warnings'][-1]):
                        if pw_msg in w:
                            if pw in out['parent_warnings'][-1]:
                                out['parent_warnings'][-1].remove(pw)
                            if w in out['warnings'][-1]:
                                out['warnings'][-1].remove(w)
                            break
            elif f not in files:
                out['parent_warnings'].append([i for i in a_res['all_warnings'] if i.split(':')[0] in f])
        project_results.append(out)
        write_results("compare_warning_"+p+"_"+a_commit+"_"+b_commit, project_results)
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
# get_type_warning_removed_output(['Python'], 0, { 
#     # commits with "mypy" in commit message:
#     "Python": ["5e7eed6", "20a4fdf", "af0810f", "4545270", "d009cea", "3c22524", "da71184", "a5bcf0f", "a4b7d12", "c5003a2", "7634cf0", "407c979", "7342b33", "bc09ba9", "4a2216b", "307ffd8", "256c319", "4412eaf", "9586230", "86baec0", "62d4418", "3ea5a13", "977511b", "03d9b67", "deb7116", "252df0a", "531d2d6", "c49fa08", "8c29860", "20c7518", "6089536", "a53fcf2", "5229c74", "895bca3", "c22c7d5", "9b60be6", "9595079", "a8db5d4", "ce99859", "14bcb58", "2c6f553", "8d7ef6a", "9875673", "ffa53c0", "8e488dd", "4f6a929", "4c76e3c", "7df393f", "a4726ca", "2a6e4bb", "81c46df", "2595cf0", "97b6ca2", "d594f45", "00e279e", "207ac95", "f3ba9b6", "ad5108d", "06dad4f", "25164bb", "03e7f37", "aaaa175", "00a6701", "20e09c3", "11ec2fd", "629848e", "0616148", "d924a80", "08254eb", "83a63d9", "b373c99", "9153db2", "fdf095f", "08d4d22", "4bf2eed", "4cf1aae", "bcfca67", "d324f91", "abc725f", "c1b15a8"]
# })
repos = [
    # [repo_name, parent commit, current commit]
    # ['asciidots', 'ee95023', '4c3243b'],
    # ['polyglot', 'f72f0d7','75f82b3'],
    # ['ObjectPath', '9cb35aa', '93bedaf'],
    # ['ahkab', '43beb43', '42826d0'],
    # ['streamalert', 'f200eaba','19fffb57'],
    # ['unsync', '992f00c','c7d6a73'],
    # ['kaldi-gstreamer-server', 'fa894d1','81640a4'],
    # ['sh', '48554ce','7e5539b'],
    # ['anchore-engine', '704964bb','cfcf4ee9'],
    # ['thoonk.py', 'fc6803c','b8844fa'],
    # ['Arelle', 'dbb8c43b','7463baed'],
    # ['LibCST', '3ccfc4a^','3ccfc4a'],
    # ['pyscaffold', '609f548','4628e57'],
    # ['operator', '824aa2d^','824aa2d'],
    # ['faker', '9a382ed^','9a382ed'],
    # ['hivemind', '40d3ece^','40d3ece'],
    # ['pytorch', '78d5707^','78d5707'],
    # ['pytorch', 'd4d5f85^','d4d5f85'], # n
    # ['pytorch', 'e89b150^','e89b150'], # n
    # ['pytorch', '8ec7b47^','8ec7b47'],
    # ['pytorch', '88ed93c^','88ed93c'],
    # ['pytorch', '85b562d^','85b562d'], # n
    # ['Fixit', 'cbef89f^','cbef89f'], # strict, pyre ignore
    # ['openr', 'b53d50a^','b53d50a'], # strict, pyre ignore
    # ['keras', '41d967f^','41d967f'],
    # ['keras', '050e8cb^','050e8cb'],
    # ['keras', '9f8f520^','9f8f520'],
    # ['fastapi', '0e19c24014c96e241bd73bede2805e21fc20c9d8^','0e19c24014c96e241bd73bede2805e21fc20c9d8'], # n 
    # ['fastapi', 'ca27317b654e8265b8783df22e88a439adf96e8a^','ca27317b654e8265b8783df22e88a439adf96e8a'], # n
    # ['fastapi', '75407b92952d4a5fabe9b2d7084fddce5725dcbd^','75407b92952d4a5fabe9b2d7084fddce5725dcbd'], # n
    # ['fastapi', 'e71636e381a297d1825b37f71362ecd36f2fb3fb^','e71636e381a297d1825b37f71362ecd36f2fb3fb'], # n
    # ['fastapi', 'fdb6c9ccc504f90afd0fbcec53f3ea0bfebc261a^','fdb6c9ccc504f90afd0fbcec53f3ea0bfebc261a'],
    # ['fastapi', '4d208b2b9035e24bdf80505571b5b1bac8f9ae7a^','4d208b2b9035e24bdf80505571b5b1bac8f9ae7a'], # n
    # ['fastapi', 'd8fe307d61a55148a4d95c550f0ef33148ba8681^','d8fe307d61a55148a4d95c550f0ef33148ba8681'], # n
    # ['fastapi', 'f1c5330b6526b706b1dc2d9b3301a3ec401ddca4^','f1c5330b6526b706b1dc2d9b3301a3ec401ddca4'], # n
    # ['faker', 'eb088b85861d4e26565024c748ccf021e8ced88c^', 'eb088b85861d4e26565024c748ccf021e8ced88c'], 
    # ['faker', 'acdfc155099722414be5e46103ad09c3bf19c58b^', 'acdfc155099722414be5e46103ad09c3bf19c58b'], 
    # ['faker', 'f4deca79f8e13e7029b2bfa7c7b2ce2a82c41b0f^', 'f4deca79f8e13e7029b2bfa7c7b2ce2a82c41b0f'], 
    # ['faker', '8d1a2bd0159de38533c5262a60be2eacf564852d^', '8d1a2bd0159de38533c5262a60be2eacf564852d'], 
    # ['faker', '9a382ed237ef6ac40eb272703eb3b6ce0546ad0f^', '9a382ed237ef6ac40eb272703eb3b6ce0546ad0f'], 
    # ['faker', 'b63b5f434925c3b5751b2693a0aec87dfa021892^', 'b63b5f434925c3b5751b2693a0aec87dfa021892'], 
    # ['rich', 'f513abd35fdacccdc6fcbcc6989b5792b75ec97a^', 'f513abd35fdacccdc6fcbcc6989b5792b75ec97a'], 
    # ['rich', 'f84c84f2623c4b5605641d440479edc259de8e64^', 'f84c84f2623c4b5605641d440479edc259de8e64'], 
    # ['rich', '9e881e5510931f4e2d005cb4f852f19412eb337d^', '9e881e5510931f4e2d005cb4f852f19412eb337d'], 
    # ['rich', '22d55908d261ef103778d9af41a947c4e44ac3b6^', '22d55908d261ef103778d9af41a947c4e44ac3b6'], 
    # ['rich', '19961c1a6a7448295377bb52479ac937e2bfdf9b^', '19961c1a6a7448295377bb52479ac937e2bfdf9b'], 
    # ['Kats', '61d3945^','61d3945'],
    # ['Kats', '4405225^','4405225'], # n
    # ['Kats', '4a395b4^','4a395b4'], # n
    # ['Kats', 'feed421cbeeecf566cb1d39522b3c1d14ccddbc5^','feed421cbeeecf566cb1d39522b3c1d14ccddbc5'], 
    # ['Kats', '4884647a99432804647ec03d37040a5ac10e9508^','4884647a99432804647ec03d37040a5ac10e9508'], 
    # ['Kats', '2c955ab9825a48124fd2d3ba523048b1bed0da43^','2c955ab9825a48124fd2d3ba523048b1bed0da43'], 
    ['rasa', '1ded5effc8aa78d723f8a8be06997c0bef1d2fbe^','1ded5effc8aa78d723f8a8be06997c0bef1d2fbe'], 
]
for r in repos:
    compare_two_commits_warnings_output(r[0], r[1], r[2])

end = time.time()
hours, rem = divmod(end - start, 3600)
minutes, seconds = divmod(rem, 60)

print("{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

