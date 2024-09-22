class GPS_Satellite_observations:
    def __init__(self, o: str) -> None:
        temp = list(filter(None, o.split(" ")))
        self.PRN = temp[0]
        C1C_pseudo_range = float(temp[1])
        # self.pseudorange = C1C_pseudo_range
        if len(temp) > 10:
            C2C_pseudo_range = float(temp[10])
            # C5Q_pseudo_range = float(temp[22])

            GPS_L1_frequency = 1575.42e8  # 频率/HZ
            GPS_L2_frequency = 1227.60e8  # 频率/HZ
            GPS_L5_frequency = 1176.45e8  # 频率/HZ
            # 双频伪距无电离层表达式
            self.pseudorange = (GPS_L1_frequency ** 2 * C1C_pseudo_range / (
                    GPS_L1_frequency ** 2 - GPS_L2_frequency ** 2)) - (GPS_L2_frequency ** 2 * C2C_pseudo_range / (
                                       GPS_L1_frequency ** 2 - GPS_L2_frequency ** 2))



class BDS_Satellite_observations:
    def __init__(self, o: str) -> None:
        pass


class Galileo_Satellite_observations:
    def __init__(self, o: str) -> None:
        pass


class GLONASS_Satellite_observations:
    def __init__(self, o: str) -> None:
        pass

if __name__ == "__main__":
    s1 = ('G31  21764306.240 7 114372452.09007       273.043 7        47.082    21764305.954 7        45.342    '
          '21764307.099 7  89121532.95707       212.762 7        45.342    21764307.789 7  89121590.95607       '
          '212.845 7        43.323')
    g1 = GPS_Satellite_observations(s1)
    g2 = Galileo_Satellite_observations(s1)
