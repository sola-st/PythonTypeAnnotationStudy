import json
import os
import random

directories = [
  r'Resources/Output_type_fix_commits_via_API_pyre/', 
  r'Resources/Output_type_fix_commits_via_API_mypy/'
]
for dir in directories:  
  i = 0
  files = os.listdir(dir)
  random.shuffle(files)	
  print('-------------------------------------------')
  print('Sampling from '+dir)
  for data_file in files:
    if i >= 10:
      break
    elif data_file.startswith('compare_warning_') and data_file.endswith('.json'):
      print(data_file)
      i += 1

