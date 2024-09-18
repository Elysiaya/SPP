class GPS_Satellite_observations:
    def __init__(self, o: str) -> None:
        temp = list(filter(None, o.split(" ")))
        self.PRN = temp[0]
        C1C_pseudo_range = float(temp[1])
        self.pseudorange = C1C_pseudo_range
        # if len(temp) > 22:
        # GPS_L1_frequency = 1575.42  # 频率/MHZ
        # GPS_L2_frequency = 1227.60  # 频率/MHZ
        # GPS_L5_frequency = 1176.45  # 频率/MHZ
        #     C5Q_pseudo_range = float(temp[22])
        #     # 双频伪距无电离层表达式
        #     self.pseudorange = GPS_L1_frequency ** 2 * C1C_pseudo_range / (
        #             GPS_L1_frequency ** 2 - GPS_L5_frequency ** 2) - GPS_L5_frequency ** 2 * C5Q_pseudo_range / (
        #                                GPS_L1_frequency ** 2 - GPS_L5_frequency ** 2)
        # else:
        #     self.pseudorange = C1C_pseudo_range


class BDS_Satellite_observations:
    def __init__(self, o: str) -> None:
        pass


class Galileo_Satellite_observations:
    def __init__(self, o: str) -> None:
        pass


class GLONASS_Satellite_observations:
    def __init__(self, o: str) -> None:
        pass
