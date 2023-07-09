import json, math, jellyfish, re, strsimpy
import numpy as np
from itertools import product
from collections import deque, defaultdict
from scipy.optimize import linear_sum_assignment

# TODO: spell checking
# TODO: auto re-assign category for environment

with open('constraint_dict.json', 'r') as infile:
    CONSTRAINT_JSON = json.load(infile)

NORMALIZED_RELATIONS = {
            'is not at or above': 'is less than',
            'is not equal to or above': 'is less than',
            'is below': 'is less than',
            'is not equal to or greater than': 'is less than',
            'is not greater than or equal to': 'is less than',
            'is equal to or less than': 'is less than or equal to',
            'is not greater than': 'is less than or equal to',
            'is not less than': 'is greater than or equal to',
            'is equal to or greater than': 'is greater than or equal to',
            'is not equal to or less than': 'is greater than or equal to'
        }

def normalize_relation(relation):
    mapping = NORMALIZED_RELATIONS
    if relation in mapping:
        return mapping[relation]
    return relation

def sanitize(string):
    s = re.sub("\n", " ", string.lower())
    s = re.sub("\r", " ", s)
    s = re.sub("[\[\]]", "", s)
    s = re.sub("[\s]{2,}", " ", s)
    return s

def lev_match(string, options, thresh=0.1, verbose=False):
    if string in options:
        return string

    distances = np.array([strsimpy.normalized_levenshtein.NormalizedLevenshtein().distance(string.lower(), 
                                                                                           s.lower()) for s in options])
    argmin = np.argmin(distances)
    out = options[argmin]
    if (distances[argmin] < thresh):
        if verbose:
            print(f"matched {string} with {out}")
        return out
    return string
    
# this is a list of sets: all constraint categories, names, relations, and values, so we can check how many inputs are original to annotators
CJSON_EXP = [list(CONSTRAINT_JSON.keys()), 
             {sanitize(k) for key in list(CONSTRAINT_JSON.keys()) for k in list(CONSTRAINT_JSON[key].keys())},
             {'is', 'is not', 
              'is less than',
              'is less than or equal to',
              'is greater than',
              'is greater than or equal to',
             }.union(set(NORMALIZED_RELATIONS.values())),
             {sanitize(kk) for key in list(CONSTRAINT_JSON.keys()) for k in list(CONSTRAINT_JSON[key].keys()) for kk in list(CONSTRAINT_JSON[key][k])}
            ] 

POLYSEMOUS = {'dry', 'private', 'hazardous', 'high', 'dirty'} # empty, clean, hot
VALUE_TO_NAME = defaultdict(lambda: defaultdict(set))
for code, key in zip(['E', 'A'],
                     ['the environment', "the PERSON PERFORMING BEHAVIOR's attribute"]):
    for k in list(CONSTRAINT_JSON[key].keys()):
        for kk in list(CONSTRAINT_JSON[key][k]):
            name = sanitize(k)
            value = sanitize(kk)

            VALUE_TO_NAME[code][value].add(name)
            
def match(constraint, verbose=False):
    constraint_copy = constraint.copy()
    CAT = constraint_copy.category
    VAL = constraint_copy.value
    DIC = {}
    
    if CAT == 'the environment':
        DIC = VALUE_TO_NAME['E']
    elif CAT in {"the PERSON PERFORMING BEHAVIOR's attribute", "some OTHER PERSON's attribute"}:
        DIC = VALUE_TO_NAME['A']

    if (constraint.value in DIC) and len(DIC[VAL])==1 and list(DIC[VAL])[0] not in POLYSEMOUS:
        constraint_copy.name = list(DIC[VAL])[0]
        
    if (constraint.name == 'country'):
        constraint_copy.category = 'the environment'

    if (constraint_copy.name != constraint.name) and verbose:
        print(f"matched {constraint} to {constraint_copy}")
        
    return constraint_copy
    
