import numpy as n 
from numpy import genfromtxt
import matplotlib.pyplot as plt

arg1 = "./process_durations.txt"

data = genfromtxt(arg1)
data = n.array(data)
data = data / 1000000. 

plt.plot(data,"o")
plt.ylabel("milliseconds")
plt.xlabel("frame number")
plt.show()

