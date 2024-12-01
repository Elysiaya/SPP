import datetime
import math
import numpy as np

from Saastamoinen import Saastamoinen
from SatelliteOrbit.GPS_satellite_orbit import GPS_satellite_orbit
from XYZ2ENU import XYZ2ENU

Radv = 7.2921151467e-5  # 地球自转角速度（rad/s）
GM = 3.986005e14  # 地球引力常数GM（m^3/s^2）
C = 2.99792458e8  # 真空中的光速（m/s）


def computer(observations, Ephemerides, X0, iter, cutoff_angle):
    """
    计算矩阵A L
    :param observations:观测数据列表
    :param Ephemeris:卫星星历
    :param X0:迭代初始值
    :param iter:当前迭代次数
    :param cutoff_angle:截止高度角(弧度制)
    :return:
    """
    A = []
    L = []
    for _, observation in observations.iterrows():
        observations_time = observation['Time'] #观测时间
        PRN = observation['PRN'] #卫星号
        pseudo_range = observation['IF_c'] #无电离层组合卫星伪距
        # 选择对应的星历
        Ephemeris = Ephemerides[Ephemerides["PRN"] == PRN].iloc[0].tolist()
        GSO = GPS_satellite_orbit(Ephemeris)

        # 计算卫星信号发射的概略时刻
        dtr = X0[3] / C  # 将接收机钟差赋值到dtr
        dts = 0
        # 设置信号传播时间的初值
        t0si = pseudo_range / C - dtr + dts
        while True:
            # 计算信号发射时刻
            Tsi = observations_time - datetime.timedelta(seconds=t0si)
            # 计算卫星在Tsi时刻的位置
            satellite_position = GSO.Run(Tsi)
            # 进行地球自传改正
            a = Radv * t0si
            satellite_position = np.array(
                [[math.cos(a), math.sin(a), 0], [-math.sin(a), math.cos(a), 0], [0, 0, 1]]) @ np.array(
                satellite_position)
            # print(satellite_position)
            # 计算卫星和测站的几何位置
            Rsr = math.sqrt((satellite_position[0] - X0[0]) ** 2 + (satellite_position[1] - X0[1]) ** 2 + (
                    satellite_position[2] - X0[2]) ** 2)
            t1si = Rsr / C
            if abs(t0si - t1si) < 10e-7:
                break
            else:
                t0si = t1si

        R = Rsr
        b0si = (X0[0] - satellite_position[0]) / R
        b1si = (X0[1] - satellite_position[1]) / R
        b2si = (X0[2] - satellite_position[2]) / R
        b3si = 1

        # # 计算对流层延迟改正量，前两次不改
        if iter > 3:
            R_s, A_s, H_s, BLH = XYZ2ENU(satellite_position, X0[0:3])
            # 如果高度角小于截止高度角，跳过这颗卫星
            if H_s<cutoff_angle:
                break
            D_troposphere = Saastamoinen(BLH[2], 0.7, BLH[0], H_s)
        else:
            D_troposphere = 0
        diono = 0  # 电离层延迟改正量，采用无电离层伪距观测组合值时此项为0
        D_RTCM = 0  # 对伪距的差分改证值
        dts = GSO.sat_clk_error  #卫星钟差
        dtprel = GSO.d_prel  # 相对论效应改正
        l = pseudo_range - R + C * (dts + dtprel) - D_troposphere - diono + D_RTCM
        A.append([b0si, b1si, b2si, b3si])
        L.append(l)

    return np.array(A), np.array(L)
