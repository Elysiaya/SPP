from datetime import datetime

from SatelliteObservations.Satellite_observations import *


class Epoch:
    #  C伪距;L载波;D多普勒;S信号强度
    # https://blog.csdn.net/Gou_Hailong/article/details/120911467
    def __init__(self, dateinfo: str, s_info: list[str]) -> None:
        # 2024 09 01 00 00  0.0000000  0 44
        self.date_str = list(filter(None, dateinfo.split(" ")))
        # print(self.date_str)
        self.date_year = int(self.date_str[0])
        self.date_month = int(self.date_str[1])
        self.date_day = int(self.date_str[2])
        self.date_hour = int(self.date_str[3])
        self.date_minute = int(self.date_str[4])
        self.date_second = int(float(self.date_str[5]))
        self.date_microsecond = int((float(self.date_str[5]) - self.date_second) * 1000000)
        self.date: datetime = datetime(self.date_year, self.date_month, self.date_day, self.date_hour, self.date_minute,
                                       self.date_second, self.date_microsecond)
        self.gpsWeek, self.gpsWIS = self.gps_NYR_WeekWIS(
            datetime(self.date_year, self.date_month, self.date_day, self.date_hour, self.date_minute,
                     self.date_second, self.date_microsecond))
        # self.time =time.mktime()
        self.epoch_flag = int(self.date_str[6])
        self.satellites_number = int(self.date_str[7])  # 卫星数量
        # self.satellites_observations: list[Satellite_observations] = [Satellite_observations(s) for s in s_info]

        self.GPS_observations = [GPS_Satellite_observations(s) for s in s_info if s[0] == "G"]
        self.BDS_observations = [BDS_Satellite_observations(s) for s in s_info if s[0] == "C"]
        self.Galileo_observations = [Galileo_Satellite_observations(s) for s in s_info if s[0] == "E"]
        self.GLONASS_observations = [GLONASS_Satellite_observations(s) for s in s_info if s[0] == "R"]

    def gps_NYR_WeekWIS(self, gpsNYR: datetime):
        gpsBeginUTC = datetime(1980, 1, 6, 0, 0, 0)
        interval = gpsNYR - gpsBeginUTC
        gpsWeek = int(interval.total_seconds() / (24 * 60 * 60))
        gpsWIS = interval.total_seconds() % (24 * 60 * 60)
        return gpsWeek, gpsWIS


class RINEX3_O:
    def __init__(self, filename) -> None:
        self.header = ""
        self.read_observation_file(filename)
        print("观测文件读取成功,文件名:" + filename)
        print("RINEX文件版本:" + self.RINEX_VERSION)

    def read_observation_file(self, filename):
        self.epochs: list[Epoch] = []
        dateinfo = ""
        s_info = []
        with open(filename, "r") as f:
            lines = f.readlines()
        is_header_data = True
        self.RINEX_VERSION = lines[0][0:18].strip()
        for line_str in lines:
            if is_header_data:
                self.header += line_str
                if "END OF HEADER" in line_str:
                    is_header_data = False
            else:
                if ">" in line_str:
                    dateinfo = line_str[2:-1]
                    n = int(dateinfo.split(" ")[-1])
                else:
                    s_info.append(line_str)
                    if len(s_info) == n:
                        self.epochs.append(Epoch(dateinfo, s_info))
                        dateinfo = ""
                        s_info = []


if __name__ == "__main__":
    r3 = RINEX3_O("../data/ABMF00GLP_R_20242450000_01D_30S_MO.rnx")
    print(r3.epochs[0].satellites_observations[0].PRN)
    print(r3.epochs[0].satellites_observations[0].pseudorange)
