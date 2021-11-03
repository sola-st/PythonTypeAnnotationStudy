import json
import os

directory = r'Resources/type_fix_dataset/'
out_directory = r'Resources/type_fix_code_data/'
count = 0
for data_file in os.listdir(directory):
  if data_file.startswith('type_fix_') and data_file.endswith('.json'):
    folder = data_file.replace('type_fix_','').replace('.json','')    
    with open(directory+'/'+data_file) as f:
      data = json.load(f) 
      for d in data:
        count += 1

print(count)
