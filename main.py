"""Create csv's needed for cricket dashboard"""

import pandas as pd
import json
import re
from id_finder import create_player_dict
from player import Batsman
from survivalFunctions import make_tables
from hazardkde import kernel_density_df


def rolling_df(download=False):
    """create csv's with all average/opposition/dismissal data"""
    with open(f'data/{d}/{s}/ids_names.json') as file:
        i_n = json.load(file)
    master_df = pd.DataFrame(columns=['Runs', 'BF', 'Pos', 'Dismissal', 'Dismissed', 'Opposition', 'Ground',
                                     'Start Date', 'Date', 'DisType', 'Tally', 'Ave', 'rolling10', 'rolling20',
                                     'rolling30', 'rolling40', 'rolling50', 'rolling70', 'rolling100', 'Name']
    )
    for i, n in i_n.items():
        player = Batsman(n, i, 'test')
        df = player.rolling_ave_df(download)
        master_df = master_df.append(df)
    master_df = master_df.replace({'DisType':['retired notout']}, 'not out')
    master_df = master_df.replace({'DisType':['handled ball', 'hit wicket', 'obstruct field', 'retired out']}, 'other')
    master_df.to_csv(f'data/batting/test/rolling/rollingMaster.csv')

def survival_df():
    """edit survival csv's"""
    master_df = pd.DataFrame(columns=['time', 'survival', 'lower','upper'])
    for n in i_n.values():
        df = pd.read_csv(f'data/batting/test/KM/{n}.csv')
        for row in range(len(df)):
            match_regex = re.compile(r'(\d*),')
            df['time interval'][row] = match_regex.findall(df['time interval'][row])[0]
        df.rename(columns={'time interval':'time', 'lower 95% CL':'lower', 'upper 95% CL':'upper'}, inplace=True)
        df['Name'] = n
        df = df[['time', 'survival', 'lower', 'upper', 'Name']]
        master_df = master_df.append(df)
    master_df.to_csv(f'data/batting/test/KM/kmMaster.csv')
    df = pd.read_csv(f'data/batting/test/KM/master.csv')
    for row in range(len(df)):
        match_regex = re.compile(r'(\d*),')
        df['time interval'][row] = match_regex.findall(df['time interval'][row])[0]
    df.rename(columns={'time interval':'time', 'lower 95% CL':'lower', 'upper 95% CL':'upper'}, inplace=True)
    df = df[['time', 'survival', 'lower', 'upper']]
    df.to_csv(f'data/batting/test/KM/kmOverall.csv')


def hazard_df():
    """create csv's with hazard data"""
    master_df = pd.DataFrame(columns=['Name', 'time', 'hazard'])
    for n in i_n.values():
        df = kernel_density_df(n)
        df.to_csv(f'data/batting/test/kernelDensity/{n}.csv')
        master_df = master_df.append(df)
    master_df.to_csv(f'data/batting/test/kernelDensity/hazMaster.csv')
    df = kernel_density_df('master')
    df.to_csv(f'data/batting/test/kernelDensity/hazOverall.csv')


def update_data_step_one():
    """run this function before running create_CI.R"""
    d = 'batting'
    s = 'test'
    with open(f'data/batting/test/ids_names.json') as file:
        i_n = json.load(file)
    create_player_dict(s, d)
    rolling_df()
    for n in i_n.values():
        make_tables(n, s)
    make_tables('master', s)

def update_data_step_one():
    """run this function after running create_CI.R"""
    survival_df()
    hazard_df()


