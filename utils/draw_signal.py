import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
    

def draw_one(data: pd.Series, target='phs20', s=0, e=-1, color_range=[]):
    # 用于绘制某个确定子载波的图样，是查看功能
    # color_range是给后续警告留出的接口，注意传入list前小后大
    sns.lineplot(data=data[s:e], x='real_timestamp', y=target)
    for r in color_range:
        plt.axvspan(xmin=r[0], xmax=r[1], color='red', alpha=0.3)
    plt.show()


def draw_static(data: pd.DataFrame):
    # 绘制一系列的图样
    pass