class Constraint(object):
    
    def __init__(self, category, name, relation, value, similarity_dict):
        self.category = lev_match(category, CJSON_EXP[0], thresh=0.1, verbose=True) 
        self.name = sanitize(name)
        self.relation = normalize_relation(sanitize(relation))
        self.value = sanitize(value)
        self.similarity_dict = similarity_dict
        
        # quick access code for category
        self.cat = "UNK"
        if self.category == "the environment":
            self.cat = "ENV"
        elif self.category == "the PERSON PERFORMING BEHAVIOR is also doing":
            self.cat = "PBH"
        elif self.category == "the PERSON PERFORMING BEHAVIOR's attribute":
            self.cat = "PAT"
        elif self.category == "the PERSON PERFORMING BEHAVIOR's role":
            self.cat = "PRL"
        elif self.category == "some OTHER PERSON's attribute":
            self.cat = "OAT"
        elif self.category == "some OTHER PERSON's role":
            self.cat = "ORL"
            
    def __eq__(self, other): 

        return self.category == self.category\
        and self.name == other.name\
        and self.relation == other.relation\
        and self.value == other.value\
    
    def __hash__(self):
        return hash((self.category, self.name, self.relation, self.value))
        
    def __str__(self):
        if self.category == "the environment":
            return f"{self.name} {self.relation} '{self.value}'"
        elif self.category == "the PERSON PERFORMING BEHAVIOR is also doing":
            return f"[PERSON]'s behavior {self.relation} '{self.value}'"
        elif self.category == "the PERSON PERFORMING BEHAVIOR's attribute":
            return f"[PERSON]'s {self.name} {self.relation} '{self.value}'"
        elif self.category == "the PERSON PERFORMING BEHAVIOR's role":
            return f"[PERSON]'s role {self.relation} '{self.value}'"
        elif self.category == "some OTHER PERSON's attribute":
            return f"[OTHER]'s {self.name} {self.relation} '{self.value}'"
        elif self.category == "some OTHER PERSON's role":
            return f"[OTHER]'s role {self.relation} '{self.value}'"
        return f"{self.category} {self.name} {self.relation} '{self.value}'"
    
    def human_str(self):
        if self.category == "the environment":
            return f"{self.name} {self.relation} '{self.value}'"
        elif self.category == "the PERSON PERFORMING BEHAVIOR is also doing":
            return f"PERSON's behavior {self.relation} '{self.value}'"
        elif self.category == "the PERSON PERFORMING BEHAVIOR's attribute":
            return f"PERSON's {self.name} {self.relation} '{self.value}'"
        elif self.category == "the PERSON PERFORMING BEHAVIOR's role":
            return f"PERSON's role {self.relation} '{self.value}'"
        elif self.category == "some OTHER PERSON's attribute":
            return f"OTHER's {self.name} {self.relation} '{self.value}'"
        elif self.category == "some OTHER PERSON's role":
            return f"OTHER's role {self.relation} '{self.value}'"
        return f"{self.category} {self.name} {self.relation} '{self.value}'"
    
    def similarity(self, other, level=3): 
        if level==0:
            return self.similarity_dict[self.category][other.category]
        elif (self.category == other.category):
            if (level==1): return self.similarity_dict[self.name][other.name]
            if (self.name == other.name):
                if (level==2): return self.similarity_dict[self.relation][other.relation]
                if (self.relation == other.relation) and (level==3):
                    return self.similarity_dict[self.value][other.value]
        return 0
    
    def soft_eq(self, other, thresh=0.6):
        return self.similarity(other)>thresh
    
    def copy(self):
        return Constraint(self.category, self.name, self.relation, self.value, self.similarity_dict)
    
    def is_preset(self, level=""):
        if self.category in CJSON_EXP[0]:
            if level=='category':
                return True
            elif self.name in CJSON_EXP[1]:
                if level=='name':
                    return True
                elif self.relation in CJSON_EXP[2]:
                    if level=='relation':
                        return True
                    elif self.value in CJSON_EXP[3]:
                        return True
        return False   

