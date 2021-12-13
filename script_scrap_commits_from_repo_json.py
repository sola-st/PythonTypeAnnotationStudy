import json
import requests
import os
import time

repo_qualifier = ''
headers = {'Authorization': 'token %s' % 'placeholder'}
req_count = 0
total_commits_count = 0
for i in range(0,10): # 2010-2019
  filename = 'Resources/Input/Top1000_Python201'+str(i)+'_Complete.json'
  with open(filename) as f:
    data = json.load(f)  
    for r in data:
      query = '"fixing+mypy"+OR+"fixing+pyre"+repo:'+r['full_name']

      # Call search API until no more "fixing+mypy"+OR+"fixing+pyre" commits in this repo
      for i in range(1,11): # page 1-10, GitHub Search API provides up to 1,000 results for each search.
        try:
          filename = 'Resources/Input/TypeFix/top10000_mypy_OR_pyre/' + ('fixing+mypy+OR+pyre+repo:'+r['full_name']).replace('/','-') + '_commits_page'+str(i)+'.json'
          if os.path.isfile(filename):
            print('Skip repo, data already downloaded: ', query)
            break
          url = 'https://api.github.com/search/commits?q='+query+'+merge:false&per_page=100&page='+str(i)
          print(f"Downloading {url}")
          res = requests.get(url, headers=headers)
          req_count += 1
          response = res.json()
          # print(res.headers) # Check X-RateLimit-Used, etc.
          if i == 1: # first loop
            total_commits_count += response['total_count']
            remaining_count = response['total_count']
          os.makedirs(os.path.dirname(filename), exist_ok=True)
          with open(filename, 'w', encoding='utf-8') as f:
              json.dump(response['items'], f, ensure_ascii=False, indent=4)
          if req_count % 30 == 0:
            time.sleep(70) # Basic Authentication, OAuth, or client ID and secret: 30 requests per minute
          remaining_count -= 100
          if remaining_count <= 0:
            break
        except Exception as e:
          print(f"Exception {e} for {url} at page {i} (req_count: {req_count}, total_commits_count: {total_commits_count}). Skipping this query.")
          print(f"Response is {response}.")
          if req_count % 30 == 0 or 'API rate limit exceeded' in response['message']:
            time.sleep(70)
            continue              
          break # maybe 'Validation Failed'

print('req_count: ', req_count)
print('total_commits_count: ', total_commits_count)