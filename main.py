import datetime
import math
from IF import IF_combination
import numpy as np
import pandas as pd
from RINEX.RINEX3_N import RINEX3_N
from RINEX.RINEX3_O import RINEX3_O
from compute import computer
import matplotlib.pyplot as plt

Radv = 7.2921151467e-5  # 地球自转角速度（rad/s）
GM = 3.986005e14  # 地球引力常数GM（m^3/s^2）
C = 2.99792458e8  # 真空中的光速（m/s）

# 读取文件
rinex_n = RINEX3_N("./data/N/BRDM00DLR_S_20242640000_01D_MN.rnx")
rinex_o = RINEX3_O("./data/O/WUH200CHN_R_20242640000_01D_30S_MO.rnx")
# 选择GPS星历和Galileo星历
Ephemeris = rinex_n.df[(rinex_n.df["PRN"].str[0] == "E") | (rinex_n.df["PRN"].str[0] == "G")]

def main(observations_date: datetime.datetime):
    # 根据时间筛选历元
    GPS_observations = rinex_o.gps_df[rinex_o.gps_df["Time"] == observations_date]
    galileo_observations = rinex_o.galileo_df[rinex_o.galileo_df["Time"] == observations_date]
    # 筛选可用卫星
    GPS_observations = GPS_observations.dropna(axis=0,subset=["C1C","C2W"],how="any")
    GPS_observations["IF_c"] = IF_combination(GPS_observations["C1C"], GPS_observations["C2W"], 1575.42, 1227.60)

    galileo_observations = galileo_observations.dropna(axis=0,subset=["C1X","C5X"],how="any")
    galileo_observations["IF_c"] = IF_combination(galileo_observations["C1X"], galileo_observations["C5X"], 1575.42, 1176.45)
    print(f"共有 {GPS_observations.shape[0] + galileo_observations.shape[0]} 颗卫星")

    observations = pd.concat([GPS_observations[["PRN","Time","IF_c"]], galileo_observations[["PRN","Time","IF_c"]]])

    # 筛选星历，定义筛选范围为前后一个小时
    s_date = observations_date - datetime.timedelta(hours=1)
    e_date = observations_date + datetime.timedelta(hours=1)
    cond = (Ephemeris["Toc"] >= s_date) & (Ephemeris["Toc"] <= e_date)
    Ephemeris_by_date = Ephemeris[cond].reset_index(drop=True)

    # 初始化，置测站位置为1，1，1，接收机钟差为0
    X0 = [1, 1, 1, 0]

    # 设置最大迭代次数
    max_iteration = 20
    for iteration in range(max_iteration):
        A, L = computer(observations, Ephemeris_by_date, X0, iteration,10*math.pi/180)
        if A.shape[0]<4:
            print(f"共有 {A.shape[0]} 颗可用卫星")
            return None
        P = np.diag([1] * A.shape[0])

        Xi = np.linalg.inv(A.T @ P @ A) @ (A.T @ P @ L)
        if Xi[0] > 1e-6 or Xi[1] > 1e-6 or Xi[2] > 1e-6:
            X0 = X0 + Xi
            print(X0)
            # print(f"第{iteration + 1}次迭代:接收机坐标{X0[0:3]}")
        else:
            print(f"在高度角范围内的卫星有{A.shape[0]}颗")
            print(f"接收机坐标为:{X0[0:3]}")
            print(f"接收机钟差为:{X0[3] / C}")

            # 根据周解文件获取的WHU测站坐标
            STA_X = -0.226775027647810E+07
            STA_Y = 0.500915448294720E+07
            STA_Z = 0.322129434237148E+07

            print(f"Delta_X={X0[0] - STA_X}")
            print(f"Delta_Y={X0[1] - STA_Y}")
            print(f"Delta_Z={X0[2] - STA_Z}")
            error=math.sqrt((X0[0] - STA_X)**2+(X0[1] - STA_Y)**2+(X0[2] - STA_Z)**2)
            print(f"{error}")

            # G = np.linalg.inv(A.T @ A)
            # HDOP = math.sqrt(G[0][0] + G[1][1])
            # print(f"HDOP={HDOP}")
            return X0,error


if __name__ == "__main__":
    date = rinex_o.gps_df.drop_duplicates(subset=["Time"], keep="first", inplace=False)["Time"]
    # main(date.iloc[5])
    es=[]
    for i in range(200):
        print(f"第{i}次迭代")
        _,e = main(date.iloc[i])
        es.append(e)
    plt.scatter(range(len(es)),es)
    plt.show()

    
