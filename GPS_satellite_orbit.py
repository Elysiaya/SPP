from datetime import datetime
import math


class GPS_satellite_orbit:
    def __init__(self, DataBlock: list) -> None:
        self.satellite_position = None

        # SV /EPOCH / SV CLK
        # 卫星编号
        self.PRN = DataBlock[0]

        self.Toc = DataBlock[1]
        # 卫星钟差 单位秒
        self.SV_clock_bias = DataBlock[2]
        # 卫星钟漂移 单位sec
        self.SV_clock_drift = DataBlock[3]
        # 卫星钟漂变化率 单位sec/sec2
        self.SV_clock_drift_rate = DataBlock[4]

        # BROADCAST ORBIT – 1
        self.IODE = DataBlock[5]
        self.Crs = -DataBlock[6]
        self.Delta_n = DataBlock[7]
        self.M0 = DataBlock[8]

        # BROADCAST ORBIT – 2
        self.Cuc = DataBlock[9]
        self.e_Eccentricity = DataBlock[10]  # 偏心率 e
        self.Cus = DataBlock[11]
        self.sqrt_A = DataBlock[12]

        # BROADCAST ORBIT – 3
        self.Toe_Time_of_Ephemeris = DataBlock[13]  #sec of GPS week
        self.Cic = DataBlock[14]
        self.OMEGA0 = DataBlock[15]
        self.Cis = DataBlock[16]

        # BROADCAST ORBIT – 4
        self.i0 = DataBlock[17]
        self.Crc = DataBlock[18]
        self.omega = DataBlock[19]
        self.OMEGA_DOT = DataBlock[20]

        # BROADCAST ORBIT – 5
        self.IDOT = DataBlock[21]
        self.Codes_on_L2_channel = DataBlock[22]
        self.GPS_Week = DataBlock[23]  # GPS周
        self.L2_P_data_flag = DataBlock[24]

        # BROADCAST ORBIT – 6
        self.SV_accuracy = DataBlock[25]
        self.SV_health = DataBlock[26]
        self.TGD = DataBlock[27]
        self.IODC = DataBlock[28]

        # BROADCAST ORBIT – 7
        self.Transmission_time_of_message = DataBlock[29]
        self.FI = DataBlock[30]

    def NYR2GPST(self, t: datetime) -> float:
        """
        年月日转GPS时，注意二者都应该在GPS时间系统下，该函数未考虑闰秒情况
        :param t:
        :return:
        """
        GPST_start_date = datetime(1980, 1, 6)
        delta_t = t - GPST_start_date
        return delta_t.total_seconds()

    def Run(self, t: datetime, psi):
        """
        Run the satellite orbit
        :param psi: 伪距，用于计算发射时间
        :param t: 接收机时刻(GPST)
        :return:
        """

        # WGS-84基本参数
        A = 6378137  # 基准椭球体长半径（m）
        F = 1 / 298.257223563  # 基准椭球体扁率
        Radv = 7.2921151467e-5  # 地球自转角速度（rad/s）
        GM = 3.986005e14  # 地球引力常数GM（m^3/s^2）
        C = 2.99792458e8  # 真空中的光速（m/s）
        # print(f"GPS接收机时刻:{t}")
        # print(f"GPS星历时刻:{self.Toc}")
        # 接收机时刻转换为GPS时，单位秒
        t = self.NYR2GPST(t)

        Toe = self.Toe_Time_of_Ephemeris + self.GPS_Week*7*24*3600  # Toe与Toc时间同步
        Delta_t = t - Toe
        self.sat_clk_error = self.SV_clock_drift_rate * math.pow(Delta_t,
                                                                 2) + self.SV_clock_drift * Delta_t + self.SV_clock_bias - self.TGD
        TSV = t - self.sat_clk_error - psi / C
        # TSV = t - self.sat_clk_error

        # 计算规划时间，Tk等于发射时刻与参考时刻的时间差
        Tk = TSV - Toe

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

            if 0 < E < 2 * math.pi:
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
        # 升交点赤经
        omega = self.OMEGA0 + (self.OMEGA_DOT - Radv) * Tk - Radv * (Toe-self.GPS_Week*7*24*3600)
        # 计算Tsv时刻的卫星位置
        X = math.cos(u) * r * math.cos(omega) - math.sin(u) * r * math.cos(i) * math.sin(omega)
        Y = math.cos(u) * r * math.sin(omega) + math.sin(u) * r * math.cos(i) * math.cos(omega)
        Z = math.sin(u) * r * math.sin(i)

        # print(f"{self.PRN}卫星在{Tsv}秒位置", [X, Y, Z])
        self.satellite_position = [X, Y, Z]
