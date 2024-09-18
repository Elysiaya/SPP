import pandas
from datetime import datetime


class RINEX_N:
    def __init__(self, filename) -> None:
        self.header = ""
        self.df = pandas.DataFrame()

        data_start_lines = self.__get_data_start_lines(filename=filename)
        self.__get_data(data_start_lines)

        print("广播星历文件读取成功,文件名:" + filename)
        print("RINEX文件版本:" + self.RINEX_VERSION)

    # 获取数据的起始行
    def __get_data_start_lines(self, filename) -> int:
        # 定义数据的起始行
        data_start_lines = 1
        with open(file=filename, mode="r") as f:
            self.lines = f.readlines()
            self.RINEX_VERSION = self.lines[0][0:18].strip()
            for line in self.lines:
                self.header += line
                if "END OF HEADER" in line:
                    break
                data_start_lines += 1
            # print(data_start_lines)
        return data_start_lines

    def __get_data(self, data_start_lines):
        allzhen = []
        zhen = []
        h = 1
        i = data_start_lines
        # for i in range(data_start_lines,len(self.lines)):
        while i < len(self.lines):
            if self.lines[i][0] == "S" or self.lines[i][0] == "R":
                i += 4
                continue
            if h == 1:
                zhen.append(self.lines[i][0:3])
                y = int(self.lines[i][4:8])
                m = int(self.lines[i][9:11])
                d = int(self.lines[i][12:14])
                hour = int(self.lines[i][15:17])
                minute = int(self.lines[i][18:20])
                s = int(self.lines[i][21:23])
                zhen.append(datetime(year=y, month=m, day=d, hour=hour, minute=minute, second=s))

                # gpsWeek, gpsWIS = self.gps_NYR_WeekWIS(datetime(y, m, d, hour, minute, s))
                # zhen.append(gpsWeek)
                # zhen.append(gpsWIS)

                # zhen.append(int(self.lines[i][4:8]))
                # zhen.append(int(self.lines[i][9:11]))
                # zhen.append(int(self.lines[i][12:14]))
                # zhen.append(int(self.lines[i][15:17]))
                # zhen.append(int(self.lines[i][18:20]))
                # zhen.append(int(self.lines[i][21:23]))

                zhen.append(float(self.lines[i][23:42]))
                zhen.append(float(self.lines[i][42:61]))
                zhen.append(float(self.lines[i][61:80]))
            elif h != 1 and h != 8:
                if len(self.lines[i]) == 81:
                    zhen.append(float(self.lines[i][4:4 + 19]))
                    zhen.append(float(self.lines[i][4 + 19 * 1:4 + 19 * 2]))
                    zhen.append(float(self.lines[i][4 + 19 * 2:4 + 19 * 3]))
                    zhen.append(float(self.lines[i][4 + 19 * 3:4 + 19 * 4]))
                elif len(self.lines[i]) == 62:  # Galileo satellite可能出现数据缺失的情况
                    zhen.append(float(self.lines[i][4:4 + 19]))
                    zhen.append(float(self.lines[i][4 + 19 * 1:4 + 19 * 2]))
                    zhen.append(float(self.lines[i][4 + 19 * 2:4 + 19 * 3]))
                    zhen.append(0)

            if h == 8:
                # print(len(self.lines[i]))
                if len(self.lines[i]) == 81 or len(self.lines[i]) == 43:
                    zhen.append(float(self.lines[i][4:4 + 19]))
                    zhen.append(float(self.lines[i][4 + 19 * 1:4 + 19 * 2]))

                elif len(self.lines[i]) == 24:
                    zhen.append(float(self.lines[i][4:4 + 19]))
                    zhen.append(0)
                h = 0
                allzhen.append(zhen)
                zhen = []
            h += 1
            i += 1
        self.df = pandas.DataFrame(allzhen)
        self.df.columns = ["PRN", "Toc", "SV_clock_bias", "SV_clock_drift",
                           "SV_clock_drift_rate", "IODE", "Crs", "Delta_n", "M0", "Cuc", "e_Eccentricity", "Cus",
                           "sqrt_A", "Toe_Time_of_Ephemeris", "Cic", "OMEGA0", "Cis", "i0", "Crc", "omega", "OMEGA_DOT",
                           "IDOT", "Codes_on_L2_channel", "GPS_Week", "L2_P_data_flag", "SV_accuracy", "SV_health",
                           "TGD1", "IODC", "Transmission_time_of_message", "FI"]

    def writfile(self, output_filename):
        f = open(output_filename, "w")
        for line in self.df:
            for s in line:
                f.write(s)
                f.write(" ")
            f.write("\n")
        f.close()

    def print_header(self):
        print(self.header)

    def gps_NYR_WeekWIS(self, gpsNYR: datetime):
        gpsBeginUTC = datetime(1980, 1, 6, 0, 0, 0)
        interval = gpsNYR - gpsBeginUTC
        gpsWeek = int(interval.total_seconds() / (24 * 60 * 60))
        gpsWIS = int(interval.total_seconds() % (24 * 60 * 60))
        return gpsWeek, gpsWIS


if __name__ == "__main__":
    # h = header_data("ABPO00MDG_R_20240420000_01D_CN.rnx")
    r = RINEX_N("../data/BRDC00IGS_R_20242450000_01D_MN.rnx")
    # 提取所有GPS星历
    # print(r.df.loc[0:10,["PRN","Toc","SV_clock_bias","SV_clock_drift"]])
    print(r.df.loc[0]["PRN"])
