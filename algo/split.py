import pandas as pd

def interpolation(data: pd.DataFrame):
    data.loc[:, 'real_timestamp'] = data['real_timestamp'].apply(pd.Timedelta, args=("S"))
    data = data.set_index('real_timestamp').loc[:, 'amp0':'phs63'].resample('0.001S').interpolate(method='polynomial', order=2).reset_index()
    data.loc[:, 'real_timestamp'] = data['real_timestamp'].apply(lambda x: x.total_seconds())
    return data.dropna()
