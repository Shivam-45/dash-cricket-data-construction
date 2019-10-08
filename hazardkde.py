# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 21:12:37 2019

@author: lukem
"""

import pandas as pd
import matplotlib.pyplot as plt
import json

def smoothing(df, bw):
    limit = int(max(df.event_at))-1
    haz = [0]*(limit)
    ref = 1
    for i in range(limit):
        if df[df['event_at']==i].empty:
            pass
        else:
            haz[i]=df['hazard'][ref]
            ref += 1
    hazrev = haz[::-1]
    hazards = hazrev + haz
    ker = [0]*limit*2
    for i in range(bw,limit*2-bw):
        ker[i]+=sum(hazards[i-bw:i+bw])/(bw*2)
    ker = ker[limit:]
    return ker    

def df_hazard(name):
    df = pd.read_csv(f'data/batting/test/eventTable/{name}.csv')
    df['hazard'] = df['observed']/df['at_risk']
    ker1 = smoothing(df, 3)
    ker2 = smoothing(df, 10)
    ker3 = smoothing(df, 20)
    kde_df = pd.DataFrame(data={'Name':name,'time':list(range(int(max(df.event_at))-1)),'hazard1':ker1,'hazard2':ker2,'hazard3':ker3})
    return kde_df
    
with open(f'data/batting/test/ids_names.json') as file:
    i_n = json.load(file)

master_df = pd.DataFrame(columns=['Name','time','hazard1','hazard2','hazard3'])
for n in i_n.values():    
    df = df_hazard(n)
    df.to_csv(f'data/batting/test/kde/{n}.csv')
    master_df = master_df.append(df)
master_df.to_csv(f'data/batting/test/kde/master.csv')
