#!/usr/bin/python3

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
from Code.TypeAnnotations import gitUtils
import config
import signal

repos_base_dir = config.ROOT_DIR + "/GitHub/"
results_base_dir = config.ROOT_DIR + "/Resources/Output_type_fix_commits_final/"

class PyreTimeoutError(Exception):
    """
    Attributes:
        pid -- pyre.bin process id
    """

    def __init__(self, pid, message="Pyre timeout"):
        self.pid = pid
        self.message = message+str(pid)
        super().__init__(self.message)


# Useless as the CPU/memory consumption come from process spawned from the script
# def memory_limit():
#     soft, hard = resource.getrlimit(resource.RLIMIT_AS)
#     resource.setrlimit(resource.RLIMIT_AS, (get_memory() * 1024 / 2, hard))

# def get_memory():
#     with open('/proc/meminfo', 'r') as mem:
#         free_memory = 0
#         for i in mem:
#             sline = i.split()
#             if str(sline[0]) in ('MemFree:', 'Buffers:', 'Cached:'):
#                 free_memory += int(sline[1])
#     return free_memory

# # Set maximun memory usage to half of sys 
# memory_limit()

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
    print(f"Checking commit {commit} of {repo_dir}")

    # go to commit, force checkout so that git won't abort if there is unsaved changes
    # subprocess.run(f"git checkout -- .".split(" "), cwd=repo_dir)
    # subprocess.run(f"git clean -df".split(" "), cwd=repo_dir)
    subprocess.run(f"git checkout -f {commit}".split(" "), cwd=repo_dir)

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

    warnings = [k for k in warnings if 'Analysis failure' not in k and 'Parsing failure' not in k]
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

def write_results(name, results):
    with open(results_base_dir+name+".json", "w") as fp:
        fp.write(json.dumps(results, indent=2))

# b should be later than a
def compare_two_commits_warnings_output(p_commit_pair):   
    p_full_name, commits = p_commit_pair
    p = p_full_name.replace('/', '-')
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
        if os.path.isfile(results_base_dir+"compare_warning_"+p+"_"+b_commit+".json"):
            print(f"Skip commit, data {p}_{b_commit} already processed.")
            continue
        else:
            print(invoke_cmd("watchman watch .", repo_dir)) # must have watchman watching for pyre incremental to work
            pyre_server_up = True
            try:
                project_results = []
                a_res = get_commit_type_error(repo_dir, a_commit)
                b_res = get_commit_type_error(repo_dir, b_commit)
                out = {
                    'project': p_full_name,
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
                write_results("compare_warning_"+p+"_"+b_commit, project_results)
            except PyreTimeoutError as pe:
                # invoke_cmd("pyre kill", repo_dir) # Kill *all* pyre servers!!
                os.killpg(os.getpgid(pe.pid), signal.SIGTERM)  # Send the signal to all the process groups
                # print(invoke_cmd("pkill -c pyre.bin", repo_dir)) # Kill process
                print(pe.pid)
                print(f"WARNING: PyreTimeoutError with {p}: {b_commit} -- skipping this project")
                fail_log = open("failed_repo_final.txt", "a")  # append mode
                fail_log.write('Timeout: '+p+': '+b_commit+'\n')
                fail_log.close()
                print(invoke_cmd("watchman watch-del .", repo_dir)) # teardown watchman to reduce inotify instances (cannot watch if its too big)
                break # Skip this project
            except Exception as e:
                print(f"WARNING: Some problem with {p} -- skipping this commit")
                # write_results("compare_warning_"+p+"_"+b_commit, []) # write empty files so that it won't be processed again
                fail_log = open("failed_repo_final.txt", "a")  # append mode
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
            fail_log = open("failed_repo_final.txt", "a")  # append mode
            fail_log.write('Timeout when stopping: '+p+': '+b_commit+'\n')
            fail_log.close()



def get_parent_commit(repo_dir, commit):
    cmd = f"git log --pretty=%P -n 1 {commit}"
    out = invoke_cmd(cmd, repo_dir)
    return out.split("\n")[0]

start = time.time()
fail_log = open("failed_repo_final.txt", "a")  # append mode
fail_log.write('\n====================\nStart running at: '+str(start)+'\n')
fail_log.close()
#TODO: add logger
if config.CLONING:
    dir = 'Resources/Input/TypeFix/commits_final/'
    # Clone and collect commits
    repo_commit_dict = defaultdict(list)
    urls_to_clone = set()
    for f in os.listdir(dir):
        if f.endswith('.json'):
            filename = dir + f
            with open(config.ROOT_DIR +'/'+ filename) as fh:
                try:
                    commits = json.load(fh)
                    for c in commits:
                        # Is Fork / Failed to process / Too large:
                        if not c['repository']['fork'] and \
                        'cpython' not in c['repository']['full_name'] \
                        and 'gevent' not in c['repository']['full_name'] \
                        and 'naftaliharris/tauthon' not in c['repository']['full_name'] \
                        and 'platomav/MEAnalyzer' not in c['repository']['full_name'] \
                        and 'jython/frozen-mirror' not in c['repository']['full_name'] \
                        and 'rocky/python-uncompyle6' not in c['repository']['full_name'] \
                        and 'faucetsdn/ryu' not in c['repository']['full_name'] \
                        and 'gramps-project/gramps' not in c['repository']['full_name'] \
                        and 'ansible/ansible' not in c['repository']['full_name'] \
                        and 'python/typeshed' not in c['repository']['full_name'] \
                        and 'indico/indico' not in c['repository']['full_name'] \
                        and 'getsentry/sentry' not in c['repository']['full_name'] \
                        and 'Uber-Evaluation/chromium-1' not in c['repository']['full_name'] \
                        and 'bloomberg/chromium.bb' not in c['repository']['full_name'] \
                        and 'WaterfoxCo/Waterfox' not in c['repository']['full_name'] \
                        and 'MercifulPotato/mercifulpotato' not in c['repository']['full_name'] \
                        and 'jamienicol/gecko' not in c['repository']['full_name'] :
                            repo_commit_dict[c['repository']['full_name']].append(c['sha'])
                            urls_to_clone.add(c['repository']['html_url'])        
                except Exception as e:
                    print(f"cannot parse json, skip file {fh}, due to {e}")
    # --- Multi-thread ---
    # --- Cloning ---
    with multiprocessing.Pool(24) as p:
        for i in p.imap_unordered(gitUtils.repo_cloning_commits_query_with_url, urls_to_clone):
            pass
    print('--- Done Cloning ---')
    #  --- Run pyre ---
    with multiprocessing.Pool(8) as p:
        for i in p.imap_unordered(compare_two_commits_warnings_output, repo_commit_dict.items()):
            pass
    print('--- Done Running pyre ---')

    # --- Single-thread ---
    # for i in repo_commit_dict.items():
    #     compare_two_commits_warnings_output(i)

end = time.time()
hours, rem = divmod(end - start, 3600)
minutes, seconds = divmod(rem, 60)

print("{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

