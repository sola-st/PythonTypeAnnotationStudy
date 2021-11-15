from collections import OrderedDict, defaultdict
import json
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

directory = r'Resources/type_fix_dataset/'
total = 0
count_dict = defaultdict(lambda: defaultdict(lambda: 0))
fix_for_error_dict = defaultdict(lambda: defaultdict(lambda: 0))
runtime_dict = defaultdict(lambda: 0)
pyre_error_dict = defaultdict(lambda: 0)
pyre_change_dict = defaultdict(lambda: 0)
for data_file in os.listdir(directory):
  if data_file.startswith('type_fix_') and data_file.endswith('.json'):
    with open(directory+'/'+data_file) as f:
      data = json.load(f)       
      for d in data:
        total += 1
        
        # 1. Check for type mismatch between msg and "type_error" field
        msg_err_type = d["full_warning_msg"].split(' ',1)[1].split(':')[0]
        if (d["type_error"] != msg_err_type and 'pyre-fixme' not in d["full_warning_msg"]):
          print(d["full_warning_msg"])
        
        # 2. Count data for each repo
        count_dict['repos'][d['repo'].split('https://github.com/')[-1]] += 1
        
        # 3. Count data for each type_error
        count_dict['type_error'][d['type_error']] += 1

        # 4. Count data for each code_transform
        count_dict['code_transform'][d['code_transform']] += 1
        # 4.1. Count data for each code_transform in type_error
        fix_for_error_dict[d['type_error']][d['code_transform']] += 1

        # 5. Count data where change_runtime is true
        count_dict['change_runtime'][d['change_runtime']] += 1
        # 5.1. What code_transform when change_runtime is true?
        if d['change_runtime']:
          runtime_dict[d['code_transform']] += 1

        # 6. Count data where mentioned_by_pyre is true
        count_dict['mentioned_by_pyre'][d['mentioned_by_pyre']] += 1
        # 6.1. What type_error when mentioned_by_pyre is true?
        if d['mentioned_by_pyre']:
          pyre_error_dict[d['type_error']] += 1
        # 6.2. What code_transform when mentioned_by_pyre is true?
        if d['mentioned_by_pyre']:
          pyre_change_dict[d['code_transform']] += 1

        # 7. Count involved_types distribution
        for t in d['involved_types']:
          count_dict['involved_types'][t] += 1
        # TODO: Get top-5

        # 8. Is isolated_code_change "large", by counting -/+ in git-diff?
        count_dict['isolated_code_change'][1+d['isolated_code_change'].count('\n+')+d['isolated_code_change'].count('\n-')] += 1
        
        # 9. Count type_change distribution for each field: kind, from, to
        count_dict['type_change.kind'][d['type_change']['kind']] += 1
        count_dict['type_change.from'][d['type_change']['from']] += 1
        count_dict['type_change.to'][d['type_change']['to']] += 1

        # 10. Count data for each location
        count_dict['location'][d['location']] += 1

        # 11. Other insights?

# Print the result in JSON (will not be valid, need a little manual fixing)
out_d = {}
for field, field_dict in count_dict.items():
  od = OrderedDict(sorted(field_dict.items()))
  out_d[field] = od
for field, field_dict in out_d.items():
  if (field == 'change_runtime' or 
      field == 'mentioned_by_pyre' or 
      field == 'isolated_code_change' or
      field == 'type_change.kind'):
    df = pd.DataFrame.from_dict(field_dict, orient='index')
    fig = df.plot.bar(title=field, ylabel='count', legend=False, rot=0).get_figure()
    fig.savefig(field+".png")  
  else:  
    # print(list(field_dict.keys()))
    # df = pd.DataFrame.from_dict([field_dict])
    # fig = df.plot(
    #   kind='barh',
    #   title=field, 
    #   yticks=list(field_dict.keys()),
    #   # xlabel='X',
    #   # ylabel='Y',
    #   figsize=(20, 10), 
    #   legend=False, 
    #   rot=0,
    #   colormap='cubehelix',
    #   use_index=False
    # ).get_figure()
    # fig.savefig(field+".png")
    if field == 'involved_types':
      field_dict = dict(sorted(field_dict.items(), key=lambda item: item[1], reverse=True)[:10])
    plt.figure(figsize=(20, 10))
    plt.barh(*zip(*field_dict.items()))
    # plt.yticks(k_list)
    plt.xticks(rotation=0)
    plt.title(field)
    plt.xlabel('count')
    plt.savefig(field+".png")
    plt.clf()
out_d['Total count'] = total
out_d['Fix pattern'] = fix_for_error_dict
out_d['Runtime code change'] = runtime_dict
out_d['Pyre error type'] = pyre_error_dict
out_d['Pyre code change'] = pyre_change_dict
r = json.dumps(out_d, indent=4)
print(r)

# X = list(fix_for_error_dict.keys())
# Y = np.arange(len(X))
# Z = [0] * len(X)

# df = pd.DataFrame(np.c_[Y,Z,Y], index=X)
# df.plot.barh(figsize=(20, 10))
for err, dict in fix_for_error_dict.items():
  if 'Incompatible return type' in err or 'Incompatible variable type' in err or 'Incompatible parameter type' in err:
    # for cc, v in dict.items():
    plt.figure(figsize=(15, 6))
    plt.bar(*zip(*dict.items()))
    plt.xticks(rotation=0)
    plt.title('"'+err+'" Fix Pattern')
    plt.ylabel('count')
    plt.savefig(err+".png")
    plt.clf()

plt.figure(figsize=(18, 8))
plt.barh(*zip(*runtime_dict.items()))
plt.xticks(rotation=0)
plt.title('Code change that changes runtime')
plt.xlabel('count')
plt.savefig("runtime.png")
plt.clf()

plt.figure(figsize=(18, 8))
plt.barh(*zip(*pyre_error_dict.items()))
plt.xticks(rotation=0)
plt.title('Type errors where the fixes are hinted by pyre')
plt.xlabel('count')
plt.savefig("pyre_error.png")
plt.clf()

plt.figure(figsize=(18, 8))
plt.barh(*zip(*pyre_change_dict.items()))
plt.xticks(rotation=0)
plt.title('Code change hinted by pyre')
plt.xlabel('count')
plt.savefig("pyre_cc.png")
plt.clf()

# print('{')
# for field, field_dict in count_dict.items():
#   print("    \"{}\": {{".format(field))
#   od = OrderedDict(sorted(field_dict.items()))
#   out_d[field] = od
#   for nk, nv in od.items():
#     print("        \"{}\": {},".format(nk,nv))
#   print('    },')
# print("    \"Total count\": {}".format(total))
# print('}')
