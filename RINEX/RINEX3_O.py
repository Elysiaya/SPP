from datetime import datetime
import math
import pandas
import os.path
class RINEX3_O:
    def __init__(self, filename) -> None:
        # 获取文件名
        basename = os.path.basename(filename)
        # 获取测站
        self.observation_station_name = basename[0:4]
        # 获取年、年纪日
        self.year = int(basename[12:16])
        self.doy = int(basename[16:19])


        self.header = ""
        self.APPROX_POSITION = None
        self.RINEX_VERSION: str = ""

        # 存储数据
        # self.df=[]
        self.gps_obs_list = []
        self.beidou_obs_list = []
        self.galileo_obs_list = []
        self.glonass_obs_list = []

        # 存储观测值类型
        self.GPS_OBS_TYPE = []
        self.BeiDou_OBS_TYPE = []
        self.Galileo_OBS_TYPE = []
        self.GLONASS_OBS_TYPE = []

        cache_path = os.path.join("cache")
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)
            self.read_observation_file(filename)

            self.gps_df = pandas.DataFrame(self.gps_obs_list, columns=["PRN", "Time"] + self.GPS_OBS_TYPE)
            self.beidou_df = pandas.DataFrame(self.beidou_obs_list, columns=["PRN", "Time"] + self.BeiDou_OBS_TYPE)
            self.galileo_df = pandas.DataFrame(self.galileo_obs_list, columns=["PRN", "Time"] + self.Galileo_OBS_TYPE)
            self.glonass_df = pandas.DataFrame(self.glonass_obs_list, columns=["PRN", "Time"] + self.GLONASS_OBS_TYPE)

            self.gps_df.to_hdf(os.path.join(cache_path,basename.split('.')[0]+".h5"),mode="a",key="gps")
            self.beidou_df.to_hdf(os.path.join(cache_path,basename.split('.')[0]+".h5"),mode="a",key="beidou")
            self.galileo_df.to_hdf(os.path.join(cache_path,basename.split('.')[0]+".h5"),mode="a",key="galileo")
            self.glonass_df.to_hdf(os.path.join(cache_path,basename.split('.')[0]+".h5"),mode="a",key="glonass")
        else:
            self.gps_df = pandas.read_hdf(os.path.join(cache_path,basename.split('.')[0]+".h5"),key="gps")
            self.beidou_df = pandas.read_hdf(os.path.join(cache_path,basename.split('.')[0]+".h5"),key="beidou")
            self.galileo_df = pandas.read_hdf(os.path.join(cache_path,basename.split('.')[0]+".h5"),key="galileo")
            self.glonass_df = pandas.read_hdf(os.path.join(cache_path,basename.split('.')[0]+".h5"),key="glonass")
        print("观测文件读取成功,文件名:" + basename)
        print("RINEX文件版本:" + self.RINEX_VERSION)
        print("="*70)

    def read_observation_file(self, filename):
        with open(filename, "r") as f:
            lines = f.readlines()
        is_header_data = True
        self.RINEX_VERSION = lines[0][0:18].strip()
        error_flag_line = 0
        for line_str in lines:
            # 头文件
            if is_header_data:
                self.header += line_str
                # 获取头文件中的大致坐标
                if "APPROX POSITION" in line_str:
                    self.APPROX_POSITION = list(filter(None, line_str.split(" ")))[0:3]
                    self.APPROX_POSITION = [float(i) for i in self.APPROX_POSITION]

                # 获取观测值类型
                if "SYS / # / OBS TYPES" in line_str:
                    # 第一行
                    if line_str[0] == "G" or line_str[0] == "E" or line_str[0] == "C" or line_str[0] == "R":
                        satellite_type = line_str[0]
                        obs_number = int(line_str[4:6])
                        obstypelines = math.ceil(obs_number / 13)
                        current_ln = 1
                        if obs_number > 13:
                            ot = line_str[7:58].split(" ")
                        else:
                            ot = line_str[7:4 * obs_number - 1 + 7].split(" ")
                        current_ln += 1
                        continue
                    # 其他行 
                    if current_ln != 1:
                        if obs_number >= current_ln * 13:
                            ot = ot + line_str[7:58].split(" ")
                            current_ln += 1
                            continue
                        else:
                            ot = ot + line_str[7:4 * (obs_number - 13 * (current_ln - 1)) - 1 + 7].split(" ")
                        if current_ln == obstypelines:
                            if satellite_type == "G":
                                self.GPS_OBS_TYPE = ot
                            elif satellite_type == "C":
                                self.BeiDou_OBS_TYPE = ot
                            elif satellite_type == "E":
                                self.Galileo_OBS_TYPE = ot
                            elif satellite_type == "R":
                                self.GLONASS_OBS_TYPE = ot
                            current_ln = 1
                            continue

                if "END OF HEADER" in line_str:
                    is_header_data = False
            # 数据文件
            else:
                # 数据文件的文件头
                if ">" in line_str:
                    # "> 2024 09 20 00 31 00.0000000  0 60       -.000171399986"
                    dateinfo = line_str
                    # n为数据行数
                    n = int(line_str[33:35])
                    # 卫星状态码,0为正常，其他为不正常
                    code = int(dateinfo[31:32])
                    if code != 0:
                        error_flag_line = n
                        continue
                else:
                    # 遇到错误代码的处理方式
                    if error_flag_line != 0:
                        error_flag_line -= 1
                        continue

                    if line_str[0][0] == "C":
                        self.beidou_obs_list.append(self.format_one_line(line_str, dateinfo))
                    elif line_str[0][0] == "E":
                        self.galileo_obs_list.append(self.format_one_line(line_str, dateinfo))
                    elif line_str[0][0] == "G":
                        self.gps_obs_list.append(self.format_one_line(line_str, dateinfo))
                    elif line_str[0][0] == "R":
                        self.glonass_obs_list.append(self.format_one_line(line_str, dateinfo))

    @staticmethod
    def format_one_line(line: str, dateinfo) -> list:
        # "> 2024 09 20 00 31 00.0000000  0 60       -.000171399986"
        dateinfo = dateinfo[2:29]
        l = []
        temp_date_str = list(filter(None, dateinfo.split(" ")))
        obs_date = datetime(int(temp_date_str[0]), int(temp_date_str[1]), int(temp_date_str[2]), int(temp_date_str[3]),
                            int(temp_date_str[4]), int(temp_date_str[5][0:2]),
                            int((float(temp_date_str[5]) - int(temp_date_str[5][0:2])) * 1000000)
                            )
        l.append(line[0:3])
        l.append(obs_date)
        start_l = 5
        while start_l < len(line):
            u = line[start_l:start_l + 13]
            if u != "             ":
                l.append(float(u))
            else:
                l.append(None)
            start_l += 16
        return l


if __name__ == "__main__":
    r3 = RINEX3_O("./data/O/WUH200CHN_R_20242640000_01D_30S_MO.rnx")
