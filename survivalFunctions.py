Survival Model of Batsmen
check if pos is relevant 
"""
import pandas as pd
import json
import matplotlib.pyplot as plt
import lifelines
import re
from player import Batsman

pd.options.mode.chained_assignment = None
pd.set_option('display.max_rows', 400)
pd.set_option('display.max_columns', 12)
pd.set_option('display.width', 140)

def update_full():
    df = pd.DataFrame(columns=['Runs', 'BF', 'Pos', 'Dismissal', 'Opposition', 'Ground', 'Start Date', 'Date'])
    with open(f'{d}/{s}/ids_names.json') as file:
        i_n = json.load(file)
    for i, n in i_n.items():
        a = Batsman(n, i, s)
        a_df = a.load_runs_per_inns_df()
        print(a_df.columns)
        df = df.append(a_df, ignore_index=True)
    print(df)
    df.to_pickle(f'{d}/{s}/dataframes/formBased/full.pkl')

def load(s, n):
    """load dataframe of all player innings combined"""
    return pd.read_csv(f'data/batting/test/rollingAve/{n}.csv')

def runs(n, i, s):
    """provide the dataframe for calculations based on runs scored"""
    if n in ['master', 'openers', 'middle']:
        df = load(s, n)        
    else:
        player = Batsman(n, i, s)
        df = player.rolling_ave_df()
    df = df[['Runs', 'Dismissed']]
    df['Runs'] = df.Runs
    df.dropna(inplace=True)
    df = df.reset_index()
    del df['index']  
    df['Runs'] = df.Runs.astype(float)
    df.to_csv(f'data/batting/test/TE/{n}.csv', index=False)
    return df
                
def make_fitters(n, i, s):
    """create fitters based on the appropriate breakpoints and data"""
    df = runs(n, i, s)
    T, E = df.Runs, df.Dismissed
    breaks=[21,51,101]
# =============================================================================
#     kmf = lifelines.KaplanMeierFitter().fit(T, E)
#     pf = lifelines.PiecewiseExponentialFitter(breakpoints=breaks).fit(T, E)
# =============================================================================
    naf = lifelines.NelsonAalenFitter().fit(T, E)
# =============================================================================
#     kmf.event_table.to_csv(f'data/batting/{s}/eventTable/{n}.csv')
#     kmf.survival_function_.to_csv(f'data/batting/{s}/KMF/{n}.csv')
# =============================================================================
    return naf
    
def partial_player(n, i, s):
    """add players lines to graph for comparison purposes"""
    naf = make_fitters(n, i, s)
    
# =============================================================================
#     plt.figure(1)
#     ax = plt.gca()
#     pf.plot_hazard(ax=ax, label=f'{n}, {s} PF', ci_show=False)
#     ax.set_title(f'Hazard')
#     
#     plt.figure(2)
#     ax = plt.gca()
#     kmf.plot(ax=ax, label=f'{n}, {s} KMF', ci_show=False)
#     plt.title(f'Survival Function')
#     plt.ylim(0, 1)
#     plt.legend()
#     
# =============================================================================
    plt.figure(1)
    ax = plt.gca()
    naf.plot_hazard(bandwidth=10, ax=ax, ci_show=False)
    
def compare_players(*args, s='test'):
    """master function to compare an arbitrary number of players"""
    with open(f'data/batting/{s}/ids_names.json') as file:
        ids_names = json.load(file)
    names_ids = {y:x for x,y in ids_names.items()}
    for n in args:
        if n in  ['master', 'openers', 'middle']:
            i = 0
        else:
            i = names_ids[n]
        partial_player(n, i, s)
    
d = 'batting'
s='test'

with open(f'data/batting/test/ids_names.json') as file:
    i_n = json.load(file)
    
# =============================================================================
# master_df = pd.DataFrame(columns=['time', 'survival', 'lower','upper'])
# for i, n in i_n.items():
#     df = pd.read_csv(f'data/batting/test/KMF/{n}.csv')
#     try:
#         for row in range(len(df)):
#             match_regex = re.compile(r'(\d*),')
#             df['time interval'][row] = match_regex.findall(df['time interval'][row])[0]
#         df.rename(columns={'time interval':'time', 'lower 95% CL':'lower','upper 95% CL':'upper'},inplace=True)
#     except:
#         pass
#     df['Name'] = n
#     df = df[['time', 'survival', 'lower', 'upper', 'Name']]
#     print(df)
#     master_df = master_df.append(df)
#     df.to_csv(f'data/batting/test/KMF/{n}.csv')
# =============================================================================

# =============================================================================
# df = pd.read_csv(f'data/batting/test/KMF/overall.csv')
# try:
#     for row in range(len(df)):
#         match_regex = re.compile(r'(\d*),')
#         df['time interval'][row] = match_regex.findall(df['time interval'][row])[0]
#     df.rename(columns={'time interval':'time', 'lower 95% CL':'lower','upper 95% CL':'upper'},inplace=True)
# except:
#     pass
# df = df[['time', 'survival', 'lower', 'upper']]
# df.to_csv(f'data/batting/test/KMF/overall.csv')
# =============================================================================

compare_players('master')