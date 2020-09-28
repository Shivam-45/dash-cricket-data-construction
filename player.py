"""Download, clean and perform calculations on test match batting data from 
cricinfo statsguru for a given player. Provide the players name as seen on 
their cricinfo profile, and the id found in the url of their profile page"""

import pandas as pd
import numpy as np


class Batsman:
    def __init__(self, name, player_id, match):
        """The batsman's name, cricinfo id, match format are assigned for use."""
        
        self.name = name
        self.player_id = player_id
        self.match = match
        

    def download_df(self):
        """Download the innings table from players cricinfo batting summary page"""
        
        if self.match == 'odi':
            df = pd.read_html(f'http://stats.espncricinfo.com/ci/engine/player/{self.player_id}.html?class=2;template=results;type=batting;view=innings')
        else:
            df = pd.read_html(f'http://stats.espncricinfo.com/ci/engine/player/{self.player_id}.html?class=1;template=results;type=batting;view=innings')
        summary = df[2]
        summary['Name'] = self.name
        summary = summary[['Name', 'Span', 'Mat', 'Inns', 'Runs', 'HS', 'Ave', '50', '100']]
        summary.to_pickle(f'data/batting/{self.match}/summary/{self.name}.pkl')
        df = df[3]
        df.to_pickle(f'data/batting/{self.match}/original/{self.name}.pkl')            
        return df

    
    def _edit_df(self, df):
        """Remove unwanted cols, calculate and append further cols."""
        
        #removing unwanted cols and preparing data
        df = df[['Runs', 'BF', 'Pos', 'Dismissal', 'Opposition', 'Start Date']]
        df['Name'] = self.name
        df.rename(columns={'Start Date':'Date'}, inplace=True)
        df['Date'] = df['Date'].apply(lambda x: x[-4:])
        df['Opposition'] = df['Opposition'].apply(lambda x: x[2:])
        df['Out'] = df['Dismissal'].isin(['lbw', 'caught', 'run out', 'bowled',
                                       'stumped', 'hit wicket', 'obstruct field',
                                       'handled ball', 'retired out']) * 1
        df = df.replace({'Runs': ['absent', '-', 'DNB', 'TDNB', 'sub']}, np.NaN)
        df = df.replace({'BF': ['-']}, 0)
        df['Runs'] = df['Runs'].str.replace(r"*",'')
        df[['Runs', 'BF']] = df[['Runs', 'BF']].apply(pd.to_numeric)        
        df.dropna(inplace=True)
        df = df.reset_index()
        del df['index']
        
        #calculating and adding cols for career average/rolling averages
        df['RunTally'] = df.Runs.cumsum()
        df['DisTally'] = df.Out.cumsum()
        df['Ave'] = round(df['RunTally']/df['DisTally'], 2)
        lengths = [10, 20, 30, 40, 50, 70, 100]
        for length in lengths:
            df[f'rolling{length}'] = round((df['Runs'].rolling(window=length, center=False).sum() /
                                            df['Out'].rolling(window=length, center=False).sum()), 2)
        df = df[['Name', 'Runs', 'Dismissal', 'Pos', 'Opposition', 'Ave', 'RunTally', 
             'DisTally', 'Date', 'Out', 'rolling10', 'rolling20', 'rolling30',
             'rolling40', 'rolling50', 'rolling70', 'rolling100']]       
        return df
    
    
    def get_summary_df(self):
        df = pd.read_pickle(f'data/batting/{self.match}/summary/{self.name}.pkl')
        return df
    
    def create_final_df(self, download=False):
        """Create the final dataframe that will be used by adding columns of rolling averages.
        If download=True, all records will be refreshed from cricinfo.
        If download=False, local files will be searched for and records will only be
        downloaded from cricinfo if the local file is not found.
        """
        
        if download:
            df = self.download_df()
        else:
            try:
                df = pd.read_pickle(f'data/batting/{self.match}/original/{self.name}.pkl')
            except FileNotFoundError:
                df = self.download_df()
        df = self._edit_df(df)
        df.to_csv(f'data/batting/{self.match}/rolling/{self.name}.csv')
        return df
    
player = Batsman('V Kohli', 253802, 'test')
player.get_summary_df()