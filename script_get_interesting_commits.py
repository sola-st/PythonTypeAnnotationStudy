# To get interesting commits (i.e. reducing number of warnings of previous commit)
# from dataset by luca
# Use script_AnalyzeRepo.py to compare 2 commits to check warnings in detail
import json
import os

directory = r'Resources/Output_typeErrors_luca/'
all_files = sorted(os.listdir(directory), key=str.casefold)
for data_file in all_files:
  if data_file.startswith('history_') and data_file.endswith('.json'):
    with open(directory+'/'+data_file) as f:
      data = json.load(f)
      for (i, d) in enumerate(data):
        if i+1 < len(data):
          next_commit = d
          cur_commit = data[i+1]
          for w, count in cur_commit["kind_to_nb"].items():
            if (
              (
                w not in next_commit["kind_to_nb"] or
                (
                  w in next_commit["kind_to_nb"] and 
                  next_commit["kind_to_nb"][w] < count
                )
              ) and 
              "Undefined import" not in w and 
              "Could not find a module corresponding to import" not in w and 
              "Parsing failure" not in w and 
              "Unbound name" not in w and 
              "Missing argument" not in w and 
              "Too many arguments" not in w and
              "Unexpected keyword"  not in w
            ):
              project = data_file[8:-5]
              # assuming owner name has no hyphen:
              owner = project.split("-")[0]
              repo = ''.join(project.split("-")[1:])
              print("https://github.com/"+owner+"/"+repo+"/compare/"+ cur_commit["commit"]+".."+next_commit["commit"]+" -> "+w + " (" + project + ")")