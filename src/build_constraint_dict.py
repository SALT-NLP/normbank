import json
from glob import glob

def condition(name):
    #return name > 'ar' and name < 'cas'
    #return name >= 'cas' and name < 'f'
    #return name >= 'f' and name < 'm'  
    #return name >= 'm' and name < 's'
    #return name >= 's'
    #return name < 'c'
    #return (name >= 'c') and (name < 'h')
    #return (name >= 'h') and (name < 's')
    return True

def alpha_sort_ignore_det(string):
    if not len(string):
        return 0
    elif string[:2] == 'a ':
        return string[2].lower()
    elif string[:3] == 'an ':
        return string[3].lower()
    elif string[:4] == 'the ':
        return string[4].lower()
    else:
        return string[0].lower()

constraint_dict = {}
constraint_dict['the environment'] = {}
for fn in sorted(glob('../data/Environment/*.txt')):
    name = fn.split('/')[-1][:-4]
    with open(fn, 'r') as infile:
        lst = [x.strip() for x in infile.readlines()]
        if name not in {'time period', 'temperature', 'noise', 'day of the week', 'time of day'}:
            lst = sorted(set(lst), key=alpha_sort_ignore_det)
        constraint_dict['the environment'][name] = lst
        
constraint_dict["the PERSON PERFORMING BEHAVIOR's role"] = {}
constraint_dict["some OTHER PERSON's role"] = {}
for fn in sorted(glob('../data/Settings-Roles/*.txt')):
    name = fn.split('/')[-1][:-4] + ' role'
    with open(fn, 'r') as infile:
        lst = list(sorted(set([x.strip() for x in infile.readlines()]),
                          key=alpha_sort_ignore_det
                         ))
        constraint_dict["the PERSON PERFORMING BEHAVIOR's role"][name] = lst
        constraint_dict["some OTHER PERSON's role"][name] = lst
        
constraint_dict["the PERSON PERFORMING BEHAVIOR's attribute"] = {}
constraint_dict["some OTHER PERSON's attribute"] = {}
# constraint_dict["the JUDGE's attribute"] = {}
for fn in sorted(glob('../data/Attributes/*.txt')):
    name = fn.split('/')[-1][:-4]
    if '-subset' in name:
        continue
    if 'race-ethnicity' == name:
        name = 'race or ethnicity'
    if name in {'emotion', 'political ideology', 'disability'}:
        continue
    with open(fn, 'r') as infile:
        lst = [x.strip() for x in infile.readlines()]
        if name not in {'age bracket', 'children', 'education', 'gender'}:
            lst = sorted(set(lst), key=alpha_sort_ignore_det)
        constraint_dict["the PERSON PERFORMING BEHAVIOR's attribute"][name] = lst
        constraint_dict["some OTHER PERSON's attribute"][name] = lst

constraint_dict2 = {}#constraint_dict#{}        
constraint_dict2["the PERSON PERFORMING BEHAVIOR is also doing"] = {}
constraint_dict2["some OTHER PERSON is also doing"] = {}
for fn in sorted(glob('../data/Behaviors-All-Hand-Filtered/*.txt')):
    name = fn.split('/')[-1][:-4] + ' behavior'
    with open(fn, 'r') as infile:
        lst = list(sorted(set([x.strip() for x in infile.readlines()]),
                          key=alpha_sort_ignore_det
                         ))
        if condition(name):
            constraint_dict2["the PERSON PERFORMING BEHAVIOR is also doing"][name] = lst
            constraint_dict2["some OTHER PERSON is also doing"][name] = lst

# with open('constraint_dict.json', 'w') as outfile:
#     json.dump(constraint_dict2, outfile, ensure_ascii=False)
print(json.dumps(constraint_dict2, ensure_ascii=False))
with open('tmp.json', 'w') as outfile:
    json.dump(constraint_dict2, outfile)
# print() 
#print(json.dumps(constraint_dict, ensure_ascii=False))