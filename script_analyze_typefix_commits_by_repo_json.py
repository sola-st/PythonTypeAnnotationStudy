#!/usr/bin/python3

# TODO: This file is the latest version of script_analyze_type_commits*. Run diff on other script_analyze_type_commits*.py to update them.

import multiprocessing
import resource
import os
import subprocess
import sys
import re
import random
import time
from collections import Counter, defaultdict
import json
from Code.TypeErrors.TypeAnnotationCounter import count_type_annotations
from Code.TypeAnnotations import gitUtils
import config
import signal

repos_base_dir = config.ROOT_DIR + "/GitHub/"
results_base_dir = config.ROOT_DIR + "/Resources/Output_type_fix_commits_via_API_repo_json/"

class PyreTimeoutError(Exception):
    """
    Attributes:
        pid -- pyre.bin process id
    """

    def __init__(self, pid, message="Pyre timeout"):
        self.pid = pid
        self.message = message+str(pid)
        super().__init__(self.message)

def memory_limit():
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (get_memory() * 1024 / 2, hard))

def get_memory():
    with open('/proc/meminfo', 'r') as mem:
        free_memory = 0
        for i in mem:
            sline = i.split()
            if str(sline[0]) in ('MemFree:', 'Buffers:', 'Cached:'):
                free_memory += int(sline[1])
    return free_memory

# Set maximun memory usage to half of sys 
memory_limit()

def init_pyre(repo_dir):
    if not path.isfile(repo_dir+"/.pyre_configuration"):
        print(f"Creating pyre configuration for {repo_dir}")
        subprocess.run(
            f"cp data/.pyre_configuration {repo_dir}".split(" "))
    else:
        print(f"Reusing existing pyre configuration for {repo_dir}")


def invoke_cmd(cmd, cwd):
    try:
        # The os.setsid() is passed in the argument preexec_fn so
        # it's run after the fork() and before  exec() to run the shell.
        proc = subprocess.Popen(cmd.split(" "), cwd=cwd, stdout=subprocess.PIPE, preexec_fn=os.setsid)
        pid = proc.pid
        out = proc.communicate(timeout=180)[0]
        out = out.decode(sys.stdout.encoding)
    except subprocess.TimeoutExpired as e:
        raise PyreTimeoutError(pid)
    # except subprocess.CalledProcessError as e:
    #     # handle exit codes, e.g., when type checker reports warnings
    #     out = e.output.decode(sys.stdout.encoding)
    return out

def get_commit_type_error(repo_dir, commit): # repo_dir = /home/wai/hiwi/TypeAnnotation_Study/GitHub/Python
    print("\n===========================================")
    print(f"Running git reset --hard for {repo_dir}")
    # reset so that git won't abort if there is unsaved changes
    subprocess.run(f"git reset --hard".split(" "), cwd=repo_dir)
    subprocess.run(f"git clean -df".split(" "), cwd=repo_dir)

    print(f"Checking commit {commit} of {repo_dir}")

    # go to commit
    subprocess.run(f"git checkout {commit}".split(" "), cwd=repo_dir)

    # get date of commit
    out = subprocess.check_output(
        f"git show -s --format=%ci {commit}".split(" "), cwd=repo_dir)
    commit_date = out.decode(sys.stdout.encoding).rstrip()

    # # count lines of code
    # print("--- Counting lines of code")
    # out = invoke_cmd(f"sloccount .", repo_dir)

    # loc = 0
    # for l in out.split("\n"):
    #     l_search = re.search(r"python:\s*(\d+) .*", l)
    #     if l_search is not None:
    #         loc = int(l_search.group(1))

    # # count Python files
    # out = invoke_cmd(f"find . -name *.py", repo_dir)
    # nb_python_files = len(out.split("\n")) - 1  # last line is empty

    # type check
    print("--- Type checking")
    out = invoke_cmd("pyre incremental", repo_dir)
    
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
        # "loc": loc,  # number line of code
        # "nb_python_files": nb_python_files,
        # "nb_param_types": param_types,
        # "nb_return_types": return_types,
        # "nb_variable_types": variable_types,
        "nb_warnings": len(warnings),
        "kind_to_nb": kind_to_nb,
        "file_to_count": file_to_count,
        "all_warnings": warnings,
    }
    return result

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

