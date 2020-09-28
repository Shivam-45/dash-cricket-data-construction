"""uses the lifelines package to construct survival and hazard series for batsmen
"""

import pandas as pd
import lifelines
import matplotlib.pyplot as plt
pd.set_option('display.max_rows', 500)


def _runs_df(player_name, style):
    """Provide the dataframe for calculations based on runs scored"""
    df = pd.read_csv(f'data/batting/{style}/rolling/{player_name}.csv')
    df = df[['Runs', 'Out']]
    df['Runs'] = df.Runs + 1
    df.dropna(inplace=True)
    df = df.reset_index()
    del df['index']  
    df['Runs'] = df.Runs.astype(float)
    return df


def make_tables(player_name, style):
    """Create an event table of the batsman's innings"""
    df = _runs_df(player_name, style)
    time, event = df.Runs, df.Out
    kmf = lifelines.KaplanMeierFitter().fit(time, event)
    kmf.event_table['Name'] = player_name
    kmf.event_table.to_csv(f'data/batting/{style}/eventTable/{player_name}.csv')


def smooth_hazard(name,window=19):
    df = pd.read_csv(f'data/batting/test/eventTable/{name}.csv')
    df['hazard'] = df['observed']/df['at_risk']
    df['event_at'] = df['event_at'].astype(int)
    new_index = range(int(df['event_at'].max()))
    df = df.set_index('event_at')
    df = df.reindex(new_index, fill_value=0)
    df=df[1:]
    dfrev = df[window-1:0:-1]
    df = dfrev.append(df)
    df['Smooth Haz'] = df['hazard'].rolling(window=window, center=True).mean()
    df['Smooth2 Haz'] = df['Smooth Haz'].rolling(window=window, center=True).mean()
    df['Name'] = name
    df=df[window-1:window+120]
    return df