"""Perform actions and generate results on the players data"""

import pandas as pd
from player import Batsman
from player import Bowler
import json

pd.options.mode.chained_assignment = None
pd.set_option('display.max_rows', 250)
pd.set_option('display.max_columns', 12)
pd.set_option('display.width', 140)

def construct_rolling_table_base(data, match, bat_or_bowl, length):
    stats = []
    if bat_or_bowl == 'batting':
        for ids, names in data.items():
            person = Batsman(names, ids, match)
            stats.append(person.rolling_comparison_first(length))
    if bat_or_bowl == 'bowling':
        for ids, names in data.items():
            person = Bowler(names, ids, match)
            stats.append(person.rolling_comparison_first(length))
    df = pd.DataFrame(stats)
    df.sort_values(f'Career', axis=0, ascending=False, inplace=True, kind='quicksort', na_position='last')
    df.to_pickle(f'{bat_or_bowl}/{match}/tables/rollingAves/byDismissal/overall.pkl')
    return df

def add_to_rolling_table(data, match, bat_or_bowl, length):
    stats = []
    if bat_or_bowl == 'batting':
        for ids, names in data.items():
            person = Batsman(names, ids, match)
            stats.append(person.rolling_comparison_subsequent(length))
    if bat_or_bowl == 'bowling':
        for ids, names in data.items():
            person = Bowler(names, ids, match)
            stats.append(person.rolling_comparison_subsequent(length))
    df = pd.read_pickle(f'{bat_or_bowl}/{match}/tables/rollingAves/byDismissal/overall.pkl')
    df[f'{length} Max'] = stats
    df.to_pickle(f'{bat_or_bowl}/{match}/tables/rollingAves/byDismissal/overall.pkl')
    return df

def load_rolling_table(match, bat_or_bowl):
    df = pd.read_pickle(f'{bat_or_bowl}/{match}/tables/rollingAves/byDismissal/overall.pkl')
    return df

def construct_split_table(data, match, bat_or_bowl):
    stats = []
    if bat_or_bowl == 'batting':
        for ids, names in data.items():
            person = Batsman(names, ids, match)
            stats.append(person.split_comparison())
    if bat_or_bowl == 'bowling':
        for ids, names in data.items():
            person = Bowler(names, ids, match)
            stats.append(person.split_comparison())
    df = pd.DataFrame(stats)
    df.sort_values(f'Split Max', axis=0, ascending=False, inplace=True, kind='quicksort', na_position='last')
    df.to_pickle(f'{bat_or_bowl}/{match}/tables/splitAves/Split Max.pkl')
    return df

def load_split_table(match, bat_or_bowl, mini=False):
    df = pd.read_pickle(f'{bat_or_bowl}/{match}/tables/splitAves/Split Max.pkl')
    if mini:
        df.sort_values(f'Split Min', axis=0, ascending=True, inplace=True, kind='quicksort', na_position='last')
        df = df[['Name', 'Split Min']]
    else:
        df = df[['Name', 'Split Max']]
    return df

def update_master_df():
    with open(f'data/{d}/{s}/ids_names.json') as file:
        i_n = json.load(file)
    master_df= pd.DataFrame(columns=['Runs', 'BF' ,'Pos', 'Dismissal', 'Dismissed','Opposition',
                 'Ground' ,'Start Date', 'Date', 'DisType', 'Tally', 'Ave' ,'rolling10',
                 'rolling20', 'rolling30', 'rolling40' ,'rolling50' ,'rolling70', 'rolling100',
                 'Name'])
    
    for i, n in i_n.items():
        player = Batsman(n, i, 'test')
        df = player.rolling_ave_df()
        df = df[['Runs', 'BF' ,'Pos', 'Dismissal' ,'Opposition', 'Dismissed',
                 'Ground' ,'Start Date', 'Date', 'DisType', 'Tally', 'Ave' ,'rolling10',
                 'rolling20', 'rolling30', 'rolling40' ,'rolling50' ,'rolling70', 'rolling100',
                 'Name']]
        df.to_csv(f'data/batting/test/rollingAve/{n}.csv')
        master_df = master_df.append(df)
    
    master_df.to_csv(f'data/batting/test/rollingAve/masterUnedited.csv')
    master_df = master_df.replace({'DisType':['retired notout']}, 'not out')
    master_df = master_df.replace({'DisType':['handled ball', 'hit wicket', 'obstruct field', 'retired out']}, 'other')
    master_df.to_csv(f'data/batting/test/rollingAve/master.csv')


d = 'batting'

s = 'test'




