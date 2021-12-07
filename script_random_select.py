import json
import os
import random

directories = [
  r'Resources/Output_type_fix_commits_via_API_pyre/', 
  r'Resources/Output_type_fix_commits_via_API_mypy/',
  r'Resources/Output_type_fix_commits_via_API_repo/',
  r'Resources/Output_type_fix_commits_via_API_repo_json/'
]
for dir in directories:  
  i = 0
  files = os.listdir(dir)
  random.shuffle(files)	
  print('-------------------------------------------')
  print('Sampling from '+dir)
  for fn in files:
    try:
      if i >= 10:
        break
      elif fn.startswith('compare_warning_') and fn.endswith('.json'):
        with open(dir+fn) as f:
          data = json.load(f) 
          for d in data: 
            if len(d['parent_warnings']) > 0:            
              print(fn)
              i += 1
    except Exception as e:
      # print(e)
      print(f"cannot parse json, skip file {f}")


