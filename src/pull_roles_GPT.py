from GPTLib import *
import os, json, csv
from glob import glob
from tqdm import tqdm
from util import *

def get_prep_det(setting):
    if setting in prepositions_dets:
        return prepositions_dets[setting]
    
    prep = 'in'
    det = 'a'
    if setting[0] in 'aeiou':
        det = 'an'
    return (prep, det)

def get_roles(setting):
    prep, det = get_prep_det(setting)
    prompt = f"Some roles {prep} {det} {setting}:"
    roles = get_completion_list(prompt, verbose=True) #['this', 'is', 'a', 'test'] #
    print(prompt)
    print(roles)
    print('--------')
    return roles

def main():
    
    outdir = "../data/raw/Settings-Roles"
    with open('../data/raw/settings.txt', 'r') as infile:
        settings = infile.readlines()
        for i, setting in enumerate(settings):
            roles = get_roles(setting)
            
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            
            with open(f"{outdir}/{setting}.txt", 'w') as infile:
                infile.write('\n'.join(roles))

            nxt=""
            if i<len(settings):
                nxt = f" (next={settings[i+1]})"
            x = input(f"Skip or Continue?{nxt}")
            if x.lower() in {'skip'}:
                continue
            elif x.lower() in {'n', 'no'}:
                break

main()