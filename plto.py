import matplotlib.pyplot as plt

def plto(x,y):
    plt.figure(figsize=(10,7),dpi=100)
    plt.grid(True)

    plt.title("SPP error")
    plt.xlabel("epochs")
    plt.ylabel("Delta_X(m)")
    plt.ylim((-20,20))
    plt.scatter(x,y,c="red",s=5)
    plt.savefig("figure.png")