class ConstraintTable(object):
    
    def __init__(self, similarity_dict):
        self.similarity_dict = similarity_dict
        self.constraints = []
        self.constraint_order = defaultdict(lambda: 7, {
            "some OTHER PERSON's role": 1,
            "some OTHER PERSON's attribute": 2,
            "the PERSON PERFORMING BEHAVIOR's role": 3,
            "the PERSON PERFORMING BEHAVIOR's attribute": 4,
            "the PERSON PERFORMING BEHAVIOR is also doing": 5,
            "the environment": 6
        })
        self.random_order = np.argsort(np.random.randn(10))
        
    def __str__(self):
        return ' [AND] '.join([str(C) for C in self.sorted_constraints()])
    
    def __len__(self):
        return len(self.constraints)
    
    def __getitem__(self, i):
        return self.sorted_constraints()[i]
    
    def html_representation(self):
        inner = ' '.join([f"<li>{constraint.human_str()}</li>" for constraint in self.sorted_constraints()])
        
        out = f"""<ol>{inner}</ol>"""
        return out
    
    def sorted_constraints(self):
        return sorted(self.constraints, key=lambda x: (self.constraint_order[x.category], x.name, x.value) )
    
    def shuffled_constraints(self):
        lst = []
        for idx in self.random_order:
            if idx<len(self.constraints):
                lst.append(self.constraints[idx])
        return lst
    
    def is_duplicate(self, constraint):
        for c in self.constraints:
            if c==constraint:
                return True
            if self.is_exclusive(constraint)\
            and constraint.relation=='is not'\
            and constraint.name==c.name and c.relation=='is':
                return True
        return False
        
    def add_constraint(self, category, name, relation, value):
        if type(category)==str and len(category) \
        and type(name)==str and len(name) \
        and type(relation)==str and len(relation) \
        and type(value)==str and len(value):
            C = Constraint(category, name, relation, value, self.similarity_dict)
            self.check_consistent_constraint(C)
            if not self.is_duplicate(C):
                self.constraints.append(match(C))
            
    def add_constraint_c(self, constraint):
        if type(constraint)==Constraint \
        and type(constraint.category)==str and len(constraint.category) \
        and type(constraint.name)==str and len(constraint.name) \
        and type(constraint.relation)==str and len(constraint.relation) \
        and type(constraint.value)==str and len(constraint.value):
            self.check_consistent_constraint(constraint)
            if not self.is_duplicate(constraint):
                self.constraints.append(match(constraint))
            
    def is_exclusive(self, constraint):
        
        if (constraint.category in CONSTRAINT_JSON)\
        and (constraint.name in CONSTRAINT_JSON[constraint.category])\
        and (constraint.value in CONSTRAINT_JSON[constraint.category][constraint.name]):
            if constraint.name in {'cleanliness', 'day of the week', 'noise', 
                                   'temperature', 'time of day', 'time period',
                                   'age bracket', 'children', 'country', 'diet',
                                   'marriage', 'gender'
                                  }:
                return True
            if 'role' in constraint.category:
                return True
        return False
            
    def check_consistent_constraint(self, constraint):
        if self.is_exclusive(constraint):
            for c in self.constraints:
                if (c.category==constraint.category)\
                and (c.name==constraint.name)\
                and c.relation=='is':
                    if (c.relation!=constraint.relation) and (c.value==constraint.value):
                        raise Exception("Incompatible Constraints:", str(c), str(constraint))
                    if (c.relation==constraint.relation) and (c.value!=constraint.value):
                        raise Exception("Incompatible Constraints:", str(c), str(constraint))
        return True
    
    def copy(self):
        CT = ConstraintTable(self.similarity_dict)
        CT.constraints = [c.copy() for c in self.constraints]
        return CT
        
    def compare(self, other, soft=0):
        
        eq = lambda s, o: s==o
        if soft:
            eq = lambda s, o: s.soft_eq(o, thresh=soft)
            
        def is_in(constr_s, constraints=other.constraints):
            for constr_o in constraints:
                if eq(constr_o, constr_s):
                    return True
            return False
        
        intersection = [c for c in self.constraints if is_in(c, other.constraints)]
        left = [c for c in self.constraints if not is_in(c, intersection)]
        right = [c for c in other.constraints if not is_in(c, intersection)]
        
        out = {
            'intersection': len(intersection),
            'union': len(left) + len(intersection) + len(right)
        }
        
        if out['union']:
            out['jaccard'] = out['intersection'] / out['union']
        else:
            out['jaccard'] = 0
        
        return out
        
