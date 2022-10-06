from math import sqrt, atan2
import pandas as pd


def parse_csi(csi_raw):
    # 用于处理csi所在的column
    csi_raw = csi_raw[csi_raw.index('[')+1:csi_raw.index(']')-1]
    csi_int = [int(x) for x in csi_raw.split()]

    csi_real = csi_int[::2]
    csi_img = csi_int[1::2]
    num_of_carrier = len(csi_real)
    csi_amp = [sqrt(csi_real[i]**2+csi_img[i]**2)
                for i in range(num_of_carrier)]
    csi_phs = [atan2(csi_img[i], csi_real[i])
                for i in range(num_of_carrier)]

    return [*csi_amp, *csi_phs]


def read_static(filename):
    data = pd.read_csv(filename)
    csi_data = pd.DataFrame(data['CSI_DATA'].apply(parse_csi).tolist())
    csi_data.columns = [*['amp'+str(x) for x in range(64)], *['phs'+str(x) for x in range(64)]]
    return pd.concat([data, csi_data], axis=1)



def read_dynamic():
    # TODO:增加
    pass


if __name__ == "__main__":
    read_static('CSI_Activity_Dataset/静止动作/蹲姿/Squat_v1ap.csv')