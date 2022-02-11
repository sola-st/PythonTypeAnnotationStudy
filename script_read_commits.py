import json
import os

repo = 'Python'

out = {repo: []}

owner = 'TheAlgorithms'
directory = r'Resources/Input/' + owner + '_' + repo
for filename in os.listdir(directory):
  if filename.startswith('commits_p') and filename.endswith('.json'):
    with open(directory+'/'+filename) as f:
      data = json.load(f)
      out[repo].append(data)

flattened = []
for sublist in out[repo]:
    for val in sublist:
      if 'mypy' in val['commit']['message']:
        flattened.append(val['sha'][0:7])
out[repo] = flattened

with open(directory+'/'+'mypy_commits.json', 'w') as json_file:
  # json.dump(out, json_file, indent=4)
  json.dump(out, json_file)
