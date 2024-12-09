import numpy as np

import datetime
import math

from matplotlib import pyplot as plt

from RINEX.RINEX3_N import RINEX3_N
from RINEX.RINEX3_O import RINEX3_O
from compute import computer

Radv = 7.2921151467e-5  # 地球自转角速度（rad/s）
GM = 3.986005e14  # 地球引力常数GM（m^3/s^2）
C = 2.99792458e8  # 真空中的光速（m/s）

# 读取文件
rinex_n = RINEX3_N("./data/N/BRDM00DLR_S_20242640000_01D_MN.rnx")
rinex_o = RINEX3_O("./data/O/WUH200CHN_R_20242640000_01D_30S_MO.rnx")
# 筛选GPS卫星星历
GPS_Ephemeris = rinex_n.df[rinex_n.df["PRN"].str[0] == "G"]
def least_square(GPS_observations_date: datetime.datetime):
    # 根据时间筛选历元
    GPS_observations = rinex_o.gps_df[rinex_o.gps_df["Time"] == GPS_observations_date]
    observations = GPS_observations.dropna(axis=0,subset=["C1C"])
    print(f"共有 {observations.shape[0]} 颗卫星")

    # 筛选星历，定义筛选范围为前后一个小时
    s_date = GPS_observations_date - datetime.timedelta(hours=1)
    e_date = GPS_observations_date + datetime.timedelta(hours=1)
    cond = (GPS_Ephemeris["Toc"] >= s_date) & (GPS_Ephemeris["Toc"] <= e_date)
    GPS_Ephemeris_by_date = GPS_Ephemeris[cond].reset_index(drop=True)

    # 初始化，置测站位置为1，1，1，接收机钟差为0
    X0 = [1, 1, 1, 0]

    # 设置最大迭代次数
    max_iteration = 20
    for iteration in range(max_iteration):
        A, L = computer(observations, GPS_Ephemeris_by_date, X0, iteration,10*math.pi/180)
        if A.shape[0]<4:
            print(f"共有 {A.shape[0]} 颗可用卫星")
            return None
        P = np.diag([1] * A.shape[0])

        Xi = np.linalg.inv(A.T @ P @ A) @ (A.T @ P @ L)
        if Xi[0] > 1e-6 or Xi[1] > 1e-6 or Xi[2] > 1e-6:
            X0 = X0 + Xi
        else:
            # print(f"在高度角范围内的卫星有{A.shape[0]}颗")
            # print(f"接收机坐标为:{X0[0:3]}")
            # print(f"接收机钟差为:{X0[3] / C}")
            #
            # # 根据周解文件获取的WHU测站坐标
            # STA_X = -0.226775027647810E+07
            # STA_Y = 0.500915448294720E+07
            # STA_Z = 0.322129434237148E+07
            #
            # print(f"Delta_X={X0[0] - STA_X}")
            # print(f"Delta_Y={X0[1] - STA_Y}")
            # print(f"Delta_Z={X0[2] - STA_Z}")
            #
            # print(f"{math.sqrt((X0[0] - STA_X)**2+(X0[1] - STA_Y)**2+(X0[2] - STA_Z)**2)}")

            # G = np.linalg.inv(A.T @ A)
            # HDOP = math.sqrt(G[0][0] + G[1][1])
            # print(f"HDOP={HDOP}")
            Nk = np.linalg.inv(A.T @ P @ A)
            return X0,Nk,Xi,A,L

def kalman_filter(X:np.array,P:np.array,F:np.array,Q:np.array,R:np.array,Z:np.array,H:np.array):
    """
    卡尔曼滤波,其中状态转移方程为
    X(k)=F*X(k-1)+Q
    测量方程为
    Z(k)=H*X(k)+R
    :param X:上一时刻的最佳估值
    :param Q:过程噪声
    :param F:状态转移矩阵
    :param R:观测噪声
    :param Z:观测值
    :param H:观测值转移矩阵
    :return:X 最佳估值,P 协方差矩阵
    """

    # 预测
    X_ = F @ X
    P_ = F @ P @ F.T + Q

    # 更新过程
    R = np.diag([5] * H.shape[0])
    # 求解卡尔曼增益
    K = P_ @ H.T @ np.linalg.inv(H @ P_ @ H.T + R)
    # 求解最佳估值
    X = X_ + K @ (Z - H @ X_)
    # 更新协方差矩阵
    P = (np.eye((K @ H).shape[0]) - K @ H ) @ P_

    return X,P


# 获取坐标初值
date = rinex_o.gps_df.drop_duplicates(subset=["Time"], keep="first", inplace=False)["Time"]
X0,Nk,Xi,A,L= least_square(date.iloc[0])

F = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,0]])
Q = np.array([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,10e9]])
P = np.diag([1] * F.shape[0])
R = np.diag([5] * A.shape[0])
a2 = []
for i in range(300):
    GPS_observations_date = date.iloc[i]
    GPS_observations = rinex_o.gps_df[rinex_o.gps_df["Time"] == GPS_observations_date]
    observations = GPS_observations.dropna(axis=0, subset=["C1C"])
    # 筛选星历，定义筛选范围为前后一个小时
    s_date = GPS_observations_date - datetime.timedelta(hours=1)
    e_date = GPS_observations_date + datetime.timedelta(hours=1)
    cond = (GPS_Ephemeris["Toc"] >= s_date) & (GPS_Ephemeris["Toc"] <= e_date)
    GPS_Ephemeris_by_date = GPS_Ephemeris[cond].reset_index(drop=True)
    #
    H, L = computer(observations, GPS_Ephemeris_by_date, X0, 1,10*math.pi/180)

    X2,P2= kalman_filter(Xi,P,F,Q,R,L,H)
    print(X0+X2)
    a2.append(X0+X2)
    print("="*80)
    Xi = X2
    P = P2

y1 = [i[0] + 0.226775027647810E+07 for i in a2]
y2 = [i[1] - 0.500915448294720E+07 for i in a2]
y3 = [i[2] - 0.322129434237148E+07 for i in a2]

x = range(len(y1))
plt.title("Kalman filtering  SPP error(XYZ)")
plt.xlabel("epoch")
plt.ylabel("Error")
plt.plot(x,y1)
plt.plot(x,y2)
plt.plot(x,y3)
plt.legend(["X","Y","Z"])
plt.show()
plt.savefig("figure3.png")

