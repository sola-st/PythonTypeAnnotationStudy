import json
import requests
import os

repo_qualifier = ''
with open('Resources/Input/TypeFix/repositories_top100.json') as f:
  data = json.load(f)  
  for r in data['items']:
    repo_qualifier = repo_qualifier + '+repo:' + r['full_name']
query = 'fix+typing+'+repo_qualifier

for i in range(1,6):
  # print('https://api.github.com/search/commits?q='+query+'+merge:false&per_page=100&page='+str(i))
  response = requests.get(
    'https://api.github.com/search/commits?q='+query+'+merge:false&per_page=100&page='+str(i)
  ).json()

  filename = 'Resources/Input/TypeFix/fix+typing+repo_commits_page'+str(i)+'.json'
  os.makedirs(os.path.dirname(filename), exist_ok=True)
  with open(filename, 'w', encoding='utf-8') as f:
      json.dump(response['items'], f, ensure_ascii=False, indent=4)
