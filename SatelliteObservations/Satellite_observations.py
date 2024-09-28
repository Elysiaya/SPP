class GPS_Satellite_observations:
    def __init__(self, o: str) -> None:
        self.PRN = o[0:3]
        self.pseudorange = self.__get_pseudo_range(o)

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

if __name__ == "__main__":
    # s1 = ('G31  21764306.240 7 114372452.09007       273.043 7        47.082    21764305.954 7        45.342    '
    #       '21764307.099 7  89121532.95707       212.762 7        45.342    21764307.789 7  89121590.95607       '
    #       '212.845 7        43.323')
    s1 = "G28  22463511.206 7 118046877.69107      -403.611 7        44.519    22463511.005 5        32.784    22463512.717 5  91984757.78605      -314.499 5        32.784    22463513.497 7  91984768.78307      -314.486 7        44.030    22463518.470 7  88152126.69907      -301.424 7        47.804"
    g1 = GPS_Satellite_observations(s1)
    000
    # g2 = Galileo_Satellite_observations(s1)
