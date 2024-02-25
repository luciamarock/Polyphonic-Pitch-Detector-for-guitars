# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 09:46:26 2023

@author: luciamarock
"""

import numpy as n 
from numpy import genfromtxt
import matplotlib.pyplot as plt

rtfi1 = "/home/luciamarock/Documents/AudioAnalyzer/scores/Ibanez/rtfi/45.out"
rtfi2 = "/home/luciamarock/Documents/AudioAnalyzer/scores/Ibanez/A110_filefilter.out"

datartfi1 = genfromtxt(rtfi1)
datartfi2 = genfromtxt(rtfi2)

datartfi1 = n.array(datartfi1)
datartfi2 = n.array(datartfi2)

# Enable interactive mode
plt.ion()

for i in range(len(datartfi2)):
    vectrtfi1 = datartfi1[i]
    vectrtfi2 = datartfi2[i]/170.
    plt.clf()
    plt.plot(vectrtfi1, linestyle='dashed')
    plt.plot(vectrtfi2, color='yellow')
    plt.pause(0.09)

# 170 