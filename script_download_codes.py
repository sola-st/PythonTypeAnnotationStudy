import json
import os
import requests

directory = r'Resources/type_fix_dataset/'
out_directory = r'Resources/type_fix_code_data/'
miss_dict = {}
for data_file in os.listdir(directory):
  if data_file.startswith('type_fix_') and data_file.endswith('.json'):
    folder = data_file.replace('type_fix_','').replace('.json','')    
    with open(directory+'/'+data_file) as f:
      data = json.load(f) 
      for d in data:
        # note: filepath is from the old version
        filepath = d['full_warning_msg'].split(':')[0]
        filename = filepath.split('/')[-1]
        folderpath = str.join('/', filepath.split('/')[0:-1])
        d_split = d['url'].split('/')
        commit_hex = d_split[-1]
        repo = d_split[-3]
        owner = d_split[-4]
        # print(commit_hex, repo, owner, filepath)
        # print(filepath)
        # print(folderpath, filename)

        # Create old + new code folders for each commit 
        old_folder = out_directory+folder+'/'+commit_hex+'/old_code/' + folderpath + '/'
        new_folder = out_directory+folder+'/'+commit_hex+'/new_code/' + folderpath + '/'
        os.makedirs(os.path.dirname(old_folder), exist_ok=True)
        os.makedirs(os.path.dirname(new_folder), exist_ok=True)

        # Download old version code
        url = 'https://raw.githubusercontent.com/'+owner+'/'+repo+'/'+commit_hex+'^/'+filepath
        pyfile = requests.get(url)
        with open(old_folder+'/'+filename, 'wb') as ff:
          if pyfile.status_code == 200:
            ff.write(pyfile.content)
          else:
            miss_dict[url] = pyfile.status_code
        
        # Download new version code, if it is not found in the new version, manually find the new filepath
        url = 'https://raw.githubusercontent.com/'+owner+'/'+repo+'/'+commit_hex+'/'+filepath
        pyfile = requests.get(url)
        with open(new_folder+'/'+filename, 'wb') as ff:
          if pyfile.status_code == 200:
            ff.write(pyfile.content)
          else:
            miss_dict[url] = pyfile.status_code

# Output files that are not found in the new version

with open('code_not_found.json', 'w') as json_file:
  json.dump(miss_dict, json_file)