class ConstraintSet(object):
    
    def __init__(self, similarity_dict={}, max_tables=5, max_rows=10):
        
        self.setting = None
        self.behavior = None
        self.worker_id = None
        self.metadata = None
        self.similarity_dict = similarity_dict
        
        # dictionary of lists of ConstraintTable objects
        self.tables = {
            'expected': [],
            'normal': [],
            'taboo': []
        }
        
        self.max_tables = max_tables
        self.max_rows = max_rows
        
    def __str__(self):
        out = f"<{self.setting}, {self.behavior}>\n"
        for table_name in self.tables.keys():
            table_set = self.tables[table_name]
            out += (f"\n=======[{table_name}]=======\n")
            out += ('\n---OR---\n'.join([str(table) for table in table_set]))
        return out
    
    def __len__(self):
        return sum([len(table) for table_name in self.tables for table in self.tables[table_name]])
    
    def tup_has_nan(self, tup):
        for item in tup:
            if not item:
                return True
            if item == 'nan':
                return True
            if type(item) in {int, float} and math.isnan(item):
                return True
        return False
    
    def pull_constraint_tups(self, row, table_name, L, subset_role=False, subset_not_role=False):
        tups = []
        for table_row_idx in range(1, self.max_rows):
            tup = ()
            
            try:
                tup = (row[f'Answer.{table_name}{L}_category{table_row_idx}'],
                row[f'Answer.{table_name}{L}_type{table_row_idx}'],
                row[f'Answer.{table_name}{L}_relation{table_row_idx}'],
                row[f'Answer.{table_name}{L}_value{table_row_idx}'])
            except:
                pass
            
            if len(tup) and not self.tup_has_nan(tup):
                if ((tup[0]=="the PERSON PERFORMING BEHAVIOR's role") and (tup[2]=='is')):
                    if subset_role: tups.append(tup)
                elif subset_not_role:
                    tups.append(tup)
        return tups
        
    def from_mturk(self, row, rectify=True): # row is a row of the MTurk output
        self.setting = row['Input.setting']
        self.behavior = row['Input.behavior']
        self.worker_id = row['WorkerId']
        
        self.metadata = dict(row[['HITId',
                                 'HITTypeId',
                                 'Title',
                                 'Description',
                                 'Keywords',
                                 'Reward',
                                 'CreationTime',
                                 'MaxAssignments',
                                 'RequesterAnnotation',
                                 'AssignmentDurationInSeconds',
                                 'AutoApprovalDelayInSeconds',
                                 'Expiration',
                                 'NumberOfSimilarHITs',
                                 'LifetimeInSeconds',
                                 'AssignmentId',
                                 'WorkerId',
                                 'AssignmentStatus',
                                 'AcceptTime',
                                 'SubmitTime',
                                 'AutoApprovalTime',
                                 'ApprovalTime',
                                 'RejectionTime',
                                 'RequesterFeedback',
                                 'WorkTimeInSeconds',
                                 'LifetimeApprovalRate',
                                 'Last30DaysApprovalRate',
                                 'Last7DaysApprovalRate']])
        
        for table_name in self.tables.keys():
            for L in range(1, self.max_tables+1):
                CT = ConstraintTable(self.similarity_dict)
                tups_role = self.pull_constraint_tups(row, table_name, L, subset_role=True)
                tups_not_role = self.pull_constraint_tups(row, table_name, L, subset_not_role=True)
                for tup in tups_not_role:
                    CT.add_constraint(*tup)
                    if not len(tups_role):
                        self.tables[table_name].append(CT)
                for tup in tups_role:
                    CT_ = CT.copy()
                    CT_.add_constraint(*tup)
                    if len(CT_):
                        self.tables[table_name].append(CT_)
        if rectify: self.rectify_constraints()
                    
    def rectify_constraints(self):
        self.propagate_taboo_roles()
        
    def flip_logical_relation(self, r):
        if r=='is':
            return 'is not'
        elif r=='is not':
            return 'is'
        elif r=='is greater than':
            return 'is less than or equal to'
        elif r=='is less than':
            return 'is greater than or equal to'
        elif r=='is greater than or equal to':
            return 'is less than'
        elif r=='is less than or equal to':
            return 'is greater than'
        else:
            raise(Exception(f"Relation '{r}' is not logical"))
    
    def propagate_taboo_roles(self):
        for table in self.tables['taboo']:
            if len(table) == 1 and table[0].cat in {'PRL', 'PAT'}: # person's role or attribute
                
                self.propagage(Constraint(table[0].category, 
                                     table[0].name,
                                     self.flip_logical_relation(table[0].relation),
                                     table[0].value,
                                     self.similarity_dict
                                    ), table_names=['normal', 'expected'])
                
    def propagage(self, constraint, table_names=[]):
        for table_name in table_names:
            table_list = self.tables[table_name]
            for table in table_list:
                
                table.add_constraint_c(constraint)
                
    def compare(self, other, sim_threshold=0.8):
        
        def similarity_matrix(tables_1, tables_2):
            M = np.zeros((len(tables_1), len(tables_2)))
            for i in range(len(tables_1)):
                for j in range(len(tables_2)):
                    M[i,j] = tables_1[i].compare(tables_2[j], soft=sim_threshold)['jaccard']
                    
            return M
        
        out = {}
        for table_name in self.tables:
            s = self.tables[table_name]
            o = other.tables[table_name]
            if len(s) and len(o):
                M = -similarity_matrix(s, o)
                row_ind, col_ind = linear_sum_assignment(M)
                sim = -M[row_ind, col_ind].mean()
                out[table_name] = sim
            else:
                out[table_name] = 0
                
        out['avg'] = sum([out[table] for table in self.tables]) / len(self.tables)
        
        return out