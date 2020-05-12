import pandas as pd
import json
import lifelines
import re


def _runs_df(n, s):
    """provide the dataframe for calculations based on runs scored"""
    df = pd.read_csv(f'data/batting/{s}/rolling/{n}.csv')
    df = df[['Runs', 'Dismissed']]
    df['Runs'] = df.Runs + 1
    df.dropna(inplace=True)
    df = df.reset_index()
    del df['index']  
    df['Runs'] = df.Runs.astype(float)
    return df


def make_tables(n, s):
    """create fitters based on the appropriate breakpoints and data"""
    df = _runs_df(n, s)
    df.to_csv(f'data/batting/{s}/TE/{n}.csv', index=False)
    time, event = df.Runs, df.Dismissed
    kmf = lifelines.KaplanMeierFitter().fit(time, event)
    kmf.event_table.to_csv(f'data/batting/{s}/eventTable/{n}.csv')
