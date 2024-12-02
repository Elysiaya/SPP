def IF_combination(C1_pseudo_range: float, C2_pseudo_range: float,frequency1: float,frequency2: float) -> float:
    """
    Ionosphere free combination
    :param C1_pseudo_range: 第1频段的伪距观测值
    :param C2_pseudo_range: 第2频段的伪距观测值
    :param frequency1: 第1频段频率
    :param frequency2: 第2频段频率
    :return: 双频改正之后的伪距观测值
    """

    GPS_L1_frequency = 1575.42  # 频率/HZ
    GPS_L2_frequency = 1227.60  # 频率/HZ
    GPS_L5_frequency = 1176.45  # 频率/HZ
    # 双频伪距无电离层表达式
    pseudo_range = (frequency1 ** 2 * C1_pseudo_range / (
            frequency1 ** 2 - frequency2 ** 2)) - (frequency2 ** 2 * C2_pseudo_range / (
            frequency1 ** 2 - frequency2 ** 2))
    return pseudo_range