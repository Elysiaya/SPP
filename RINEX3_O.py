class Epoch:
    #  C伪距;L载波;D多普勒;S信号强度
    # https://blog.csdn.net/Gou_Hailong/article/details/120911467
     def __init__(self,dateinfo:str,s_info:list[str]) -> None:
        # 2024 09 01 00 00  0.0000000  0 44
        self.date_str = list(filter(None,dateinfo.split(" ")))
        # print(self.date_str)
        self.date_year = int(self.date_str[0])
        self.date_month = int(self.date_str[1])
        self.date_day = int(self.date_str[2])
        self.date_hour = int(self.date_str[3])
        self.date_minute = int(self.date_str[4])
        self.date_second = float(self.date_str[5])
        self.epoch_flag = int(self.date_str[6])
        self.satellites_number = int(self.date_str[7]) # 卫星数量
        self.satellites_observations:list[Satellite_observations] = [Satellite_observations(s) for s in s_info]

class Satellite_observations:
    def __init__(self,o:str) -> None:
        temp = list(filter(None,o.split(" ")))
        self.PRN = temp[0]
        self.pseudorange = float(temp[1])
class RINEX3_O:
    def __init__(self,filename) -> None:
        self.header = ""
        self.read_observation_file(filename)
        print("观测文件读取成功,文件名:"+filename)
        print("RINEX文件版本:"+self.RINEX_VERSION)

    def read_observation_file(self,filename):
        self.epochs:list[Epoch]=[]
        dateinfo = ""
        s_info=[]
        with open(filename,"r") as f:
            lines = f.readlines()
        is_header_data=True
        self.RINEX_VERSION=lines[0][0:18].strip()
        for line_str in lines:
            if is_header_data:
                self.header+=line_str
                if "END OF HEADER" in line_str:
                     is_header_data=False
            else:
                if ">" in line_str:
                    dateinfo=line_str[2:-1]
                    n = int(dateinfo.split(" ")[-1])
                else:
                     s_info.append(line_str)
                     if len(s_info)==n:
                        self.epochs.append(Epoch(dateinfo,s_info))
                        dateinfo = ""
                        s_info=[]
if __name__ =="__main__":
    r3 = RINEX3_O("./data/ABMF00GLP_R_20242450000_01D_30S_MO.rnx")
    print(r3.epochs[0].satellites_observations[0].PRN)
    print(r3.epochs[0].satellites_observations[0].pseudorange)


