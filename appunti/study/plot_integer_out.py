# -*- coding: utf-8 -*-
"""
Created on Sun Dec  3 09:35:16 2023

@author: luciamarock
"""

import numpy as np 
import matplotlib.pyplot as plt

outfile = "/home/luciamarock/Dropbox/shared/dev/PitchDetector/src/integer.out"
integer_file = "/home/luciamarock/Documents/AudioAnalyzer/scores/Prs/Fd185_integer.out"
attack = np.genfromtxt(outfile)
integer_out = np.genfromtxt(integer_file)
plt.plot(integer_out,color="black")
plt.plot(attack,"o",color="blue")
plt.show()