#float weightedSum = 0.0;
#float totalAmplitude = 0.0;
#for (int i = 0; i < NHARMS; i++) {
#    weightedSum += fc[i] * amplitude[i]; // Assuming 'amplitude' is the array storing amplitude values
#    totalAmplitude += amplitude[i];
#}
#float spectralCentroid = weightedSum / totalAmplitude;

import matplotlib.pyplot as plt
import numpy as np
from numpy import genfromtxt

arg3 = "./integer.out"
arg4="../scores/piano/Beat_It_cut_integer.out"

spc=genfromtxt(arg3)
env=genfromtxt(arg4)

spc = np.array(spc)
env = np.array(env)

plt.plot(env)
plt.plot(spc/5000.)
plt.show()
