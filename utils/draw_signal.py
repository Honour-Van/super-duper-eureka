import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from math import ceil

def draw_one(data: pd.DataFrame, target='phs20', s=0, e=float('inf'), color_range=[]):
    # 用于绘制某个确定子载波的图样，是查看功能
    # color_range是给后续警告留出的接口，注意传入list前小后大
    sns.lineplot(data=data[(data['real_timestamp']>s)&(data['real_timestamp']<e)], x='real_timestamp', y=target)
    for r in color_range:
        plt.axvspan(xmin=r[0], xmax=r[1], color='red', alpha=0.3)
    plt.show()


def draw_static(data: pd.DataFrame):
    # 绘制一系列的图样
    targets=[*['amp'+str(x) for x in range(64)], *['phs'+str(x) for x in range(64)]]
    num_of_plots = len(targets)
    row_of_plots = ceil(num_of_plots // 4)
    
    plt.figure(figsize=(20, 3*row_of_plots))
    for i, target in enumerate(targets):
        plt.subplot(row_of_plots, 4, i+1)
        sns.lineplot(data=data, x='real_timestamp', y=target)
    plt.tight_layout()
    plt.show()
