import matplotlib.pyplot as plt

def plto(x,y):
    plt.figure(figsize=(15,10),dpi=100)
    plt.title("SPP error")
    plt.xlabel("epochs")
    plt.ylabel("Delta_X(m)")
    plt.ylim((-20,20))
    plt.scatter(x,y,c="red",s=5)
    plt.savefig("./image/figure.png")