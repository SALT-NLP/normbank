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

def get_normal_behaviors(setting, role=None):
    prep, det = get_prep_det(setting)
    
    prompt = f"""Some things you would do {prep} {det} {setting}:

-"""

    if role:
        prep_role, det_role = get_prep_det(role)
        prompt = f"""Some things you would do {prep} {det} {setting} if you were {det_role} {role}:
-"""
    
    behaviors = get_completion_list(prompt, verbose=True, drop_keywords={"^you would "})
    print(prompt)
    print(behaviors)
    print('--------')
    return behaviors


def get_taboo_behaviors(setting, role=None):
    prep, det = get_prep_det(setting)
    
    prompt = f"""Some things your friends would tell you not to do when you are {prep} {det} {setting}:
-"""

    if role:
        prep_role, det_role = get_prep_det(role)
        prompt = f"""Some things {det_role} {role} should never do {prep} {det} {setting}:
-"""
    
    drop = f"^(a |an )?{role} should never "
    behaviors = get_completion_list(prompt, verbose=True, drop_keywords={drop, "^don't ", "^never "})
    print(prompt)
    print(behaviors)
    print('--------')
    return behaviors

def main():
    
    if not os.path.exists(f"../data/raw/Settings-Items"):
        os.makedirs(f"../data/raw/Settings-Items")
    
    x = ""
    fns = sorted(glob('../data/raw/Settings-Roles/*.txt'))
    for i, fn in enumerate(fns):

        if x.lower() in {'skip'}:
            continue
            
        setting = fn.split('/')[-1][:-4]
        
        normal = get_normal_behaviors(setting, role=None)
        with open(f"../data/raw/Settings-Behaviors_Normal/{setting}.txt", 'a') as infile:
            infile.write('\n'.join(normal))
            
        taboo = get_taboo_behaviors(setting, role=None)
        with open(f"../data/raw/Settings-Behaviors_Taboo/{setting}.txt", 'a') as infile:
            infile.write('\n'.join(taboo))
        
        roles = set()
        with open(f"../data/raw/Settings-Roles/{setting}.txt", 'r') as infile:
            roles = sorted(set([x.strip() for x in infile.readlines()]))       
        
            for role in roles:
                if x.lower() in {'skip'}:
                    continue
                
                if not os.path.exists(f"../data/raw/Settings-Roles-Behaviors_Normal/{setting}"):
                    os.makedirs(f"../data/raw/Settings-Roles-Behaviors_Normal/{setting}")
                    
                if not os.path.exists(f"../data/raw/Settings-Roles-Behaviors_Taboo/{setting}"):
                    os.makedirs(f"../data/raw/Settings-Roles-Behaviors_Taboo/{setting}")
                
                normal = get_normal_behaviors(setting, role=role)                
                with open(f"../data/raw/Settings-Roles-Behaviors_Normal/{setting}/{setting}_{role}.txt", 'a') as infile:
                    infile.write('\n'.join(normal))

                taboo = get_taboo_behaviors(setting, role=role)                
                with open(f"../data/raw/Settings-Roles-Behaviors_Taboo/{setting}/{setting}_{role}.txt", 'a') as infile:
                    infile.write('\n'.join(taboo))
                    
                time.sleep(10)
                
        time.sleep(10)

main()