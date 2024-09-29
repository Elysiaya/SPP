import math

def Saastamoinen(h, hrel, fai, z):
    """
    Saastamoinen 模型计算对流层延迟
    :param z: 天顶角
    :param fai: 测站的纬度
    :param hrel: 相对湿度
    :param h:海拔高度
    :return:
    """
    # 使用标准大气模型

    # p为大气压力
    p = 1013.25 * math.pow(1 - 2.2557e-5 * h, 5.2568)
    # t为大气绝对温度
    t = 15 - 6.5e-3 * h + 273.15
    # e为大气水汽压力
    e = 6.108 * math.exp((17.15 * t - 4684.0) / (t - 38.45)) * hrel
    # 静力学延迟（干延迟）
    T_h = 0.0022768 * p / (1 - 0.00266 * math.cos(2 * fai) - 0.00028 * h * 1e-3) * (1 / math.cos(z))
    # 湿延迟
    T_w = 0.0022768 * (1255 / t + 0.05) * e * (1 / math.cos(z))
    # 总延迟
    T_r = T_h + T_w
    return T_r