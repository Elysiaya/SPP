from RINEX_N import RINEX_N
from RINEX3_O import RINEX3_O
from GEO_eph import GEO_eph
import numpy as np
# rinex_n=RINEX_N("./data/BRDC00IGS_R_20242340000_01D_MN.rnx")
rinex_n=RINEX_N("./data/BRDC00IGS_R_20242340000_01D_MN.rnx")
block = rinex_n.df.iloc[0]
print(rinex_n.df)
# geo = GEO_eph(block)
# geo.Run()

# rinex_o = RINEX3_O("./data/ABMF00GLP_R_20242450000_01D_30S_MO.rnx")
# print(rinex_o.epochs[0].satellites_observations[0].pseudorange)


