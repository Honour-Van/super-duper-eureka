import pandas as pd
from scipy import signal

def interpolation(data: pd.DataFrame):
    data.loc[:, 'real_timestamp'] = data['real_timestamp'].apply(pd.Timedelta, args=("S"))
    data = data.set_index('real_timestamp').loc[:, 'amp0':'phs63'].resample('0.001S').interpolate(method='polynomial', order=2).reset_index()
    data.loc[:, 'real_timestamp'] = data['real_timestamp'].apply(lambda x: x.total_seconds())
    return data.dropna()

def synthesis(data: pd.DataFrame):
    data["amp"] = data.loc[:,'amp0':'amp63'].apply(lambda x: x.mean(), axis=1)
    data["phs"] = data.loc[:,'phs0':'phs63'].apply(lambda x: x.mean(), axis=1)
    return data[['real_timestamp', 'amp', 'phs']]

def filter(data: pd.DataFrame, filt_col=['amp', 'phs'], kernel_size=1001):
    pd.options.mode.chained_assignment = None  # default='warn'
    data['filtered_phs'] = signal.medfilt(data['phs'], kernel_size=kernel_size)
    data['filtered_amp'] = signal.medfilt(data['amp'], kernel_size=kernel_size)
    return data
