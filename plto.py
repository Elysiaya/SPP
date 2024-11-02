import matplotlib.pyplot as plt

def plto(x,y):
    plt.xlabel("epochs")
    plt.ylabel("Delta(m)")
    plt.ylim((-10,10))
    plt.scatter(x,y,c="red",s=5)
    plt.show()