import json
import os
import time

# -------- Count fixed warnings in commits *after filtering* for mypy --------
directory = r'Resources/Input/TypeFix/'
count = 0
for data_file in os.listdir(directory):
  if data_file.startswith('fixing+mypy+committer-date:'):
    with open(directory+data_file) as f:
      try:
        data = json.load(f) 
        for d in data: 
          count += 1
      except Exception:
        print(f"cannot parse json, skip file {f}")

print('Resources/Input/TypeFix/fixing+mypy+committer-date:*.json commits count: ', count)