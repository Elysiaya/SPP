from RINEX_N import RINEX_N
from RINEX3_O import RINEX3_O
import pandas
import datetime
from GEO_eph import GEO_eph
import numpy as np





# rinex_n=RINEX_N("./data/BRDC00IGS_R_20242340000_01D_MN.rnx")
rinex_n = RINEX_N("./data/BRDC00IGS_R_20242450000_01D_MN.rnx")
rinex_o = RINEX3_O("./data/ABMF00GLP_R_20242450000_01D_30S_MO.rnx")
GPS_Ephemeris = rinex_n.df[rinex_n.df[0].str[0] == "G"]
GPS_observations = rinex_o.epochs[0].GPS_observations
# print(GPS_Ephemeris)
# cond = (GPS_Ephemeris[4] <= rinex_o.epochs[0].date_hour + 1) & (GPS_Ephemeris[4] >= rinex_o.epochs[0].date_hour - 1)
#
# cond2 = gps_NYR_WeekWIS(GPS_Ephemeris[4])[1] - gps_NYR_WeekWIS(rinex_o.epochs[0].date)[1] <= 3600
e = 1000
print(rinex_o.epochs[e].gpsWIS)
print(rinex_o.epochs[e].gpsWeek)
print(len(rinex_o.epochs))


cond3 = (abs(GPS_Ephemeris[2]-rinex_o.epochs[e].gpsWIS) <= 3600) & (GPS_Ephemeris[1] == rinex_o.epochs[e].gpsWeek)

GPS_Ephemeris = GPS_Ephemeris[cond3]

print(GPS_Ephemeris)

