from GPTLib import *
import os, json, csv
from glob import glob
from tqdm import tqdm
from util import *
import time

attribute_metadata = {
    'age bracket': {
        'prefix': 'were ',
        'determiner': True,
        'postfix': ''
    },
    
    'children': {
        'prefix': 'had ',
        'determiner': False,
        'postfix': ''
    },
    
    'country-subset': {
        'prefix': 'were living in ',
        'determiner': False,
        'postfix': ''
    },
    
    'diet': {
        'prefix': 'were following ',
        'determiner': True,
        'postfix': ' diet'
    },
    
    'disability': {
        'prefix': 'had ',
        'determiner': False,
        'postfix': ''
    },
    
    'education': {
        'prefix': 'were attending ',
        'determiner': False,
        'postfix': ''
    },
    
    'emotion': {
        'prefix': 'were feeling ',
        'determiner': False,
        'postfix': ''
    },
    
    'employment': {
        'prefix': 'were ',
        'determiner': False,
        'postfix': ''
    },
    
    'gender': {
        'prefix': 'were ',
        'determiner': True,
        'postfix': ''
    },
    
    'marriage': {
        'prefix': 'were ',
        'determiner': False,
        'postfix': ''
    },
    
    'political ideology': {
        'prefix': 'were ',
        'determiner': True,
        'postfix': ''
    },
    
    'race or ethnicity': {
        'prefix': 'were ',
        'determiner': True,
        'postfix': ' person'
    },
    
    'religion': {
        'prefix': 'followed ',
        'determiner': False,
        'postfix': ''
    },
    
    'sexuality': {
        'prefix': 'were ',
        'determiner': False,
        'postfix': ''
    },
    
    'social class': {
        'prefix': 'were ',
        'determiner': False,
        'postfix': ''
    }  
}

def get_det(setting):    
    if setting[0] in 'aeiou':
        return 'an '
    return 'a '

def get_prep_det(setting):
    if setting in prepositions_dets:
        return prepositions_dets[setting]
    
    prep = 'in'
    det = 'a'
    if setting[0] in 'aeiou':
        det = 'an'
    return (prep, det)

def get_normal_behaviors(setting, attribute_class, attribute):
    prep, det = get_prep_det(setting)
    
    assert attribute_class in attribute_metadata
    
    det = get_det(attribute) if attribute_metadata[attribute_class]['determiner'] else ''

    prompt = f"""Some things you would do {prep} {det} {setting} if you {attribute_metadata[attribute_class]['prefix']}{det}{attribute}{attribute_metadata[attribute_class]['postfix']}:
-"""
    
    behaviors = get_completion_list(prompt, verbose=True, drop_keywords={"^you would need to ", "^you would "})
    print(prompt)
    print(behaviors)
    print('--------')
    return behaviors


def get_taboo_behaviors(setting, attribute_class, attribute):
    prep, det = get_prep_det(setting)
    
    assert attribute_class in attribute_metadata
    
    det = get_det(attribute) if attribute_metadata[attribute_class]['determiner'] else ''

    prompt = f"""Some things you would never do {prep} {det} {setting} if you {attribute_metadata[attribute_class]['prefix']}{det}{attribute}{attribute_metadata[attribute_class]['postfix']}:
-"""
    
    drop1 = f"^(a |an )?{attribute} should never "
    drop2 = f" if you {attribute_metadata[attribute_class]['prefix']}{det}{attribute}{attribute_metadata[attribute_class]['postfix']}"
    drop3 = f" (in|into|at|on) (a |an )?{setting}"
    
    behaviors = get_completion_list(prompt, verbose=True, drop_keywords={drop1, drop2, drop3, "^don't ", "^never ", "^you would never ", "^you should never "})
    print(prompt)
    print(behaviors)
    print('--------')
    return behaviors

def main():
    
    x = ""
    fns = sorted(glob('../data/raw/Settings-Roles/*.txt'))
    for i, fn in enumerate(fns):
        if i<260:
            continue

        if x.lower() in {'skip'}:
            continue
            
        setting = fn.split('/')[-1][:-4]       
        
        for attribute_class in attribute_metadata:
            
            attributes = set()
            with open(f"../data/raw/Attributes/{attribute_class}.txt", 'r') as infile:
                attributes = sorted(set([x.strip() for x in infile.readlines()]))
                
                for attribute in attributes:

                    if x.lower() in {'skip'}:
                        continue

                    if not os.path.exists(f"../data/raw/Settings-Attributes-Behaviors_Taboo/{setting}"):
                        os.makedirs(f"../data/raw/Settings-Attributes-Behaviors_Taboo/{setting}")
                    
                    if os.path.exists(f"../data/raw/Settings-Attributes-Behaviors_Taboo/{setting}/{setting}_{attribute}.txt"):
                        print('skipping', setting, attribute)
                        continue
                
                    taboo = get_taboo_behaviors(setting, attribute_class, attribute)                
                    with open(f"../data/raw/Settings-Attributes-Behaviors_Taboo/{setting}/{setting}_{attribute}.txt", 'a') as infile:
                        infile.write('\n'.join(taboo))

                    time.sleep(10)
                
        time.sleep(10)

main()