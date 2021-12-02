import json
import requests
import os

query = 'pyre+fix' # or mypy+fix
for i in range(1,6):
  response = requests.get(
    'https://api.github.com/search/commits?q='+query+'+merge:false&per_page=100&page='+str(i)
  ).json()

  filename = 'Resources/Input/TypeFix/'+query+'_commits_page'+str(i)+'.json'
  os.makedirs(os.path.dirname(filename), exist_ok=True)
  with open(filename, 'w', encoding='utf-8') as f:
      json.dump(response['items'], f, ensure_ascii=False, indent=4)
