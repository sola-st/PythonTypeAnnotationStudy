#!/usr/bin/python3
import os
import json
import config

repos_base_dir = config.ROOT_DIR + "/GitHub/"
results_base_dir = config.ROOT_DIR + "/Resources/Output_type_fix_commits_final/"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Update the project field to be c['repository']['full_name'], 
# not c['repository']['full_name'].replace('/', '-')
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

dir = 'Resources/Input/TypeFix/commits_final/'
for f in os.listdir(dir):
  if f.endswith('.json'):
    input_file = dir + f
    with open(config.ROOT_DIR +'/'+ input_file) as fh:
      commits = json.load(fh)
      for c in commits:
        p = c['repository']['full_name'].replace('/', '-')
        b_commit = c['sha']
        output_file = results_base_dir+"compare_warning_"+p+"_"+b_commit+".json"
        if os.path.isfile(output_file):
          with open(output_file, 'r') as f:
            data = json.load(f)
            for d in data:
              d['project'] = c['repository']['full_name']
              os.remove(output_file)
              with open(output_file, 'w') as f2:
                  json.dump(data, f2, indent=4)


