import json
import requests
import os
import calendar
import time
import config

# Get all repos in the commits data
repos_to_query = set()
for y in range(2015, 2022):
  for m in range(1,13):
    query = 'fixing+mypy+committer-date:'+ \
      str(y)+'-'+str(m).zfill(2)+'-01..'+ \
      str(y)+'-'+str(m).zfill(2)+'-'+str(calendar.monthrange(y, m)[1])    
    for i in range(1,11): # page 1-10, GitHub Search API provides up to 1,000 results for each search.
      filename = 'Resources/Input/TypeFix/fix_mypy_all/'+query+'_commits_page'+str(i)+'.json'
      with open(filename) as f:
        commits = json.load(f)  
        for c in commits:
          if not c['repository']['fork']:
            repos_to_query.add(c['repository']['full_name'])

# Query Github for repo metada, check for stars:>=100 and size:<=5000000 (5GB)
repo_qualifier = ''
headers = {'Authorization': 'token %s' % config.GIT_TOKEN}
req_count = 0
repo_count = 0
repo_after_filter_count = 0
repo_to_call = []
for r in repos_to_query:
  try:
    repo_to_call.append(r)
    repo_count += 1
    if repo_count % 100 == 0: 
      qualifier = " repo:".join(repo_to_call)
      repo_to_call = []
      filename = 'Resources/Input/TypeFix/fix_mypy_all/repos_after_filter_stars=10_'+str(repo_count)+'.json'
      url = 'https://api.github.com/search/repositories?q=repo:'+qualifier+'+stars:>=10+size:<=5000000&per_page=100'
      print(f"Downloading {url}")
      res = requests.get(url, headers=headers)
      req_count += 1
      response = res.json()
      # print(res.headers) # Check X-RateLimit-Used, etc.
      os.makedirs(os.path.dirname(filename), exist_ok=True)
      repo_after_filter_count += len(response['items'])
      with open(filename, 'w', encoding='utf-8') as f:
          json.dump(response['items'], f, ensure_ascii=False, indent=4)
      if req_count % 30 == 0:
        time.sleep(70) # Basic Authentication, OAuth, or client ID and secret: 30 requests per minute
  except Exception as e:
    print(f"Exception {e} for {url} at page {i}. Skipping this query.")
    print(f"Response is {response}.")
    if req_count % 10 == 0 or 'API rate limit exceeded' in response['message'] or 'You have exceeded a secondary rate limit' in response['message']:
      time.sleep(70)
      continue
    break # maybe 'Validation Failed'

print('req_count: ', req_count) 
print('repo_count: ', repo_count) 
print('repo_after_filter_count: ', repo_after_filter_count) 