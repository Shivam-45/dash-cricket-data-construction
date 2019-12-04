"""Gather, format and save data on cricket players from cricinfo statsguru"""

import pandas as pd
import numpy as np
import pygal as pyg


class Batsman:
    """Gather and format data batsman data"""
    def __init__(self, name, player_id, match):
        """take the name, cricinfo id of the batsman and the match format"""
        self.name = name
        self.player_id = player_id
        self.match = match

    def download_df(self):
        """fetch full innings table from players batting summary page"""
        if self.match == 'odi':
            df = pd.read_html(f'http://stats.espncricinfo.com/ci/engine/player/{self.player_id}.html?class=2;template=results;type=batting;view=innings')
        else:
            df = pd.read_html(f'http://stats.espncricinfo.com/ci/engine/player/{self.player_id}.html?class=1;template=results;type=batting;view=innings')
        df = df[3]
        df.to_pickle(f'data/batting/{self.match}/original/{self.name}.pkl')            
        return df

    def _trim_df(self, df):
        """Edit out unwanted columns in the full dataframe"""
        df = df[['Runs', 'BF', 'Pos', 'Dismissal', 'Opposition', 'Start Date']]
        df['Date'] = 0
        for row in range(len(df)):
            df['Date'][row] = df['Start Date'][row][-4:]
            df['Opposition'][row] = df['Opposition'][row][2:]
        return df

    def _runs_per_inns_df(self, df):
        """edit the dataframe to display runs per inning, BF, dismissal status"""
        df['DisType'] = df['Dismissal']
        df = df.replace({'Runs': ['absent', '-', 'DNB', 'TDNB', 'sub']}, np.NaN)
        df = df.replace({'Dismissal': ['lbw', 'caught', 'run out', 'bowled',
                                       'stumped', 'hit wicket', 'obstruct field',
                                       'handled ball', 'retired out']}, 1)
        df = df.replace({'Dismissal': ['not out', 'retired notout']}, 0)
        df = df.replace({'BF': ['-']}, 0)
        df.dropna(inplace=True)
        df = df.reset_index()
        del df['index']
        for row in range(len(df)):
            if not df.Dismissal[row]:
                df.Runs[row] = df.Runs[row][:-1]
            df.Runs[row] = int(df.Runs[row])
            df.BF[row] = int(df.BF[row])
        return df
    
    def _averages_df(self, df):
        """add a column of the players average throughout their career"""
        runs = 0
        dismissal = 0
        df['Name'] = self.name
        df['Tally'] = 0
        df['Dismissed'] = df['Dismissal']
        df['Ave'] = 0.0
        for row in range(len(df)):
            runs += df['Runs'][row]
            dismissal += df['Dismissal'][row]
            df['Tally'][row] = runs
            df['Dismissal'][row] = dismissal
        for row in range(0, len(df)):
            df['Ave'][row] = (df['Tally'][row]/df['Dismissal'][row]
                              if df['Dismissal'][row] else df['Tally'][row])
        df['Ave'] = round(df['Ave'], 2)
        lengths = [10, 20, 30, 40, 50, 70, 100]
        for length in lengths:
            df[f'rolling{length}'] = round((df['Runs'].rolling(window=length, center=False).sum() /
                                            df['Dismissed'].rolling(window=length, center=False).sum()), 2)
        return df
    
    def rolling_ave_df(self, download=False):
        """Create the final df with rolling averages"""
        if download:
            df = self.download_df()
        else:
            try:
                df = pd.read_pickle(f'data/batting/{self.match}/original/{self.name}.pkl')
            except FileNotFoundError:
                df = self.download_df()
        df = self._trim_df(df)
        df = self._runs_per_inns_df(df)
        df = self._averages_df(df)
        df = df[['Runs', 'Pos', 'Opposition', 'Dismissed','Date', 'DisType', 'Ave',
                 'rolling10', 'rolling20', 'rolling30', 'rolling40', 'rolling50',
                 'rolling70', 'rolling100', 'Name']]
        df.to_csv(f'data/batting/{self.match}/rolling/{self.name}.csv')
        return df
