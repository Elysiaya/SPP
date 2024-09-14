a = ["PRN", "Toc", "SV_clock_bias", "SV_clock_drift",
     "SV_clock_drift_rate", "IODE", "Crs", "Delta_n", "M0", "Cuc", "e_Eccentricity", "Cus",
     "sqrt_A", "Toe_Time_of_Ephemeris", "Cic", "OMEGA0", "Cis", "i0", "Crc", "omega", "OMEGA_DOT",
     "IDOT", "Codes_on_L2_channel", "GPS_Week", "L2_P_data_flag", "SV_accuracy", "SV_health",
     "TGD1", "IODC", "Transmission_time_of_message", "FI"]

from datetime import datetime

date = datetime.today()
print(str(date.year))


def to_Toc(year: int, month: int, day, hour: int, minute: int, second: float) -> float:
    """
    datatime对象转换为周内秒
    :param year:
    :param month:
    :param day:
    :param hour:
    :param minute:
    :param second:
    :return:
    """
    weekday = (datetime(year, month, day).weekday() + 1) % 7
    t = weekday * 24 * 3600 + hour * 3600 + minute * 60 + second
    return t


t = to_Toc(2024, 9, 1, 0, 0, second=0)
print(t)


def NYR2GPST(t: datetime) -> float:
    """
    年月日转GPS时，注意二者都应该在GPS时间系统下，该函数未考虑闰秒情况
    :param t:
    :return:
    """
    GPST_start_date = datetime(1980, 1, 6)
    delta_t = t - GPST_start_date
    return delta_t.total_seconds()

"""
G01 2024 09 01 02 00 00 2.087550237775E-04-8.981260180008E-12 0.000000000000E+00
     1.700000000000E+01 6.406250000000E+00 6.675635209859E-09 1.072107051345E+00
     4.563480615616E-07 1.339385216124E-02 4.759058356285E-06 5.153602550507E+03
     7.200000000000E+03-1.825392246246E-07-1.809351307316E+00 1.713633537292E-07
     9.534384648934E-01 2.874375000000E+02 1.034861238970E+00-8.654646215040E-09
    -7.357449324439E-11 1.000000000000E+00 2.330000000000E+03 0.000000000000E+00
     2.800000000000E+00 6.300000000000E+01-1.955777406693E-08 1.700000000000E+01
     1.800000000000E+01 4.000000000000E+00
"""

t2 = NYR2GPST(datetime(2024, 9, 1, 2))
print(2.330000000000E+03*7*24*3600+7.200000000000E+03)
print(t2)
