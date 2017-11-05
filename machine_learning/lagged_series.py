import numpy as np
import pandas as pd


def create_lagged_series(data_file, start_date, lags=5):
    ts = pd.read_csv(data_file, sep=';', header=1, index_col='time', parse_dates=True)

    tslag = pd.DataFrame(index=ts.index)
    tslag['Today'] = ts['closeBid']
    tslag['Volume'] = ts['volume']

    for i in range(0, lags):
        tslag['Lag%s' % str(i+1)] = ts['closeBid'].shift(i+1)

    tsret = pd.DataFrame(index=tslag.index)
    tsret['Volume'] = tslag['Volume']
    tsret['Today'] = tslag['Today'].pct_change() * 100

    for i,x in enumerate(tsret['Today']):
        if abs(x) < 0.0001:
            tsret['Today'][i] = 0.0001

    for i in range(0, lags):
        tsret['Lag%s' % str(i+1)] = tslag['Lag%s' % str(i+1)].pct_change() * 100

    tsret['Direction'] = np.sign(tsret['Today'])
    tsret = tsret[tsret.index >= start_date]

    return tsret




