import numpy as n 
from numpy import genfromtxt
import matplotlib.pyplot as plt

fft1 = "/home/luciamarock/Documents/AudioAnalyzer/scores/Ibanez/fft/45.out"
fft2 = "/home/luciamarock/Documents/AudioAnalyzer/scores/Ibanez/A110_filefft.out"

datafft1 = genfromtxt(fft1)
datafft2 = genfromtxt(fft2)

datafft1 = n.array(datafft1)
datafft2 = n.array(datafft2)

# Enable interactive mode
plt.ion()

for i in range(len(datafft2)):
    vectfft1 = datafft1[i]
    vectfft2 = datafft2[i]*3.75
    plt.clf()
    plt.plot(vectfft1, linestyle='dashed')
    plt.plot(vectfft2, color='yellow')
    plt.pause(0.09)

