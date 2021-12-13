import json
import requests
import os
import calendar
import time

repo_qualifier = ''
headers = {'Authorization': 'token %s' % 'placeholder'}
req_count = 0
total_commits_count = 0
for y in range(2015, 2022):
  for m in range(1,13):
    query = 'fixing+mypy+committer-date:'+ \
      str(y)+'-'+str(m).zfill(2)+'-01..'+ \
      str(y)+'-'+str(m).zfill(2)+'-'+str(calendar.monthrange(y, m)[1])    
    for i in range(1,11): # page 1-10, GitHub Search API provides up to 1,000 results for each search.
      try:
        filename = 'Resources/Input/TypeFix/'+query+'_commits_page'+str(i)+'.json'
        if os.path.isfile(filename):
          print('Skip this page of commits, data already downloaded: ', query)
          continue
        url = 'https://api.github.com/search/commits?q='+query+'+merge:false&per_page=100&page='+str(i)
        print(f"Downloading {url}")
        res = requests.get(url, headers=headers)
        req_count += 1
        response = res.json()
        # print(res.headers) # Check X-RateLimit-Used, etc.
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(response['items'], f, ensure_ascii=False, indent=4)
        # if req_count % 30 == 0:
        if req_count % 10 == 0: # Since we break secondary rate limit, we lower req_count
          time.sleep(70) # Basic Authentication, OAuth, or client ID and secret: 30 requests per minute
      except Exception as e:
        print(f"Exception {e} for {url} at page {i}. Skipping this query.")
        print(f"Response is {response}.")
        if req_count % 10 == 0 or 'API rate limit exceeded' in response['message'] or 'You have exceeded a secondary rate limit' in response['message']:
          time.sleep(70)
          continue
        break # maybe 'Validation Failed'

print('req_count: ', req_count) # should be 12*7 = 84
print('total_commits_count: ', total_commits_count) # should be < 84000