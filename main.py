from RINEX_N import RINEX_N
from RINEX3_O import RINEX3_O
from GPS_satellite_orbit import GPS_satellite_orbit
import datetime
import math
import numpy as np
# 读取文件
rinex_n = RINEX_N("./data/BRDC00IGS_R_20242450000_01D_MN.rnx")
rinex_o = RINEX3_O("./data/ABMF00GLP_R_20242450000_01D_30S_MO.rnx")
# 筛选GPS卫星
GPS_Ephemeris = rinex_n.df[rinex_n.df.loc[:, "PRN"].str[0] == "G"]

# 获取当前观测值历元的观测时间，在广播星历中筛选出
e = 1
GPS_observations_date = rinex_o.epochs[e].date
# print(f"GPS observations date: {GPS_observations_date}")

# 定义筛选范围为前后一个小时
s_date = GPS_observations_date - datetime.timedelta(hours=1)
e_date = GPS_observations_date + datetime.timedelta(hours=1)
cond = (GPS_Ephemeris.loc[:, "Toc"] >= s_date) & (GPS_Ephemeris.loc[:, "Toc"] <= e_date)
GPS_Ephemeris_by_date = GPS_Ephemeris[cond].reset_index(drop=True)

# # 计算卫星位置
# for column_name,GPS_Ephemeris_single in GPS_Ephemeris.iterrows():
#     GEO = GPS_satellite_orbit(GPS_Ephemeris_single.tolist())
#     GEO.Run(GPS_observations_date)

lsi = []
A = []
X0 = np.array([0, 0, 0, 0])
C = 2.99792458e8  # 真空中的光速（m/s）
while True:
    for o in rinex_o.epochs[e].GPS_observations:
        prn = o.PRN
        psi = o.pseudorange

        k1 = GPS_Ephemeris_by_date.loc[GPS_Ephemeris_by_date.loc[:, "PRN"] == prn].values.tolist()[0]
        GSO = GPS_satellite_orbit(k1)
        GSO.Run(GPS_observations_date, psi)
        dtrop = 0  # 对流层延迟改正量
        diono = 0  # 电离层延迟改正量
        D_RTCM = 0  # 对伪距差分改正值
        # 卫星钟差
        dtsi = GSO.sat_clk_error
        #
        R = math.sqrt((X0[0] - GSO.satellite_position[0]) ** 2 + (X0[1] - GSO.satellite_position[1]) ** 2 + (
                X0[2] - GSO.satellite_position[2]) ** 2)

        b0si = (X0[0] - GSO.satellite_position[0]) / R
        b1si = (X0[1] - GSO.satellite_position[1]) / R
        b2si = (X0[2] - GSO.satellite_position[2]) / R
        b3si = 1

        l = psi - R + C * dtsi - dtrop - diono + D_RTCM
        lsi.append(l)
        list1 = [b0si, b1si, b2si, b3si]
        A.append(list1)

    A = np.array(A)
    L = np.array(lsi)

    # print(L)
    # print(A)
    # 权阵
    Xi = np.linalg.inv(A.T @ A) @ (A.T @ L)
    # print(Xi)
    if Xi[0] > 0.001 or Xi[1] > 0.001 or Xi[2] > 0.001:
        X0 = X0 + Xi
        lsi = []
        A = []
    else:
        # print(f"X0: {X0}")
        print(f"接收机坐标为:{[X0[0], X0[1], X0[2]]}")

        print(
            f"偏差值{math.sqrt((X0[0] - 2919785.7120) ** 2 + (X0[1] - -5383745.0670) ** 2 + (X0[2] - 1774604.6920) ** 2)}m")

        print(f"接收机钟差为:{X0[3] / 3e+8}")
        break
