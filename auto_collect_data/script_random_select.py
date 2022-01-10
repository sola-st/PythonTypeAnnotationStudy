# Must pass a param: Max # of warnings in a file. 

import json
import os
import random
import sys

directories = [
  # r'Resources/Output_type_fix_commits_via_API_pyre/', 
  # r'Resources/Output_type_fix_commits_via_API_mypy/',
  # r'Resources/Output_type_fix_commits_via_API_repo/',
  # r'Resources/Output_type_fix_commits_via_API_repo_json/',
  # r'Resources/Output_type_fix_commits_via_API_mypy_all_filtered/',
  r'Resources/Output_type_fix_commits_final/'
]
for dir in directories:  
  i = 0
  files = os.listdir(dir)
  random.shuffle(files)	
  print('-------------------------------------------')
  print('Sampling from '+dir)
  max_w_in_file = int(sys.argv[1])
  for fn in files:
    try:
      if i >= 10:
        break
      elif fn.startswith('compare_warning_') and fn.endswith('.json'):
        with open(dir+fn) as f:
          data = json.load(f) 
          for d in data: 
            if len(d['parent_warnings']) > 0:
              for pw in d['parent_warnings']:            
                if len(pw) <= max_w_in_file:
                  print(fn)
                  i += 1
                  break
    except Exception as e:
      print(e)
      print(f"cannot parse json, skip file {f}")


