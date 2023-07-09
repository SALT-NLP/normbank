from GPTLib import *
import os, json, csv
from glob import glob
from tqdm import tqdm
from util import *
import time

def get_prep_det(setting):
    if setting in prepositions_dets:
        return prepositions_dets[setting]
    
    prep = 'in'
    det = 'a'
    if setting[0] in 'aeiou':
        det = 'an'
    return (prep, det)

def get_items(setting, role=None):
    prep, det = get_prep_det(setting)
    
    prompt = f"Some things I might need {prep} {det} {setting}:"

    if role:
        prep_role, det_role = get_prep_det(role)
        prompt = f"Some things I might need {prep} {det} {setting} if I'm {det_role} {role}:"
    
    items = get_completion_list(prompt, verbose=True)
    print(prompt)
    print(items)
    print('--------')
    return items

def main():
    
    if not os.path.exists(f"../data/raw/Settings-Items"):
        os.makedirs(f"../data/raw/Settings-Items")
    
    x = ""
    fns = sorted(glob('../data/raw/Settings-Roles/*.txt'))
    for i, fn in enumerate(fns):

        if x.lower() in {'skip'}:
            continue
            
        setting = fn.split('/')[-1][:-4]
        
        items = get_items(setting, role=None)

        with open(f"../data/raw/Settings-Items/{setting}.txt", 'a') as infile:
            infile.write('\n'.join(items)) 
        
        roles = set()
        with open(f"../data/raw/Settings-Roles/{setting}.txt", 'r') as infile:
            roles = sorted(set([x.strip() for x in infile.readlines()]))       
        
            for role in roles:
                if x.lower() in {'skip'}:
                    continue
                
                items = get_items(setting, role=role)
                
                if not os.path.exists(f"../data/raw/Settings-Roles-Items/{setting}"):
                    os.makedirs(f"../data/raw/Settings-Roles-Items/{setting}")
                
                
                with open(f"../data/raw/Settings-Roles-Items/{setting}/{setting}_{role}.txt", 'a') as infile:
                    infile.write('\n'.join(items))
                    
                time.sleep(10)
                
        time.sleep(10)

main()