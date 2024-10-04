import pandas as pd
from pandas import DataFrame, Series


class GPS_Satellite_observations:
    def __init__(self, obs: Series) -> None:
        self.PRN = obs["PRN"]
        c1 = self.select_best(obs=obs, frequency="C1")
        c2 = self.select_best(obs=obs, frequency="C2")
        c5 = self.select_best(obs=obs, frequency="C5")
        if c1 and c2:
            self.pseudorange = self.__get_pseudo_range(c1, c2)
        elif c1 is not None:
            self.pseudorange = c1
        elif c2 is not None:
            self.pseudorange = c2
        elif c5 is not None:
            self.pseudorange = c5

    @staticmethod
    def __get_pseudo_range(C1_pseudo_range: float, C2_pseudo_range: float) -> float:
        """
        获取双频改正之后的伪距观测值
        :param C1_pseudo_range: L1频段的伪距观测值
        :param C2_pseudo_range: L2频段的伪距观测值
        :return: 双频改正之后的伪距观测值
        """

        GPS_L1_frequency = 1575.42  # 频率/HZ
        GPS_L2_frequency = 1227.60  # 频率/HZ
        GPS_L5_frequency = 1176.45  # 频率/HZ
        # 双频伪距无电离层表达式
        pseudo_range = (GPS_L1_frequency ** 2 * C1_pseudo_range / (
                GPS_L1_frequency ** 2 - GPS_L2_frequency ** 2)) - (GPS_L2_frequency ** 2 * C2_pseudo_range / (
                GPS_L1_frequency ** 2 - GPS_L2_frequency ** 2))
        return pseudo_range

    @staticmethod
    def select_best(obs: Series, frequency: str):
        """
        选择最好的伪距观测值
        :return: 最好的伪距观测值
        """
        prior = "PWCSLXYMND"
        for p in prior:
            obs_type = frequency + p
            if (obs_type in obs) and not (pd.isnull(obs[obs_type])):
                return obs[obs_type]

        return None


class BDS_Satellite_observations:
    def __init__(self, o: str) -> None:
        pass


class Galileo_Satellite_observations:
    def __init__(self, o: str) -> None:
        pass


class GLONASS_Satellite_observations:
    def __init__(self, o: str) -> None:
        pass
