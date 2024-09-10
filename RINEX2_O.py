class RINEX2_O:
    def __init__(self,filename) -> None:
        self.header=""
        self.read_observation_file(filename=filename)

    def read_observation_file(self,filename):
        # 定义数据的起始行
        start_lines = 1
        with open(file=filename,mode="r") as f:
            self.lines = f.readlines()
            self.RINEX_VERSION=self.lines[0][0:18].strip()
            for line in self.lines:
                self.header+=line
                if "END OF HEADER" in line:
                    break
                start_lines+=1
                
        epoch_start_lines=start_lines
        self.epochs:list[epoch]=[]
        while True:
            line1=list(filter(None,self.lines[epoch_start_lines].split(" ")))
            Number_of_satellites=int(line1[7][0:2])
            if Number_of_satellites<=12:
                epoch_end_lines=epoch_start_lines+2*Number_of_satellites+1
            if Number_of_satellites>12:
                epoch_end_lines=epoch_start_lines+2*Number_of_satellites+2
                line1[7]=line1[7][0:-1]+self.lines[epoch_start_lines+1].strip()

            all_data=[]
            h=epoch_start_lines+1
            if Number_of_satellites<=12:
                    pass
            if Number_of_satellites>12:
                    h=h+1
            while h<epoch_end_lines:           
                # print(h)
                # temp=list(filter(None,self.lines[h][0:-1].split(' ')))+list(filter(None,self.lines[h+1][0:-1].split(' ')))
                temp=[]
                temp.append(self.lines[h][0:-1]+self.lines[h+1][0:-1])
                all_data.append(temp)
                h=h+2

            
            self.epochs.append(epoch(line1,all_data))
            epoch_start_lines=epoch_end_lines
            if epoch_end_lines==len(self.lines):
                 break
            
        print("观测文件读取成功,文件名:"+filename)
        print("RINEX文件版本:"+self.RINEX_VERSION)


     


class epoch:
    def __init__(self,line:list,data:list) -> None:
        # print(line)
        self.year=int(line[0])
        self.month=int(line[1])
        self.day=int(line[2])
        self.hour=int(line[3])
        self.minute=int(line[4])
        self.second=float(line[5])
        self.flag=int(line[6])
        self.Number_of_satellites=int(line[7][0:2])
        self.PRNs=[]
        for i in range(2,len(line[7][0:-1]),3):
            self.PRNs.append(line[7][i:i+3])
        # print(self.Number_of_satellites)
        self.data = []
        for i,d in enumerate(data):
             self.data.append([self.PRNs[i]]+d)


if __name__ =="__main__":
    rinex_o = RINEX2_O("./data/bjfs2340.24o")
    # print(rinex_o.epochs[-1].data)
    # for i in rinex_o.epochs[-1].data:
    #      print(i)