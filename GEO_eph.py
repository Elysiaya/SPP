import datetime
import math
import numpy as np
import pandas as pd


class GEO_eph:
    def __init__(self, DataBlock: list) -> None:
        # SV /EPOCH / SV CLK
        # 卫星编号
        self.PRN = DataBlock[0]
        # 星历参考时间 年
        self.Time_year = DataBlock[1]
        # 星历参考时间 月
        self.Time_month = DataBlock[2]
        # 星历参考时间 日
        self.Time_day = DataBlock[3]
        # 星历参考时间 时
        self.Time_hour = DataBlock[4]
        # 星历参考时间 分
        self.Time_minute = DataBlock[5]
        # 星历参考时间 秒
        self.Time_second = DataBlock[6]
        # 卫星钟差 单位秒
        self.SV_clock_bias = DataBlock[7]
        # 卫星钟漂移 单位sec
        self.SV_clock_drift = DataBlock[8]
        # 卫星钟漂变化率 单位sec/sec2
        self.SV_clock_drift_rate = DataBlock[9]

        # BROADCAST ORBIT – 1
        self.AODE = DataBlock[10]
        self.Crs = -DataBlock[11]
        self.Delta_n = DataBlock[12]
        self.M0 = DataBlock[13]

        # BROADCAST ORBIT – 2
        self.Cuc = DataBlock[14]
        self.e_Eccentricity = DataBlock[15]  # 偏心率 e
        self.Cus = DataBlock[16]
        self.sqrt_A = DataBlock[17]

        # BROADCAST ORBIT – 3
        self.Toe_Time_of_Ephemeris = DataBlock[18]
        self.Cic = DataBlock[19]
        self.OMEGA0 = DataBlock[20]
        self.Cis = DataBlock[21]

        # BROADCAST ORBIT – 4
        self.i0 = DataBlock[22]
        self.Crc = DataBlock[23]
        self.omega = DataBlock[24]
        self.OMEGA_DOT = DataBlock[25]

        # BROADCAST ORBIT – 5
        self.IDOT = DataBlock[26]
        self.Spare = DataBlock[27]
        self.BDT_Week = DataBlock[28]
        self.Spare = DataBlock[29]

        # BROADCAST ORBIT – 6
        self.SV_accuracy = DataBlock[30]
        self.SatH1 = DataBlock[31]
        self.TGD1 = DataBlock[32]
        self.TGD2 = DataBlock[33]

        # BROADCAST ORBIT – 7
        self.Transmission_time_of_message = DataBlock[34]
        self.AODC = DataBlock[35]

        # 判断卫星类型
        BDS_information = pd.read_csv("./data/北斗卫星信息.csv")
        # print(BDS_information)
        BDS_information.set_index("PRN", inplace=True)
        prn = self.PRN[1:3]
        self.SVN = BDS_information.loc[int(prn), "SVN"]

    # 年月日转换为周内秒
    def __to_Toc(self, year: int, month: int, day, hour: int) -> int:
        weekday = datetime.datetime(year, month, day).weekday()
        return (weekday + 1) * 24 * 3600 + hour * 3600

    def Run(self, Tsv=601201):

        # WGS-84基本参数
        A = 6378137  # 基准椭球体长半径（m）
        F = 1 / 298.257223563  # 基准椭球体扁率
        Radv = 7.2921151467e-5  # 地球自转角速度（rad/s）
        GM = 3.986005e14  # 地球引力常数GM（m^3/s^2）
        C = 2.99792458e8  # 真空中的光速（m/s）

        # 修正Tsv的卫星钟偏
        Toc = self.__to_Toc(self.Time_year, self.Time_month, self.Time_day, self.Time_hour)
        Toe = Toc  # Toe与Toc时间同步
        Delta_t = Tsv - Toc
        sat_clk_error = self.SV_clock_drift_rate * math.pow(Delta_t,
                                                            2) + self.SV_clock_drift * Delta_t + self.SV_clock_bias - self.TGD1
        Tsv = Tsv - sat_clk_error

        # 计算规划时间，Tk等于发射时刻与参考时刻的时间差
        Tk = Tsv - Toe

        # 计算平近点角
        a = self.sqrt_A ** 2  # 轨道长半轴
        n = math.sqrt(GM / a ** 3) + self.Delta_n  #平均角速度
        M = self.M0 + n * Tk

        # 迭代求解偏近点角
        E0 = M
        while True:
            E = M + self.e_Eccentricity * math.sin(E0)
            Delta_E = E - E0
            if abs(Delta_E) < 1e-12:
                break
            else:
                E0 = E
        # 将E化为[0,2pi]区间
        while True:
            if E < 0:
                E = E + 2 * math.pi
            elif E > 2 * math.pi:
                E = E - 2 * math.pi

            if E > 0 and E < 2 * math.pi:
                break

        # 求解真近点角和升交点角距
        nu = math.atan2(math.sqrt(1 - self.e_Eccentricity ** 2) * math.sin(E), (math.cos(E) - self.e_Eccentricity))
        phi = nu + self.omega

        # 轨道参数计算，并考虑摄动改正项
        Delta_u = self.Cuc * math.cos(2 * phi) + self.Cus * math.sin(2 * phi)
        Delta_r = self.Crc * math.cos(2 * phi) + self.Crs * math.sin(2 * phi)
        Delta_i = self.Cic * math.cos(2 * phi) + self.Cis * math.sin(2 * phi)

        u = phi + Delta_u
        r = a * (1 - self.e_Eccentricity * math.cos(E)) + Delta_r
        i = self.i0 + self.IDOT * Tk + Delta_i

        # GEO卫星
        if self.SVN.split('-')[0] == "GEO":
            # 升交点赤经
            omega = self.OMEGA0 + self.OMEGA_DOT * Tk - Radv * Toe
            # 计算Tsv时刻的卫星位置
            X = math.cos(u) * r * math.cos(omega) - math.sin(u) * r * math.cos(i) * math.sin(omega)
            Y = math.cos(u) * r * math.sin(omega) + math.sin(u) * r * math.cos(i) * math.cos(omega)
            Z = math.sin(u) * r * math.sin(i)

            f = -5 / 180 * math.pi
            p = Radv * Tk

            Rx = np.array([[1, 0, 0], [0, math.cos(f), math.sin(f)], [0, -math.sin(f), math.cos(f)]], dtype=np.float64)
            Rz = np.array([[math.cos(p), math.sin(p), 0], [-math.sin(p), math.cos(p), 0], [0, 0, 1]], dtype=np.float64)

            XYZ = Rx @ Rz @ np.array([X, Y, Z]).T
            print(self.SVN.split('-')[0] + "卫星位置", XYZ.tolist())
            return XYZ.tolist()
        # MEO/IGSO卫星
        elif self.SVN.split('-')[0] == "MEO" or self.SVN.split('-')[0] == "IGSO":
            # 升交点赤经
            omega = self.OMEGA0 + (self.OMEGA_DOT - Radv) * Tk - Radv * Toe
            # 计算Tsv时刻的卫星位置
            X = math.cos(u) * r * math.cos(omega) - math.sin(u) * r * math.cos(i) * math.sin(omega)
            Y = math.cos(u) * r * math.sin(omega) + math.sin(u) * r * math.cos(i) * math.cos(omega)
            Z = math.sin(u) * r * math.sin(i)

            print(self.SVN.split('-')[0] + "卫星位置", [X, Y, Z])
            return [X, Y, Z]
