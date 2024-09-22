import datetime
import math

import numpy as np

from RINEX.RINEX3_N import RINEX3_N
from RINEX.RINEX3_O import RINEX3_O
from SatelliteOrbit.GPS_satellite_orbit import GPS_satellite_orbit

Radv = 7.2921151467e-5  # 地球自转角速度（rad/s）
GM = 3.986005e14  # 地球引力常数GM（m^3/s^2）
C = 2.99792458e8  # 真空中的光速（m/s）

# 读取文件
rinex_n = RINEX3_N("./data/BRDC00IGS_R_20242450000_01D_MN.rnx")
rinex_o = RINEX3_O("./data/ABMF00GLP_R_20242450000_01D_30S_MO.rnx")
# 筛选GPS卫星
GPS_Ephemeris = rinex_n.df[rinex_n.df["PRN"].str[0] == "G"]

e = 0
# 选取单个历元进行计算
obs = rinex_o.epochs[e].GPS_observations
# 获取当前观测值历元的观测时间，在广播星历中筛选出
GPS_observations_date = rinex_o.epochs[e].date

# 定义筛选范围为前后一个小时
s_date = GPS_observations_date - datetime.timedelta(hours=1)
e_date = GPS_observations_date + datetime.timedelta(hours=1)
cond = (GPS_Ephemeris["Toc"] >= s_date) & (GPS_Ephemeris["Toc"] <= e_date)
GPS_Ephemeris_by_date = GPS_Ephemeris[cond].reset_index(drop=True)

# 初始化，置测站位置为0，0，0，接收机钟差为dtr
X0 = [0, 0, 0, 0]
A = []
L = []
while True:
    for o in obs:
        # 卫星PRN
        PRN = o.PRN
        # 卫星伪距
        pseudo_range = o.pseudorange
        # 选择对应的星历
        Ephemeris = GPS_Ephemeris_by_date[GPS_Ephemeris_by_date["PRN"] == PRN].iloc[0].tolist()
        GSO = GPS_satellite_orbit(Ephemeris)
        # print(PRN, pseudo_range)

        # 计算卫星信号发射的概略时刻
        dtr = X0[3]  # 将接收机钟差赋值到dtr
        dts = GSO.get_sat_clk_error(GPS_observations_date)  # 获取卫星钟差
        t0si = pseudo_range / C - dtr + dts  # 计算信号传播时间
        while True:
            # 计算信号发射时刻
            Tsi = GPS_observations_date-datetime.timedelta(seconds=t0si)
            # 计算卫星在Tsi时刻的位置
            satellite_position = GSO.Run(Tsi)
            # print(satellite_position)
            # 计算卫星和测站的几何位置
            Rsr = math.sqrt((satellite_position[0]-X0[0])**2 + (satellite_position[1]-X0[1])**2+(satellite_position[2]-X0[2])**2)
            # 根据几何距离求信号传播时间
            t1si = Rsr / C
            if abs(t1si-t0si) < 10e-7:
                break
            else:
                t0si = t1si

        R = Rsr
        b0si = (X0[0] - satellite_position[0]) / R
        b1si = (X0[1] - satellite_position[1]) / R
        b2si = (X0[2] - satellite_position[2]) / R
        b3si = 1
        A.append([b0si, b1si, b2si, b3si])

        dtrop = 0 # 对流层延迟改正量
        diono = 0 # 电离层延迟改正量，采用无电离层伪距观测组合值时此项为0
        D_RTCM = 0 # 对伪距的差分改证值
        l = pseudo_range - R + C * dts - dtrop - diono + D_RTCM
        L.append(l)
    A = np.array(A)
    L = np.array(L)
    Xi = np.linalg.inv(A.T @ A) @ (A.T @ L)
    if Xi[0] > 1e-8 or Xi[1] > 1e-8 or Xi[2] > 1e-8:
        X0 = X0 + Xi
        L = []
        A = []
    else:
        print(f"接收机坐标为:{X0}")
        print(
            f"偏差:{math.sqrt((X0[0] - rinex_o.APPROX_POSITION[0]) ** 2 + (X0[1] - rinex_o.APPROX_POSITION[1]) ** 2 + (X0[2] - rinex_o.APPROX_POSITION[2]) ** 2)}")
        print(f"接收机钟差为:{X0[3] / 3e+8}")
        break