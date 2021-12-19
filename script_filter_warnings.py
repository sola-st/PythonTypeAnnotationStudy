#!/usr/bin/python3

# Remove data according to filter
# In this case, we remove repos dir and warnings that are not >=100 stars and <=5GB
import os
import json
import config
import shutil

repos_base_dir = config.ROOT_DIR + "/GitHub/"
results_base_dir = config.ROOT_DIR + "/Resources/Output_type_fix_commits_via_API_mypy_all/"
filtered_results_base_dir = config.ROOT_DIR + "/Resources/Output_type_fix_commits_via_API_mypy_all_filtered/"

# Get filtered repos
repo_dir = 'Resources/Input/TypeFix/fix_mypy_all/repos/'
repos_after_filter = []
for f in os.listdir(repo_dir):
    if f.startswith('repos_after_filter_100stars') and f.endswith('.json'):
        filename = repo_dir + f
        with open(config.ROOT_DIR +'/'+ filename) as fh:
            repos_after_filter += json.load(fh)

repos_after_filter = list(map(lambda r: r['full_name'].replace('/', '-'), repos_after_filter))

# Remove warnings that are not in repos_after_filter
count = 0
warning_jsons = os.listdir(results_base_dir)
for f in warning_jsons:
    repo_name = f.replace('compare_warning_', '').rsplit('_',1)[0]
    if repo_name in repos_after_filter:
        if not os.path.exists(filtered_results_base_dir+f):
            shutil.copy(results_base_dir+f, filtered_results_base_dir)
        count += 1
print('Total # of warnings before repo filter: ', len(warning_jsons))
print('# of warnings after repo filter: ', count)

# Get repos in GitHub/ that are not in repos_after_filter
count = 0
git_repos = os.listdir(repos_base_dir)
for repo_name in git_repos:
    if repo_name not in repos_after_filter:
        print('Removing ', repo_name)
        count += 1
print('Total # of repos before filter: ', len(git_repos))
print('# of repos to not in filter: ', count)

# # Filter commits by filtered repos
# filtered_repo_commit_dict = dict((
#     (r['full_name'].replace('/', '-'), repo_commit_dict[r['full_name'].replace('/', '-')]) for r in repos_after_filter if repo_commit_dict[r['full_name'].replace('/', '-')]
# ))
