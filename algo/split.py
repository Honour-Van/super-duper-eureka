import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt

class Splitter:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.synthesised = None
        self.rolled = None
        self.rolled_agg = None
    
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
    
    def draw_synth(self, rolled=None, rolled_agg=None):
        if rolled is None:
            rolled = self.rolled
        if rolled_agg is None:
            rolled_agg = self.rolled_agg

        x = self.synthesised['real_timestamp']
        plt.figure(figsize=(20, 10))
        for col in rolled.columns:
            plt.plot(x, rolled[col], label=col)
        plt.hlines(rolled_agg['amp'], x[0], x.iloc[-1], colors='b', linestyles='dashed')
        plt.hlines(rolled_agg['phs'], x[0], x.iloc[-1], colors='orange', linestyles='dashed')
        plt.hlines(rolled_agg['filtered_amp'], x[0], x.iloc[-1], colors='r', linestyles='dashed')
        plt.hlines(rolled_agg['filtered_phs'], x[0], x.iloc[-1], colors='g', linestyles='dashed')
        # plt.tight_layout()
        plt.legend()
        plt.show()
    
