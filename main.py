"""Create csv's needed for https://burningtin-cricket.herokuapp.com/ cricket dashboard"""

import pandas as pd
import json
from id_finder import create_player_dict
from player import Batsman
from survival import make_tables, smooth_hazard
from bpcpy import bpcp

pd.options.mode.chained_assignment = None


def _rolling_df(i_n, download=False):
    """create csv's with all average/opposition/dismissal data"""
    master_df = pd.DataFrame(columns=[
        'Name', 'Runs', 'DisTally', 'RunTally', 'Dismissal', 'Opposition', 'Date', 'Pos',
        'Out', 'Ave', 'rolling10', 'rolling20', 'rolling30',
        'rolling40', 'rolling50', 'rolling70', 'rolling100'
        ]
    )
    summary_master_df = pd.DataFrame(columns=[
        'Name', 'Span', 'Mat', 'Inns', 'Runs', 'HS', 'Ave', '50', '100'
        ]
    )
    for i, n in i_n.items():
        player = Batsman(n, i, 'test')
        df = player.create_final_df(download)
        master_df = master_df.append(df)
        summary_df = player.get_summary_df()
        summary_master_df = summary_master_df.append(summary_df)
    master_df = master_df.replace({'Dismissal': ['retired notout']}, 'not out')
    master_df = master_df.replace({'Dismissal': ['handled ball', 'hit wicket', 'obstruct field', 'retired out']}, 'other')
    master_df.to_csv('data/batting/test/final/rollingMaster.csv')
    summary_master_df.to_csv('data/batting/test/final/summaryMaster.csv')


def _create_cl(i_n, s):
    """calculate 95% confidence limits for the survival data using the bpcp"""
    for n in i_n.values():
        make_tables(n, s)
        event_table = pd.read_csv(f'data/batting/test/eventTable/{n}.csv')
        event_table.drop(event_table.head(1).index, inplace=True)
        results = bpcp(event_table)
        results.to_csv(f'data/batting/test/KMPy/{n}.csv')
    make_tables('master', s)
    event_table = pd.read_csv('data/batting/test/eventTable/master.csv')
    event_table.drop(event_table.head(1).index, inplace=True)
    results = bpcp(event_table)
    results.to_csv('data/batting/test/KMPy/overall.csv')


def _survival_df(i_n):
    """format survival data for use in Survival Curve graph"""
    master_df = pd.DataFrame(columns=['time', 'survival', 'lower', 'upper'])
    for n in i_n.values():
        df = pd.read_csv(f'data/batting/test/KMPy/{n}.csv')
        df['Name'] = n
        df = df[['time', 'survival', 'lower', 'upper', 'Name']]
        master_df = master_df.append(df)
    master_df.to_csv('data/batting/test/final/kmMaster.csv')
    df = pd.read_csv('data/batting/test/KMPy/overall.csv')
    df = df[['time', 'survival', 'lower', 'upper']]
    df.to_csv('data/batting/test/final/kmOverall.csv')


def _hazard_df(i_n):
    """calculate hazard data for use in Hazard Rate graph"""
    master_df = pd.DataFrame(columns=['Name', 'time', 'hazard'])
    for n in i_n.values():
        df = smooth_hazard(n)
        df.to_csv(f'data/batting/test/kernelDensity/{n}.csv')
        master_df = master_df.append(df)
    master_df.to_csv('data/batting/test/final/hazMaster.csv')
    df = smooth_hazard('master')
    df.to_csv('data/batting/test/final/hazOverall.csv')


def update_data(download=False):
    """run this function with download=True to update data
    running with download=False will recreate output csv's with the existing data"""
    d = 'batting'
    s = 'test'
    with open('data/batting/test/ids_names.json') as file:
        i_n = json.load(file)
    create_player_dict(s, d)
    _rolling_df(i_n, download)
    _create_cl(i_n, s)
    _survival_df(i_n)
    _hazard_df(i_n)

if __name__ == '__main__':
    update_data()