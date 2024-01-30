# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 11:02:13 2024

@author: luciamarock
"""
import os 
import sys 
import python.plots as plotters

instrument = "piano"
filename = "55_59_62_72.out"

if instrument == "piano":
    scores_base_path = "/home/luciamarock/Documents/AudioAnalyzer/scores/piano/Poly/"
else:
    sys.exit()

allowance_file = scores_base_path + "Allowance" + os.path.sep + filename 
fft_file = scores_base_path + "FFTs" + os.path.sep + filename 
periodicity_file = scores_base_path + "Periodicity" + os.path.sep + filename
rtfi_file = scores_base_path + "RTFIs" + os.path.sep + filename
centroid_file = scores_base_path + "SpectralCentroid" + os.path.sep + filename
matches_file = scores_base_path + "topMatches" + os.path.sep + filename 

plotters.continuous_plot(instrument, fft_file, centroid_file,matches_file,rtfi_file,periodicity_file,allowance_file)