import numpy as np
import math


def xyz2blh(xyz):  # 空间直角坐标转换为大地坐标
    blh = [0, 0, 0]
    # 长半轴
    a = 6378137.0
    # 扁率
    f = 1.0 / 298.257223563
    e2 = f * (2 - f)
    r2 = xyz[0] * xyz[0] + xyz[1] * xyz[1]
    z = xyz[2]
    zk = 0.0

    while (abs(z - zk) >= 0.0001):
        zk = z
        sinp = z / math.sqrt(r2 + z * z)
        v = a / math.sqrt(1.0 - e2 * sinp * sinp)
        z = xyz[2] + v * e2 * sinp

    if (r2 > 1E-12):
        blh[0] = math.atan(z / math.sqrt(r2))
        blh[1] = math.atan2(xyz[1], xyz[0])
    else:
        if (r2 > 0):
            blh[0] = math.pi / 2.0
        else:
            blh[0] = -math.pi / 2.0
        blh[1] = 0.0

    blh[2] = math.sqrt(r2 + z * z) - v
    return blh


def XYZ2ENU(Xs, Xr):
    """
    计算卫星的站心坐标,所有角度以弧度制表示
    :param Xs: 卫星在ECEF中的坐标向量XYZ
    :param Xr: 接收机在ECEF中的坐标向量XYZ
    :return:r为卫星向径，A为卫星方位角，h为卫星的高度角。
    """
    B, L, _ = xyz2blh(Xr)
    s = np.array(Xs)
    r = np.array(Xr)
    R = np.array([[-math.sin(L), math.cos(L), 0], [-math.sin(B) * math.cos(L), -math.sin(B) * math.sin(L), math.cos(B)],
                  [math.cos(B) * math.cos(L), math.cos(B) * math.sin(L), math.sin(B)]])

    Xl = R @ (s - r).T
    E, N, U = Xl

    # 卫星向径
    r = math.sqrt(E ** 2 + N ** 2 + U ** 2)
    # 卫星方位角
    A = math.atan2(E, N)
    if A < 0:
        A += 2 * math.pi
    if A > 2 * math.pi:
        A -= 2 * math.pi
    # 卫星高度角
    h = math.atan2(U, math.sqrt(E ** 2 + N ** 2))
    h = abs(h)
    return r, A, h, B


if __name__ == '__main__':
    Xr = [2919864.60820601, -5383759.7669709, 1774610.58017225]
    Xs = [7802486.770990263, -17802947.71280072, 17778697.31150082]
    # print(xyz2blh(Xr))
    r1 = XYZ2ENU(Xs, Xr)
    print(r1)