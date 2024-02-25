# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 10:19:53 2023

@author: luciamarock
"""
import os
import sys
import matplotlib.pyplot as plt
from numpy import genfromtxt

integer_file = "/home/luciamarock/Documents/AudioAnalyzer/scores/piano/"
allowance_files = "/home/luciamarock/Documents/AudioAnalyzer/scores/piano/Allowance/"
files = [f for f in os.listdir(allowance_files) if os.path.isfile(os.path.join(allowance_files, f))]
numbers = []
for allowance_file in files:
    temp = allowance_file.split(".")
    num = int(float(temp[0]))
    numbers.append(num)
prefixes = sorted(numbers)
for prefix in prefixes:
    current_integer = integer_file + str(prefix) + "_integer.out"
    current_allowance  = allowance_files + str(prefix) + ".out"

    env=genfromtxt(current_integer)
    allo=genfromtxt(current_allowance)
    
    
    plt.plot(env,color="black")
    plt.plot(allo,color="blue")
    plt.title(str(prefix))
    plt.show()