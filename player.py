"""Gather, format and save data on cricket players from cricinfo statsguru"""

import pandas as pd
import numpy as np
import pygal as pyg

class Batsman:
    """Gather and format data on a batsman in all ways required"""
    def __init__(self, name, player_id, match):
        """take the name, cricinfo id of the batsman and the match format"""
        self.name = name
        self.player_id = player_id
        self.match = match

    def full_df(self, create=False):
        """fetch full innings table from players batting summary page"""
        if not create:
            try:
                df = pd.read_pickle(f'data/batting/{self.match}/original/{self.name}.pkl')
                return df
            except FileNotFoundError:
                pass
        if self.match == 'odi':
            df = pd.read_html(f'http://stats.espncricinfo.com/ci/engine/player/{self.player_id}.html?class=2;template=results;type=batting;view=innings')
        if self.match == 'test':
            df = pd.read_html(f'http://stats.espncricinfo.com/ci/engine/player/{self.player_id}.html?class=1;template=results;type=batting;view=innings')
        df = df[3]
        df.to_pickle(f'data/batting/{self.match}/original/{self.name}.pkl')            
        return df

    def edited_df(self, create=False):
        """Edit out unwanted columns in the full dataframe"""
        if not create:
            try:
                df = pd.read_pickle(f'data/batting/{self.match}/edited/{self.name}.pkl')
                return df
            except FileNotFoundError:
                pass
        df = self.full_df()
        df = df[['Runs', 'BF', 'Pos', 'Dismissal', 'Opposition', 'Ground', 'Start Date']]
        df['Date'] = 0
        for row in range(len(df)):
            df['Date'][row] = df['Start Date'][row][-4:]
        df.to_pickle(f'data/batting/{self.match}/edited/{self.name}.pkl')
        return df

    def runs_per_inns_df(self, create=False):
        """edit the dataframe to display runs per inning, BF, dismissal status"""
        if not create:
            try:
                df = pd.read_pickle(f'data/batting/{self.match}/runsPerInns/{self.name}.pkl')
                return df
            except FileNotFoundError:
                pass
        df = self.edited_df(True)
        df = pd.read_pickle(f'data/batting/{self.match}/edited/{self.name}.pkl')
        df['DisType'] = df['Dismissal']
        df = df.replace({'Runs':['absent', '-', 'DNB', 'TDNB', 'sub']}, np.NaN)
        df = df.replace({'Dismissal':['lbw', 'caught', 'run out', 'bowled',
                                      'stumped', 'hit wicket', 'obstruct field',
                                      'handled ball', 'retired out']}, 1)
        df = df.replace({'Dismissal':['not out', 'retired notout']}, 0)
        df = df.replace({'BF': ['-']}, 0)
        df.dropna(inplace=True)
        df = df.reset_index()
        del df['index']
        for row in range(len(df)):
            if not df.Dismissal[row]:
                df.Runs[row] = df.Runs[row][:-1]
            df.Runs[row] = int(df.Runs[row])
            df.BF[row] = int(df.BF[row])
        df.to_pickle(f'data/batting/{self.match}/runsPerInns/{self.name}.pkl')
        return df

    def runs_per_dis_df(self, create=False):
        """edit the dataframe to display runs, BF per dismissal"""
        if not create:
            try:
                df = pd.read_pickle(f'data/batting/{self.match}/runsPerDis/{self.name}.pkl')
                return df
            except FileNotFoundError:
                pass
        self.runs_per_inns_df(True)
        for row in range(len(df)-1):
            if not df.Dismissal[row]:
                df.Runs[row+1] += df.Runs[row]
                df.Runs[row] = np.NaN
                df.BF[row+1] += df.BF[row]
                df.BF[row] = np.NaN
        df.to_pickle(f'data/batting/{self.match}/runsPerDis/{self.name}.pkl')
        return df
    
    def career_ave_df(self, create=False):
        """add a column of the players average throughout their career"""
        if not create:
            try:
                df = pd.read_pickle(f'data/batting/{self.match}/careerAve/{self.name}.pkl')
                return df
            except FileNotFoundError:
                pass
        df = self.runs_per_inns_df()
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
        df.to_pickle(f'data/batting/{self.match}/careerAve/{self.name}.pkl')
        return df
    
    def rolling_ave_df(self, create=False):
        """Create rolling average chart based on runs_per_inns_df"""
        if not create:
            try:
                df = pd.read_csv(f'data/batting/{self.match}/rollingAve/{self.name}.csv')
                return df
            except FileNotFoundError:
                pass
        df = self.career_ave_df(True)
        lengths = [10,20,30,40,50,70,100]
        for length in lengths:
            df[f'rolling{length}'] = (df['Runs'].rolling(window=length, center=False).sum()/
                              df['Dismissed'].rolling(window=length, center=False).sum())
        df.to_csv(f'data/batting/{self.match}/rollingAve/{self.name}.csv')
        return df

