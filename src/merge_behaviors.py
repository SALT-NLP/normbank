import re, spacy
import pandas as pd
from collections import defaultdict
from glob import glob
from tqdm import tqdm

def pipeline(string, role="", setting=""):
    
    string = remove_conditional(string)
    string = remove_negation_artifacts(string)
    string = remove_elaboration(string)
    string = grammatical(string)
    string = neutralize(string)
    string = remove_role(string, role)
    string = remove_setting(string, setting)
    string = clean_up(string)
    return string
    
def grammatical(string):
    #string = re.sub(r'(\btheir\b|\bhis\b|\bher\b)', 'your', string)
    return string

def neutralize(string):
    string = re.sub('proper(ly)?', '', string)
    string = re.sub(r'(so )?(he|she|you|they|we) should', '', string)
    string = re.sub(r'(so )?(he|she|you|they|we) would', '', string)
    string = re.sub(r'be able to', '', string)
    string = re.sub(r'see someone', '', string)
    string = re.sub(r'try to', '', string)
    return string

def remove_role(string, role):
    string = re.sub(f"{role.lower()}(s)?( should)?", '', string)
    return string

def remove_setting(string, setting):
    string = re.sub(f"(on|in|at) (a |an |the )?{setting.lower()}(s)?", '', string)
    return string
    
def remove_conditional(string):
    split = re.split('if (?:he|she|you|they|we)', string)
    if len(split)==1:
        return split[0]
    elif len(split) == 2:
        if len(split[0])>len(split[1]):
            return split[0]
        else:
            return split[1]
    else:
        return string
        
def remove_elaboration(string):
    split = re.split('because', string)
    if len(split)<2:
        return string
    else:
        return split[0]
    
def remove_negation_artifacts(string):
    string = re.sub(r'\bdo not\b', '', string)
    string = re.sub(r'\bnever\b', '', string)
    string = re.sub(r'\bnot\b', '', string)
    string = re.sub(r'\bforget to\b', '', string)
    string = re.sub(r'\brefuse to\b', '', string)
    string = re.sub(r'\bfail to\b', '', string)
    string = re.sub(r'\banything\b', 'something', string)
    string = re.sub(r'\banyone\b', 'someone', string)
    string = re.sub(r'\bin any way\b', '', string)
    string = re.sub(r'\bany\b', '', string)
    
    return string

def clean_up(string):
    string = re.sub('\s+', ' ', string)
    string = re.sub('^[0-9.]+', '', string)
    string = re.sub('\b(on|in|at)$', '', string)
    return string


nlp = spacy.load("en_core_web_sm")
def filter_must_have_verb_not_relative_no_subj(string_set):
    out = set()
    for string in string_set:
        if '(' in string or ')' in string:
            continue
        doc = nlp(string)
        POS = {t.pos_ for t in doc}
        DEP = {t.dep_ for t in doc}
        if ('VERB' in POS) and ('mark' not in DEP) and ('nsubj' not in DEP) and ('auxpass' not in DEP):
            out.add(string)
    return out

# Merge_Behaviors
print("Merging behaviors...")
behaviors_dict = defaultdict(set)
fns = sorted(glob('../data/Settings-Roles-Behaviors_Taboo/*/*.txt'))
fns += sorted(glob('../data/Settings-Roles-Behaviors_Normal/*/*.txt'))
fns += sorted(glob('../data/Settings-Attributes-Behaviors_Taboo/*/*.txt'))
for fn in tqdm(fns):
    name = fn.split('/')[-1][:-4]
    setting, role = name.split('_')
    with open(fn, 'r') as infile:
        
        add = filter_must_have_verb_not_relative_no_subj(set([pipeline(x, role, setting).strip() for x in infile.readlines()]))
        behaviors_dict[setting].update(add)
        
        if "so see someone cleaning their teeth or taking a bath" in add:
            print(fn)

print("Writing behaviors...")
for setting in tqdm(behaviors_dict):
    with open(f'../data/Behaviors-All-Merged/{setting}.txt', 'w') as outfile:
        outfile.write('\n'.join([x for x in behaviors_dict[setting] if len(x)]))  