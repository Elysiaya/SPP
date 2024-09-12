from RINEX_N import RINEX_N
from RINEX3_O import RINEX3_O
from GPS_satellite_orbit import GPS_satellite_orbit
import datetime

rinex_n = RINEX_N("./data/BRDC00IGS_R_20242450000_01D_MN.rnx")
rinex_o = RINEX3_O("./data/ABMF00GLP_R_20242450000_01D_30S_MO.rnx")
GPS_Ephemeris = rinex_n.df[rinex_n.df.loc[:, "PRN"].str[0] == "G"]

# 获取当前观测值历元的观测时间，在广播星历中筛选出
e = 1
GPS_observations_date = rinex_o.epochs[e].date
print(f"GPS observations date: {GPS_observations_date}")
# print(GPS_Ephemeris)
# 定义筛选范围为前后一个小时
s_date = GPS_observations_date - datetime.timedelta(hours=1)
e_date = GPS_observations_date + datetime.timedelta(hours=1)
cond = (GPS_Ephemeris.loc[:, "Toc"] >= s_date) & (GPS_Ephemeris.loc[:, "Toc"] <= e_date)

GPS_Ephemeris = GPS_Ephemeris[cond].reset_index(drop=True)
# print(GPS_Ephemeris.loc[0].tolist())
for column_name,GPS_Ephemeris_single in GPS_Ephemeris.iterrows():
    GEO = GPS_satellite_orbit(GPS_Ephemeris_single.tolist())
    GEO.Run(GPS_observations_date)
