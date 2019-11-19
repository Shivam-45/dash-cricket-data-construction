import pandas as pd
import matplotlib.pyplot as plt
import json


def _smoothing(df, bw):
    limit = 121+bw
    haz = [0] * limit
    ref = 1
    for i in range(limit):
        if df[df['event_at'] == i].empty:
            pass
        else:
            try:
                haz[i] = df['hazard'][ref]
                ref += 1
            except KeyError:
                break
    hazrev = haz[:0:-1]
    hazards = hazrev + haz
    ker = [0]*(241+bw*2)
    for i in range(bw, len(ker)-bw):
        for j in range(-bw, bw+1):
            ker[i] += (1 - abs(j) / bw) * hazards[i+j] / bw
    ker = ker[limit-1:]
    return ker


def kernel_density_df(name):
    bw = 20
    df = pd.read_csv(f'data/batting/test/eventTable/{name}.csv')
    df['hazard'] = df['observed']/df['at_risk']
    ker = _smoothing(df, bw)
    kd_df = pd.DataFrame(data={'Name': name, 'time': list(range(121+bw)), 'hazard': ker})
    return kd_df
