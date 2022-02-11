import json
import requests
import os
import calendar
import time
import config

# Get all repos
repos_to_query = set()
repo_dir = 'Resources/Input/TypeFix/repos_final/'
for filename in os.listdir(repo_dir):
  with open(repo_dir+filename) as f:
    try:
      repos = json.load(f)
      for r in repos:
        if not r['fork']:
          repos_to_query.add(r['full_name'])
    except Exception as e:
      print(f"Exception {e} for {filename}. Skipping this json.")

# Query Github for commits in these repos
keywords = ['fixing+typing', 'fixing+mypy', 'fixing+pyre', 'typing+bug', 'typing+error']
repo_qualifier = ''
headers = {'Authorization': 'token %s' % config.GIT_TOKEN}
req_count = 0
repo_count = 0 # total: 37170*5
commit_count = 0
repo_to_call = []
for key in keywords:
  for r in repos_to_query:
    try:
      repo_to_call.append(r)
      repo_count += 1
      # Group into a set of 10 repos, 
      # otherwise it will take at least 100 hours (37170 repos * 5 keywords/30 req per min)
      if repo_count % 10 == 0: 
        qualifier = " repo:".join(repo_to_call)
        repo_to_call = []
        for i in range(1,11):
          filename = 'Resources/Input/TypeFix/commits_final/'+key+'_'+str(repo_count)+'_page'+str(i)+'.json'
          if os.path.exists(filename): # Don't call API if we already have it
            continue
          url = 'https://api.github.com/search/commits?q='+key+'+repo:'+qualifier+'+merge:false&per_page=100&page='+str(i)
          print(f"Downloading {url}")
          res = requests.get(url, headers=headers)
          req_count += 1
          response = res.json()
          # print(res.headers) # Check X-RateLimit-Used, etc.
          if req_count % 30 == 0:
            time.sleep(70) # Basic Authentication, OAuth, or client ID and secret: 30 requests per minute                    
          os.makedirs(os.path.dirname(filename), exist_ok=True)
          commit_count += len(response['items'])
          with open(filename, 'w', encoding='utf-8') as f:
            json.dump(response['items'], f, ensure_ascii=False, indent=4)
          if not response['items']: # No more commits in this set of repos
            break          
    except Exception as e:
      print(f"Exception {e} for {url}. Skipping this query.")
      print(f"Response is {res}.")
      if req_count % 30 == 0 or 'API rate limit exceeded' in response['message'] or 'You have exceeded a secondary rate limit' in response['message']:
        time.sleep(70)
        continue
      break # maybe 'Validation Failed'

print('req_count: ', req_count) 
print('repo_count: ', repo_count) 
print('commit_count: ', commit_count) 