from pandas import DataFrame, Series


class GPS_Satellite_observations:
    def __init__(self, obs: Series) -> None:
        self.PRN = obs["PRN"]
        self.pseudorange = obs["C1C"]

    @staticmethod
    def __get_pseudo_range(o: str):
        """
        获取伪距
        :param o:
        :return: 伪距
        """
        C1C_pseudo_range = float(o[4:17])
        if len(o) < 100:
            return C1C_pseudo_range
        if " " not in o[101:113]:
            C2C_pseudo_range = float(o[101:113])
        elif " " not in o[165:177]:
            C2C_pseudo_range = float(o[165:177])
        else:
            return C1C_pseudo_range
        # 单频观测
        # pseudo_range = float(o[4:17])

        # 双频观测，如果有双频

        GPS_L1_frequency = 1575.42e8  # 频率/HZ
        GPS_L2_frequency = 1227.60e8  # 频率/HZ
        GPS_L5_frequency = 1176.45e8  # 频率/HZ
        # 双频伪距无电离层表达式
        pseudo_range = (GPS_L1_frequency ** 2 * C1C_pseudo_range / (
                GPS_L1_frequency ** 2 - GPS_L2_frequency ** 2)) - (GPS_L2_frequency ** 2 * C2C_pseudo_range / (
                GPS_L1_frequency ** 2 - GPS_L2_frequency ** 2))
        return pseudo_range


class BDS_Satellite_observations:
    def __init__(self, o: str) -> None:
        pass


class Galileo_Satellite_observations:
    def __init__(self, o: str) -> None:
        pass


class GLONASS_Satellite_observations:
    def __init__(self, o: str) -> None:
        pass
