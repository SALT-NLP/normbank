import argparse, json, math, os, random
import pandas as pd
import numpy as np
from glob import glob
from tqdm import tqdm
from constraints_emb import *
from collections import defaultdict, Counter
from sklearn.model_selection import train_test_split

LABEL_MAPPING = {'expected': 2,
                 'normal': 1,
                 'taboo': 0}

def add_split_col_and_shuffle(df, no_bleeding, train_frac=0.8, dev_frac=0.1, random_state=0):
    train, dev, test = train_dev_test(df, no_bleeding, train_frac, dev_frac)
    train['split'] = 'train'
    dev['split'] = 'dev'
    test['split'] = 'test'
    return pd.concat([train,dev,test]).sample(frac=1, random_state=random_state)

def train_dev_test(df, no_bleeding, train_frac=0.8, dev_frac=0.1):
    assert 1-train_frac-dev_frac > 0
    train, test = split(df, frac=train_frac, no_bleeding=no_bleeding)
    dev, test = split(test, frac=(dev_frac/(1-train_frac)), no_bleeding=no_bleeding)
    return train, dev, test
    
def split(df, frac=0.8, no_bleeding=''):
    if not (len(no_bleeding) and no_bleeding in df):
        print('fix no_bleeding', no_bleeding)
        
    pool = set(df[no_bleeding].values)
    train_pool = set(random.sample(sorted(list(pool)), k=int(len(pool)*frac)))
    test_pool = pool.difference(train_pool)
   
    filt = lambda s : df[[val in s for val in df[no_bleeding].values]].copy()    
    return filt(train_pool), filt(test_pool)

def manual_pre_data_filtering(df):
    block_list = {'A2RBF3IIJP15IH', 'A39SK1E6IMQBD5'}
    df = df[[wid not in block_list for wid in df['WorkerId'].values]].copy()
    return df

def manual_post_data_filtering(df):
    df = df[["[PERSON]'s condition or state is 'alive'" not in c for c in df['constraints'].values]].copy()
    return df
                
def compile_scene(train_size, dev_size, seed, extended_file=False):    
    random.seed(seed)
    np.random.seed(seed)
    
    df = pd.concat([pd.read_csv(fn, low_memory=False) for fn in glob('../hit/output/Full*.csv')])
    df = df[df['AssignmentStatus']!='Rejected'].copy()
    df = manual_pre_data_filtering(df)

    out_dict = {}
    response_dict = defaultdict(list)
    i=0
    for _, row in df.sample(frac=1, random_state=seed).iterrows():
        CS = ConstraintSet()
        try:
            CS.from_mturk(row)
            for norm_level in CS.tables.keys():
                table_set = CS.tables[norm_level]
                for table in table_set:
                    shuffled_constraints = table.shuffled_constraints()
                    d = {
                        "setting": row['Input.setting'],
                        "behavior": row['Input.behavior'],
                        "setting-behavior": f"{row['Input.setting']} [BEHAVIOR] {row['Input.behavior']}",
                        "constraints": str(table),
                        "constraints_given": ' [AND] '.join([str(C) for C in shuffled_constraints[:-1]]) + ' [AND] ',
                        "constraint_predict": str(shuffled_constraints[-1]),
                        "norm": norm_level,
                        "label": LABEL_MAPPING[norm_level]
                    }
                    if extended_file:
                        d['worker_id'] = CS.worker_id
                        d['submit_time'] = CS.metadata['SubmitTime']
                        d['string_length'] = len(str(table))
                        d['num_constraints'] = len(table)

                        for level in ['category', 'name', 'relation', 'value']:
                            d[f'preset_{level}'] = 0

                        for constraint in table:
                            for level in ['category', 'name', 'relation', 'value']:
                                if constraint.is_preset(level):
                                    d[f'preset_{level}'] += 1
                                    
                        stat = Counter([c.category for c in table.constraints])
                        for key in stat:
                            d[key] = stat[key]
                                    
                        d['dummy'] = 1
                    
                    out_dict[i] = d
                    i+=1
                    #response_dict[d['setting-behavior']].append(d['constraints'])
        except Exception as e:
            print(e)

    out_df = pd.DataFrame.from_dict(out_dict, orient='index')
    out_df = manual_post_data_filtering(out_df)
    out_df = add_split_col_and_shuffle(out_df, no_bleeding='setting-behavior', train_frac=train_size, dev_frac=dev_size)
    return out_df

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=str, default='SCENE_extended.csv')
    parser.add_argument('--seed', type=int, default=7)
    parser.add_argument('--train_size', type=int, default=0.8)
    parser.add_argument('--dev_size', type=int, default=0.1)
    args = parser.parse_args()
    
    out_df = compile_scene(args.train_size, args.dev_size, args.seed, extended_file=True)
    
    if args.output:
        out_df.to_csv(args.output, index=False)
        
    print('There are', len(set(out_df['setting-behavior'].values)), 'unique setting/behavior pairs')
    print('There are', len(set(out_df['constraints'])), 'unique constraints')