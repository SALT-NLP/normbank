import re
import pandas as pd
from collections import defaultdict, Counter
from glob import glob
from tqdm import tqdm

OUT_FN = '../hit/temp/subsample.csv'
GLOB = '../data/Behaviors-All-Hand-Filtered/*.txt'
SAMPLE_N = 75
RANDOM_STATE = 1

def condition(name):
    #return name > 'ar' and name < 'cas'
    #return name >= 'cas' and name < 'f'
    #return name >= 'f' and name < 'm'
    #return name >= 'm' and name < 's'
    return name >= 's'

NUM_SETTINGS = 0
behaviors = Counter()
for fn in sorted(glob(GLOB)):
    name = fn.split('/')[-1][:-4]
    if condition(name):
        NUM_SETTINGS += 1
        with open(fn, 'r') as infile:
            for x in infile.readlines():
                behaviors[x.strip()] += 1

behaviors_dict = {}
for fn in sorted(glob(GLOB)):
    name = fn.split('/')[-1][:-4]
    if condition(name):
        with open(fn, 'r') as infile:
            behaviors_dict[name] = [x.strip() for x in infile.readlines()]
    
df = pd.DataFrame(columns=["setting", "behavior", "inv_frequency"])
for setting in tqdm(behaviors_dict):
    for behavior in behaviors_dict[setting]:
        entry = pd.DataFrame.from_dict({
             "setting": [setting],
             "behavior":  [behavior],
             "inv_frequency": [1.0/behaviors[behavior]]
        })

        df = pd.concat([df, entry], ignore_index=True)

df.sample(n=SAMPLE_N*NUM_SETTINGS, random_state=RANDOM_STATE, weights = df.inv_frequency).to_csv(OUT_FN, index=False)