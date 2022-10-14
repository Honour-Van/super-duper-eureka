import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt

class Splitter:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.synthesised = None
        self.rolled = None
        self.rolled_agg = None
        self.finishing_points = None

    def interpolation(self, data: pd.DataFrame=None):
        if data is None:
            data = self.data
        data.loc[:, 'real_timestamp'] = data['real_timestamp'].apply(pd.Timedelta, args=("S"))
        data = data.set_index('real_timestamp').loc[:, 'amp0':'phs63'].resample('0.001S').interpolate(method='polynomial', order=2).reset_index()
        data.loc[:, 'real_timestamp'] = data['real_timestamp'].apply(lambda x: x.total_seconds())
        self.data = data.dropna()
        return self.data

    def synthesize(self, data: pd.DataFrame=None):
        if data is None:
            data = self.data
        data["amp"] = data.loc[:,'amp0':'amp63'].apply(lambda x: x.mean(), axis=1)
        data["phs"] = data.loc[:,'phs0':'phs63'].apply(lambda x: x.mean(), axis=1)
        self.synthesised = data[['real_timestamp', 'amp', 'phs']]
        return self.synthesised

    def filter(self, data: pd.DataFrame=None, filt_col=['amp', 'phs'], kernel_size=1001):
        pd.options.mode.chained_assignment = None  # default='warn'
        if data is None:
            data = self.synthesised
        data['filtered_phs'] = signal.medfilt(data['phs'], kernel_size=kernel_size)
        data['filtered_amp'] = signal.medfilt(data['amp'], kernel_size=kernel_size)
        return data

    def sliding_window(self, synthesised: pd.DataFrame=None, window_size=4001):
        if synthesised is None:
            synthesised = self.synthesised
        rolled = synthesised.iloc[:, 1:].rolling(window_size).var()
        rolled_agg = rolled.agg(['mean', 'std']).apply(lambda x: 0.5 * x[0] + 0.8 * x[1], axis=0)
        self.rolled = rolled
        self.rolled_agg = rolled_agg
        return rolled, rolled_agg
    
    def find_finishing_points(self, rolled: pd.DataFrame=None, rolled_agg: pd.DataFrame=None, items=['phs', 'filtered_phs']):
        if rolled is None:
            rolled = self.rolled
        if rolled_agg is None:
            rolled_agg = self.rolled_agg

        col_gt_than_threshold = {'phs':False, 'amp':False, 'filtered_phs':False, 'filtered_amp':False}
        finishing_points = {'phs':[0], 'amp':[0], 'filtered_phs':[0], 'filtered_amp':[0]}

        for index, row in rolled.iterrows():
            for col in rolled.columns:
                if row[col] < rolled_agg[col]:
                    if col_gt_than_threshold[col] and finishing_points[col][-1] + 5000 < index:
                        # TODO 根据freq动态调整
                        finishing_points[col].append(index)
                    col_gt_than_threshold[col] = False
                elif row[col] >= rolled_agg[col]:
                    col_gt_than_threshold[col] = True
        self.finishing_points = {k:finishing_points[k][1:] for k in items}
        return finishing_points


    def draw_synth(self, rolled=None, rolled_agg=None):
        palatte = {'phs':'blue', 'amp':'red', 'filtered_phs':'green', 'filtered_amp':'orange'}
        if rolled is None:
            rolled = self.rolled
        if rolled_agg is None:
            rolled_agg = self.rolled_agg

        x = self.synthesised['real_timestamp']
        plt.figure(figsize=(20, 10))
        for col in rolled.columns:
            plt.plot(x, rolled[col], label=col, color=palatte[col])
            plt.hlines(rolled_agg[col], x[0], x.iloc[-1], color=palatte[col], linestyles='dashed')
            if col in self.finishing_points:
                for point in self.finishing_points[col]:
                    plt.axvline(self.synthesised.loc[point, 'real_timestamp'], color=palatte[col], linestyle='--')

        plt.tight_layout()
        plt.legend()
        plt.show()
    
    