class Bowler:
    """Gather and format data on a bowler in all ways required"""
    def __init__(self, name, player_id, match):
        """take the name, cricinfo id of the bowler and the match format"""
        self.name = name
        self.player_id = player_id
        self.match = match

    def grab_full_df(self):
        """fetch dataframe from players odi bowling summary page
        Only run once per player per format to avoid repeated requests"""
        if self.match == 'odi':
            df = pd.read_html(f'http://stats.espncricinfo.com/ci/engine/player/{self.player_id}.html?class=2;template=results;type=bowling;view=innings')
        if self.match == 'test':
            df = pd.read_html(f'http://stats.espncricinfo.com/ci/engine/player/{self.player_id}.html?class=1;template=results;type=bowling;view=innings')
        df = df[3]
        df.to_pickle(f'bowling/{self.match}/original/{self.name}.pkl')
        return df

    def load_full_df(self):
        """load the original dataframe"""
        df = pd.read_pickle(f'bowling/{self.match}/original/{self.name}.pkl')
        return df

    def edited_df(self):
        """Edit the full downloaded dataframe"""
        df = pd.read_pickle(f'bowling/{self.match}/original/{self.name}.pkl')
        df = df[['Overs', 'Runs', 'Wkts', 'Opposition', 'Ground', 'Start Date']]
        df = df.replace({'Overs':['DNB', 'TDNB', 'sub']}, np.NaN)
        df.dropna(inplace=True)
        df = df.reset_index()
        del df['index']
        df[['Overs', 'Wkts', 'Runs']] = df[['Overs', 'Wkts', 'Runs']].apply(pd.to_numeric)
        df['Date'] = 0
        df['Balls'] = (df['Overs']*10)//10 * 6 + (df['Overs']*10)%10
        for row in range(len(df)):
            df['Date'][row] = df['Start Date'][row][-8:]
        df.to_pickle(f'bowling/{self.match}/edited/{self.name}.pkl')
        return df

    def load_edited_df(self):
        """load the edited dataframe"""
        df = pd.read_pickle(f'bowling/{self.match}/edited/{self.name}.pkl')
        return df

    def tally_df(self):
        """edit the dataframe to display wickets, runs and balls per innings with tally"""
        df = pd.read_pickle(f'bowling/{self.match}/edited/{self.name}.pkl')
        df = df[['Runs', 'Wkts', 'Date', 'Balls']]
        runs_tally = 0
        wickets_tally = 0
        balls_tally = 0
        df['TallyR'] = 0
        df['TallyW'] = 0
        df['TallyB'] = 0
        df['TallyO'] = 0.0
        for row in range(len(df)):
            runs_tally += df['Runs'][row]
            wickets_tally += df['Wkts'][row]
            balls_tally += df['Balls'][row]
            df['TallyR'][row] = runs_tally
            df['TallyW'][row] = wickets_tally
            df['TallyB'][row] = balls_tally
            df['TallyO'][row] = df['TallyB'][row]//6+(df['TallyB'][row]%6)/10
        df.to_pickle(f'bowling/{self.match}/tally/{self.name}.pkl')
        return df

    def load_tally_df(self):
        """load the tally dataframe"""
        df = pd.read_pickle(f'bowling/{self.match}/tally/{self.name}.pkl')
        return df

    def split_aves_df(self):
        """find the past and future average throughout career"""
        df = pd.read_pickle(f'bowling/{self.match}/tally/{self.name}.pkl')
        df['Pre'] = 0.0
        df['Post'] = 0.0
        df.Post[0] = df.TallyR[len(df)-1]/df.TallyW[len(df)-1]
        for row in range(1, len(df)):
            df['Pre'][row] = (df['TallyR'][row-1]/df['TallyW'][row-1]
                              if df['TallyW'][row-1] else df['TallyR'][row-1])
            df['Post'][row] = ((df['TallyR'][len(df)-1]-df['TallyR'][row-1])/
                               (df['TallyW'][len(df)-1]-df['TallyW'][row-1])
                               if (df['TallyW'][len(df)-1]-df['TallyW'][row-1])
                               else (df['TallyR'][len(df)-1]-df['TallyR'][row-1]))
        df['Post'] = round(df['Post'], 2)
        df['Pre'] = round(df['Pre'], 2)
        df['Split'] = df['Pre']-df['Post']
        df.to_pickle(f'bowling/{self.match}/splitAves/{self.name}.pkl')
        return df

    def load_split_aves_df(self):
        """load the split aves dataframe"""
        df = pd.read_pickle(f'bowling/{self.match}/splitAves/{self.name}.pkl')
        return df

    def split_aves_chart_png(self):
        """Create png chart based on the split aves dataframe"""
        df = pd.read_pickle(f'bowling/{self.match}/splitAves/{self.name}.pkl')
        df = df.reset_index()
        del df['index']

        x_axis = {'l':[], 'v':[]}
        x_axis['l'].append(str(df.Date[1][-4:]))
        x_axis['v'].append(0)
        for row in range(1, len(df)):
            if df.Date[row][-4:] != df.Date[row-1][-4:] and df.Date[row][-4:] not in x_axis['l']:
                x_axis['l'].append(str(df.Date[row][-4:]))
                x_axis['v'].append(int(row))
            else:
                x_axis['l'].append('0')

        post_values_labels = [{'value':df.Post[0], 'label':f'{df.TallyW[len(df)-1]} wickets in {len(df)} innings ({df.TallyO[len(df)-1]} overs)'}]
        pre_values_labels = [{'value':df.Pre[0], 'label':f'0 wickets over 0 innings'}]
        for i in range(1, len(df)):
            overs = ((df.TallyB[len(df)-1]-df.TallyB[i-1])*10)//10 + ((df.TallyB[len(df)-1]-df.TallyB[i-1])*10)%10
            post_values_labels.append({'value':df.Post[i], 'label':f'{df.TallyW[len(df)-1]-df.TallyW[i-1]} wickets in {len(df)-i} innings ({overs} overs)'})
            pre_values_labels.append({'value':df.Pre[i], 'label':f'{df.TallyW[i-1]} wickets in {i} innings ({df.TallyO[i-1]} overs)'})

        valid = [0]
        first_check = df.index[df['TallyW'] >= 45].tolist()
        second_check = df.index[df.TallyW.max()-df['TallyW'] >= 45].tolist()
        all_checks = [i for i in first_check if i in second_check]
        desired_range_max = max((max(df.Pre.max(), df.Post.max())//10+1)*10, 60)
        for i in range(1, len(df)-1):
            if i in all_checks:
                valid.append(desired_range_max)
            else:
                valid.append(0)
        valid.append(0)

        chart = pyg.Line(legend_at_bottom=True, show_y_guides=True,
                         show_x_guides=False, legend_at_bottom_columns=4, x_label_rotation=45,
                         show_minor_x_labels=False, show_minor_y_labels=True, width=1600,
                         height=900, zero=desired_range_max,
                         style=pyg.style.Style(legend_font_size=20,
                                               label_font_size=16,
                                               major_label_font_size=16,
                                               title_font_size=26, opacity=0.3,
                                               colors=('red', 'blue', 'green', '#a3a3a3')))
        if self.match == 'test':
            chart.title = f'{self.name}: Future and Past Averages in Test Matches'
        if self.match == 'odi':
            chart.title = f'{self.name}: Future and Past Averages in ODIs'
        chart.x_labels = x_axis['l']
        chart.x_labels_major = [x_axis['l'][i] for i in x_axis['v']]
        chart.add('Future Average', post_values_labels, show_only_major_dots=True)
        chart.add('Past Average', pre_values_labels, show_only_major_dots=True)
        chart.add('Career Average', [df.Post[0]]*(len(df)), show_dots=False)
        chart.add('PA or FA on < 45 Wkts', valid, show_dots=False, fill=True, allow_interruptions=True)
        chart.render_to_png(filename=f'bowling/{self.match}/graphs/splitAvesPNG/{self.name}.png')

    def split_aves_chart_svg(self):
        """Create svg chart based on the split aves dataframe"""
        df = pd.read_pickle(f'bowling/{self.match}/splitAves/{self.name}.pkl')
        mean_line = [df.Post[0]]*(len(df))
        df = df.reset_index()
        del df['index']

        x_axis = {'l':[], 'v':[]}
        x_axis['l'].append(str(df.Date[1][-4:]))
        x_axis['v'].append(0)
        for row in range(1, len(df)):
            if df.Date[row][-4:] != df.Date[row-1][-4:] and df.Date[row][-4:] not in x_axis['l']:
                x_axis['l'].append(str(df.Date[row][-4:]))
                x_axis['v'].append(int(row))
            else:
                x_axis['l'].append('0')

        post_values_labels = [{'value':df.Post[0], 'label':f'{df.TallyW[len(df)-1]} wickets in {len(df)} innings ({df.TallyO[len(df)-1]} overs)'}]
        pre_values_labels = [{'value':df.Pre[0], 'label':f'0 wickets over 0 innings'}]
        for i in range(1, len(df)):
            overs = (df.TallyB[len(df)-1]-df.TallyB[i-1])//6 + ((df.TallyB[len(df)-1]-df.TallyB[i-1])%6)/10
            post_values_labels.append({'value':df.Post[i], 'label':f'{df.TallyW[len(df)-1]-df.TallyW[i-1]} wickets in {len(df)-i} innings ({overs} overs)'})
            pre_values_labels.append({'value':df.Pre[i], 'label':f'{df.TallyW[i-1]} wickets in {i} innings ({df.TallyO[i-1]} overs)'})

        desired_range_max = max((max(df.Pre.max(), df.Post.max())//10+1)*10, 60)
        chart = pyg.Line(legend_at_bottom=True, show_y_guides=True,
                         show_x_guides=False, x_label_rotation=45,
                         show_minor_x_labels=False, show_minor_y_labels=True,
                         tooltip_border_radius=10, zero=desired_range_max,
                         style=pyg.style.Style(colors=('red', 'blue', 'green', '#a3a3a3')))
        if self.match == 'test':
            chart.title = f'{self.name}: Future and Past Averages in Test Matches'
        if self.match == 'odi':
            chart.title = f'{self.name}: Future and Past Averages in ODIs'
        chart.x_labels = x_axis['l']
        chart.x_labels_major = [x_axis['l'][i] for i in x_axis['v']]
        chart.add('Future Average', post_values_labels, show_only_major_dots=True)
        chart.add('Past Average', pre_values_labels, show_only_major_dots=True)
        chart.add('Career Average', mean_line, show_dots=False)
        chart.render_to_file(f'bowling/{self.match}/graphs/splitAvesSVG/{self.name}.svg')

    def rolling_chart_dis(self, length):
        """Create rolling average chart based on runs_per_dis_df"""
        df = pd.read_pickle(f'bowling/{self.match}/runsPerDis/{self.name}.pkl')
        rolling = df['Runs'].rolling(window=length, center=False).mean()
        rolling.dropna(inplace=True)
        mean_line = [df['Runs'].mean()]*(len(df) + 1 - length)
        chart = pyg.Line()
        if self.match == 'test':
            chart.title = f'{self.name}: {length} Dismissal Rolling Average in Test Matches'
        if self.match == 'odi':
            chart.title = f'{self.name}: {length} Dismissal Rolling Average in ODIs'
        chart.add('Rolling Average', rolling)
        chart.add('Overall Average', mean_line, show_dots=False, stroke_style={'width': 3})
        chart.render_to_file(f'bowling/{self.match}/graphs/rollingAves/byDismissal/{length}/{self.name}.svg')

    def rolling_chart_inns(self, length):
        """Create rolling average chart based on runs_per_inns_df"""
        df = pd.read_pickle(f'bowling/{self.match}/runsPerInns/{self.name}.pkl')
        rolling = (df['Runs'].rolling(window=length, center=False).sum()/
                   df['Dismissal'].rolling(window=length, center=False).sum())
        df = df.iloc[length:]
        rolling.dropna(inplace=True)
        mean_line = [df['Runs'].sum()/df['Dismissal'].sum()]*(len(df) + 1 - length)
        chart = pyg.Line()
        if self.match == 'test':
            chart.title = f'{self.name}: {length} Innings Rolling Average in Test Matches'
        if self.match == 'odi':
            chart.title = f'{self.name}: {length} Innings Rolling Average in ODIs'
        chart.add('Rolling Average', rolling, label=df['Date'])
        chart.add('Overall Average', mean_line, show_dots=False, stroke_style={'width': 3})
        chart.render_to_file(f'bowling/{self.match}/graphs/rollingAves/byInnings/{length}/{self.name}B.svg')

    def rolling_comparison(self, length):
        """Create df to compare players by rolling average metrics"""
        df = pd.read_pickle(f'bowling/{self.match}/runsPerDis/{self.name}.pkl')
        rolling = df['Runs'].rolling(window=length, center=False).mean()
        rolling.dropna(inplace=True)
        individual = {'Name':self.name, 'Ave':df['Runs'].mean(),
                      f'{length}Max':rolling.max(), f'{length}Min':rolling.min(),
                      f'{length}Dif':rolling.max()-rolling.min()}
        return individual

    def split_comparison(self):
        """create df comparing players based on split average max and min"""
        df = pd.read_pickle(f'bowling/{self.match}/splitAves/{self.name}.pkl')
        first_check = df.index[df['TallyW'] >= 45].tolist()
        second_check = df.index[df.TallyW.max()-df['TallyW'] >= 45].tolist()
        both = [i for i in first_check if i in second_check]
        if both:
            df.drop(df.tail(-both[-1]).index, inplace=True)
            df.drop(df.head(both[0]).index, inplace=True)
            individual = {'Name':self.name, 'Split Max':df.Split.max(),
                          'Split Min':df.Split.min()}
        else:
            individual = {'Name':self.name, 'Split Max':np.NaN,
                          'Split Min':np.NaN}
        return individual


