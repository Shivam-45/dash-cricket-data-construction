# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 17:03:58 2019

@author: lukem
"""

import pandas as pd
import json

import rpy2.robjects as ro
from rpy2.robjects.conversion import localconverter
import rpy2.robjects.packages as rpackages
from rpy2.robjects.vectors import StrVector
from rpy2.rinterface import RRuntimeError

utils = rpackages.importr('utils')
utils.chooseCRANmirror(ind=1);
packnames = ['bpcp']
names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
if len(names_to_install) > 0:
    utils.install_packages(StrVector(names_to_install))

ro.pandas2ri.activate()

bpcp = rpackages.importr('bpcp')

def bpcp_survival(df, runs_max):
    try:
        bfit = bpcp.bpcp(df[0],df[1],Delta=1)
    except RRuntimeError:
        return pd.Series(index=['time', 'survival','lower','upper'])
    with localconverter(ro.default_converter + ro.pandas2ri.converter):
        surv_results = bfit
    return surv_results

with open(f'data/batting/test/ids_names.json') as file:
    i_n = json.load(file)

master_df = pd.DataFrame(columns=['Runs', 'Dismissed'])
names = []
for i, n in i_n.items():
    names.append(n)
print(names)
# =============================================================================
# runs = int(df.Runs.max())
# r_df = ro.pandas2ri.py2ri(df)
#     
# df = bpcp_survival(r_df,runs)
# df = pd.DataFrame(df)
# df.to_csv(f'data/batting/test/KMF/SR Tendulkar.csv')
# =============================================================================
