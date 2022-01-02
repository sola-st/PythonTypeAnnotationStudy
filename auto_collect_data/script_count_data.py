import json
import os
import time

# directory = r'Resources/type_fix_dataset/'
# count = 0
# for data_file in os.listdir(directory):
#   if data_file.startswith('type_fix_') and data_file.endswith('.json'):
#     with open(directory+'/'+data_file) as f:
#       data = json.load(f) 
#       for d in data:
#         count += 1

# print('Resources/type_fix_dataset/ count: ', count)

# # -------- Count type fixing commits for top 1000 repos from 2010-2019 --------
# directory = r'Resources/Input/TypeFix/top10000/'
# count = 0
# for data_file in os.listdir(directory):
#     with open(directory+data_file) as f:
#       try:
#         data = json.load(f) 
#         for d in data:
#           count += 1
#       except Exception:
#         print(f"cannot parse json, skip file {f}")

# print('Resources/Input/TypeFix/top10000/ commits count: ', count)

# -------- Count fixed warnings in commits *after filtering* for mypy --------
directory = r'Resources/Output_type_fix_commits_via_API_mypy/'
count = 0
for data_file in os.listdir(directory):
    with open(directory+data_file) as f:
      try:
        data = json.load(f) 
        for d in data: 
          for pw in d['parent_warnings']:
            count += len(pw)
      except Exception:
        print(f"cannot parse json, skip file {f}")

print('Resources/Output_type_fix_commits_via_API_mypy/ fixed warnings in commits *after filtering* count: ', count)

# -------- Count fixed warnings in commits *after filtering* for pyre --------
directory = r'Resources/Output_type_fix_commits_via_API_pyre/'
count = 0
for data_file in os.listdir(directory):
    with open(directory+data_file) as f:
      try:
        data = json.load(f) 
        for d in data: 
          for pw in d['parent_warnings']:
            count += len(pw)
      except Exception:
        print(f"cannot parse json, skip file {f}")

print('Resources/Output_type_fix_commits_via_API_pyre/ fixed warnings in commits *after filtering* count: ', count)

# -------- Count fixed warnings in commits *after filtering* for repo --------
directory = r'Resources/Output_type_fix_commits_via_API_repo/'
count = 0
for data_file in os.listdir(directory):
    with open(directory+data_file) as f:
      try:
        data = json.load(f) 
        for d in data: 
          for pw in d['parent_warnings']:
            count += len(pw)
      except Exception:
        print(f"cannot parse json, skip file {f}")

print('Resources/Output_type_fix_commits_via_API_repo/ fixed warnings in commits *after filtering* count: ', count)

# -------- Count fixed warnings in commits *after filtering* for top 1000 repos from 2010-2019 --------
directory = r'Resources/Output_type_fix_commits_via_API_repo_json/'
count = 0
commit_count = 0
for data_file in os.listdir(directory):
    with open(directory+data_file) as f:
      try:
        data = json.load(f) 
        commit_count += 1
        for d in data: 
          for pw in d['parent_warnings']:
            count += len(pw)
      except Exception:
        print(f"cannot parse json, skip file {f}")

print('Resources/Output_type_fix_commits_via_API_repo_json/ fixed warnings in commits *after filtering* count: ', count)
print('Resources/Output_type_fix_commits_via_API_repo_json/ processed commits count: ', commit_count)

# -------- Count fixed warnings in commits *after warning filtering* for top 1000 repos from 2010-2019 --------
directory = r'Resources/Output_type_fix_commits_via_API_mypy_all/'
count = 0
commit_count = 0
for data_file in os.listdir(directory):
    with open(directory+data_file) as f:
      try:
        data = json.load(f) 
        commit_count += 1
        for d in data: 
          for pw in d['parent_warnings']:
            count += len(pw)
      except Exception:
        print(f"cannot parse json, skip file {f}")

print('Resources/Output_type_fix_commits_via_API_mypy_all/ fixed warnings in commits *after warning filtering* count: ', count)
print('Resources/Output_type_fix_commits_via_API_mypy_all/ processed commits count: ', commit_count)

# -------- Count fixed warnings in commits *after warning+repo filtering* for top 1000 repos from 2010-2019 --------
directory = r'Resources/Output_type_fix_commits_via_API_mypy_all_filtered/'
count = 0
commit_count = 0
for data_file in os.listdir(directory):
    with open(directory+data_file) as f:
      try:
        data = json.load(f) 
        commit_count += 1
        for d in data: 
          for pw in d['parent_warnings']:
            count += len(pw)
      except Exception:
        print(f"cannot parse json, skip file {f}")

print('Resources/Output_type_fix_commits_via_API_mypy_all_filtered/ fixed warnings in commits *after warning+repo filtering* count: ', count)
print('Resources/Output_type_fix_commits_via_API_mypy_all_filtered/ processed commits count: ', commit_count)

# -------- Count --------
directory = r'Resources/Input/TypeFix/repos_final/'
count = 0
size_sum = 0
for data_file in os.listdir(directory):
    with open(directory+data_file) as f:
      try:
        data = json.load(f) 
        for d in data: 
          count += 1
          size_sum += d['size'] 
      except Exception:
        print(f"cannot parse json, skip file {f}")

print('Resources/Input/TypeFix/repos_final/ repos count: ', count)
print('Resources/Input/TypeFix/repos_final/ repos size sum: ', size_sum)

# -------- Count --------
directory = r'Resources/Input/TypeFix/commits_final/'
commit_set = set()
for data_file in os.listdir(directory):
    with open(directory+data_file) as f:
      try:
        data = json.load(f) 
        for d in data: 
          commit_set.add(d['sha'])
      except Exception:
        # print(f"cannot parse json, skip file {f}")
        pass

print('Resources/Input/TypeFix/commits_final/ commits count: ', len(commit_set))

start = time.asctime()
print('Time: ' + start)

