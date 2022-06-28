import json
import numpy as np
from scipy.integrate import simps
from numpy import *
import requests
from lxml import html
import csv  
import re
import json
import requests
from pandas.io.json import json_normalize
import pandas as pd
import numpy as np
from pprint import pprint
import time
import copy


ignored_warning_kinds = [
    "Undefined import [21]",
    "Undefined or invalid type [11]",
    "Undefined name [18]",
    "Undefined attribute [16]",
]

def slopee(x1,y1,x2,y2):
    x = (y2 - y1) / (x2 - x1)
    return x

def read_results(name):
    with open(name) as fp:
        r = json.load(fp)
    return r

def count_filtered_warnings(kind_to_nb):
    total = 0
    for kind, nb in kind_to_nb.items():
        if kind not in ignored_warning_kinds:
            total += nb
    return total

def Average(lst):
    return sum(lst) / len(lst)

def statistics_computation():
    with open('../Input/oneplus_list.json') as fh:
        articles = json.load(fh)

    article_urls = [article['typeLastProjectVersion_dict'] for article in articles]

    with open('../stars.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
    
        i = 1
        for l in article_urls:
            for link in l:
                ll = []
                j = 0
                time.sleep(61)
                out = re.sub('https://github.com/', '', link[0]).replace('/', '-')
                url = link[0].replace('https://github.com/',"")
                ll.append(out)
                all_contributors = list()
                page_count = 1
                while True:
                    j += 1
                    #print(j)    
                    contributors = requests.get("https://api.github.com/repos/"+url+"/commits?page=%d"%page_count, auth=('luca-digrazia','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'), timeout=10)
                    #if j == 13:
                     #   print(j)
                    if contributors != None and contributors.status_code == 200 and len(contributors.json()) > 0:
                        all_contributors = all_contributors + contributors.json()
                    else:
                        break
                    page_count = page_count + 1
                count=len(all_contributors)
                ll.append(str(count))
                writer.writerow(ll)
                print(i, "-------------------%d" %count)
                i += 1

def statistics_read():
    with open('../Input/oneplus_list.json') as fh:
        articles = json.load(fh)

    article_urls = [article['typeLastProjectVersion_dict'] for article in articles]

    art = []
    i = 0
    while i < 10:
        with open("../Input/Top1000_Python201"+str(i)+"_Complete.json") as fh:
            art += json.load(fh)
        i += 1

    with open('../starssss.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
    
        i = 1
        for l in article_urls:
            for link in l:
                ll = []
                j = 0
                out = re.sub('https://github.com/', '', link[0]).replace('/', '-')
                url = link[0].replace('https://github.com/',"")
                ll.append(out)
                
                for repo in art:
                    if repo['html_url'] == link[0]:
                        ll.append(repo['stargazers_count'])
                        ll.append(repo['open_issues_count'])
                        ll.append(repo['forks_count'])
                        break

                writer.writerow(ll)
                print(i)
                i += 1

#statistics_computation()
#statistics_read()
from os import listdir
from os.path import isfile, join

with open('../pattern.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)
    onlyfiles = [f for f in listdir('.') if isfile(join('.', f))]

    with open('../repos.csv', 'r') as file:
        reader = csv.reader(file)
        
        regular = 0
        occasional = 0
        sprinter = 0
        inconsistent = 0
        unknown = 0


        for f in onlyfiles:
            #if "history_MrGiovanni-UNetPlusPlus.json" not in f:
            #   continue

            try:
                results = read_results(f)

                dates = []
                locs = []
                warnings = []
                annotation_evol = []
                for r in reversed(results):
                    date = r["commit_date"]
                    date = date.split(" ")[0]
                    dates.append(date)
                    locs.append(r["loc"])
                    annotation_evol.append(r["nb_param_types"] +
                                                r["nb_return_types"] + r["nb_variable_types"])
                    nb_warnings = count_filtered_warnings(r["kind_to_nb"])
                    warnings.append(nb_warnings)

                
                ratio = [(i / j if j else 0) for i, j in zip(annotation_evol, locs)]
                

                area_locs = trapz(locs, dx=1)
                #print("area =", area_locs)

                area_ann = trapz(annotation_evol, dx=1)
                #print("area =", area_ann)

                #print("Diff area =", abs(area_locs - area_ann))
                #print("Total annotations =", annotation_evol)

                slope_ann = []
                i = 0
                while i < len(annotation_evol)-1:
                    slope_ann.append(slopee(i, annotation_evol[i], i + 1, annotation_evol[i+1]))
                    i += 1

                #print("Slope ann",slope_ann)
                #print("Slope avg", average(slope_ann))
                #print("Slope zeros", slope_ann.count(0.0))

                slope_locs = []
                i = 0
                while i < len(locs)-1:
                    slope_locs.append(slopee(i, locs[i], i + 1, locs[i+1]))
                    i += 1

                #print("Slope locs",slope_locs)

                #print("#TESTTTTTTTTTTTTTTT")

                area_ratio = trapz(ratio, dx=1)
                #print("area ratio =", area_ratio)

                #check if element in list is higher than 5

                lll = []
                lll.append(f.replace(".json", "").replace("history_", ""))
                #reader2 = copy.deepcopy(reader)

                for row in reader:
                    if lll[0] == row[0]:
                        lll.append(row[1])
                        break

                file.seek(0)
                reader.__init__(file, delimiter=",")
                
                if Average(annotation_evol) == 0:
                    #print("Average = 0")
                    lll.append("NULL")
                    
                    continue
                elif (1 < Average(annotation_evol) < 15) or slope_ann.count(0.0) > 8:
                    lll.append("OCCASIONAL")
                    print(f,"## Occasional users.")
                    occasional += 1
                elif slope_ann.count(0.0) >= 4: 
                    #print(f,"## Type sprinters.")
                    lll.append("SPRINTER")
                    sprinter += 1
                elif average(slope_ann) >= 0 and slope_ann.count(0.0) < 4:
                    #print(f,"## Regular annotators.")
                    lll.append("REGULAR")
                    regular +=1
                else:
                    print(f,"## UNKNOWN.")
                    lll.append("UNKNOWN")
                    unknown += 1
                #print("\n")
                writer.writerow(lll)
            except:
                print("Error in file:", f)
                writer.writerow(lll)
                continue

        tot = regular + occasional + sprinter + unknown
        print("regular", regular, regular/tot*100, "%\noccasional", occasional, occasional/tot*100, "%\nsprinter", sprinter,sprinter/tot*100, "%\nunknown", unknown, unknown/tot*100)