# b should be later than a
def compare_two_commits_warnings_output(p_commit_pair):   
    p, commits = p_commit_pair
    repo_dir = repos_base_dir+p
    pyre_server_up = False
    if not os.path.isfile(repo_dir+"/.pyre_configuration"):
        print(f"Creating pyre configuration for {repo_dir}")
        subprocess.run(
            f"cp data/.pyre_configuration {repo_dir}".split(" "))
    if not os.path.isfile(repo_dir+"/.watchmanconfig"):
        print(f"Creating watchman configuration for {repo_dir}")
        subprocess.run(
            f"cp data/.watchmanconfig {repo_dir}".split(" "))
    for b_commit in commits:
        a_commit = b_commit+'^'
        if os.path.isfile(results_base_dir+"compare_warning_"+p+"_"+a_commit+"_"+b_commit+".json"):
            print(f"Skip commit, data {p}_{a_commit}_{b_commit} already processed.")
            continue
        else:
            print(invoke_cmd("watchman watch .", repo_dir)) # must have watchman watching for pyre incremental to work
            pyre_server_up = True
            try:
                project_results = []
                a_res = get_commit_type_error(repo_dir, a_commit)
                b_res = get_commit_type_error(repo_dir, b_commit)
                out = {
                    'project': p,
                    'a_commit': a_commit, 
                'a_commit': a_commit, 
                    'a_commit': a_commit, 
                    'b_commit': b_commit, 
                'b_commit': b_commit, 
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
            except PyreTimeoutError as pe:
                # invoke_cmd("pyre kill", repo_dir) # Kill *all* pyre servers!!
                os.killpg(os.getpgid(pe.pid), signal.SIGTERM)  # Send the signal to all the process groups
                # print(invoke_cmd("pkill -c pyre.bin", repo_dir)) # Kill process
                print(pe.pid)
                print(f"WARNING: PyreTimeoutError with {p}: {b_commit} -- skipping this project")
                fail_log = open("failed_repo.txt", "a")  # append mode
                fail_log.write('Timeout: '+p+': '+b_commit+'\n')
                fail_log.close()
                print(invoke_cmd("watchman watch-del .", repo_dir)) # teardown watchman to reduce inotify instances (cannot watch if its too big)
                break # Skip this project
            except Exception as e:
                print(f"WARNING: Some problem with {p} -- skipping this commit")
                # write_results("compare_warning_"+p+"_"+a_commit+"_"+b_commit, []) # write empty files so that it won't be processed again
                fail_log = open("failed_repo.txt", "a")  # append mode
                fail_log.write(str(e) + ' : '+p+': '+b_commit+'\n')
                fail_log.close()
                print(e)
    # Shutdown the pyre server (each repo uses one) at the end
    if pyre_server_up:
        try:
            invoke_cmd("pyre stop", repo_dir)
            print(invoke_cmd("watchman watch-del .", repo_dir)) # teardown watchman to reduce inotify instances (cannot watch if its too big)
        except PyreTimeoutError as pe:
            # invoke_cmd("pyre kill", repo_dir) # Kill *all* pyre servers!!
            os.killpg(os.getpgid(pe.pid), signal.SIGTERM)  # Send the signal to all the process groups
            # print(invoke_cmd("pkill -c pyre.bin", repo_dir)) # Kill process
            print(pe.pid)
            print('WARNING: Timeout when stopping: '+p+': '+b_commit+'\n')
            fail_log = open("failed_repo.txt", "a")  # append mode
            fail_log.write('Timeout when stopping: '+p+': '+b_commit+'\n')
            fail_log.close()



def get_parent_commit(repo_dir, commit):
    cmd = f"git log --pretty=%P -n 1 {commit}"
    out = invoke_cmd(cmd, repo_dir)
    return out.split("\n")[0]

start = time.time()

if config.CLONING:
    i = 0
    j = [0]
    dir = 'Resources/Input/TypeFix/top10000/'
    # Clone and collect commits
    repo_commit_dict = defaultdict(list)
    for f in os.listdir(dir):
        filename = dir + f
        gitUtils.repo_cloning_commits_query(config.ROOT_DIR +'/'+ filename, config.ROOT_DIR + "/GitHub", j)
        with open(config.ROOT_DIR +'/'+ filename) as fh:
            try:
                commits = json.load(fh)
                for c in commits:
                    if 'cpython' not in c['repository']['full_name']:
                        repo_commit_dict[c['repository']['full_name'].replace('/', '-')].append(c['sha'])
                        # compare_two_commits_warnings_output(c['repository']['full_name'].replace('/', '-'), c['sha']+'^', c['sha'])
            except Exception:
                print(f"cannot parse json, skip file {fh}")
    # with multiprocessing.Pool(4) as p:
    #     for i in p.imap_unordered(compare_two_commits_warnings_output, repo_commit_dict.items()):
            # print(i)
    for i in repo_commit_dict.items():
        compare_two_commits_warnings_output(i)

end = time.time()
hours, rem = divmod(end - start, 3600)
minutes, seconds = divmod(rem, 60)

print("{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

