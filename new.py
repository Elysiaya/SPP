a = ["PRN", "Toc",  "SV_clock_bias", "SV_clock_drift",
                           "SV_clock_drift_rate", "IODE", "Crs", "Delta_n", "M0", "Cuc", "e_Eccentricity", "Cus",
                           "sqrt_A", "Toe_Time_of_Ephemeris", "Cic", "OMEGA0", "Cis", "i0", "Crc", "omega", "OMEGA_DOT",
                           "IDOT", "Codes_on_L2_channel", "GPS_Week", "L2_P_data_flag", "SV_accuracy", "SV_health",
                           "TGD1", "IODC", "Transmission_time_of_message","FI"]

from datetime import datetime

date = datetime.today()
print(str(date.year))