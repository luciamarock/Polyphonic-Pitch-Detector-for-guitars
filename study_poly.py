# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 11:02:13 2024

@author: luciamarock
"""
import os 
import sys 
import json
import numpy as np
import python.plots as plotters

filename = "/home/luciamarock/Dropbox/shared/dev/PitchDetector/appunti/study/piano_poly.json"
if not os.path.isfile(filename):
    print("creating")
    scores_base_path = "/home/luciamarock/Documents/AudioAnalyzer/scores/piano/Poly/"
    items = os.listdir(scores_base_path)
    polydict = {}
    for item in items:
        polydict[item] = []
        feature_path = scores_base_path + item + os.path.sep
        polyfiles = os.listdir(feature_path)
        for polyfile in polyfiles:
            item_path = os.path.join(feature_path, polyfile)
            polydict[item].append(item_path)

    with open(filename, 'w') as json_file:
        json.dump(polydict, json_file, indent=2)
        json_file.close()
else:
    print("loading ...")
    with open(filename, 'r') as IF:
        polyfiles = json.load(IF)
        IF.close()

filename = "/home/luciamarock/Dropbox/shared/dev/PitchDetector/appunti/study/piano_data.json"
with open(filename, 'r') as DF:
    monofiles = json.load(DF)
    DF.close()

mono_base_path = "/home/luciamarock/Documents/AudioAnalyzer/scores/piano/"
for item in monofiles["Allowance"]:
    filename = os.path.basename(item)
    allowance_file = mono_base_path + "Allowance" + os.path.sep + filename 
    fft_file = mono_base_path + "FFTs" + os.path.sep + filename 
    periodicity_file = mono_base_path + "Periodicity" + os.path.sep + filename
    rtfi_file = mono_base_path + "RTFIs" + os.path.sep + filename
    centroid_file = mono_base_path + "SpectralCentroid" + os.path.sep + filename
    matches_file = mono_base_path + "topMatches" + os.path.sep + filename 
    dataRTFI = np.genfromtxt(rtfi_file)
    dataFFT = np.genfromtxt(fft_file)
    allowance = np.genfromtxt(allowance_file)
    periodicity = np.genfromtxt(periodicity_file)
    topMatches = np.genfromtxt(matches_file) 
    spectralCentroid = np.genfromtxt(centroid_file)
    print("    loaded {}".format(filename))

poly_base_path = "/home/luciamarock/Documents/AudioAnalyzer/scores/piano/Poly/"
for item in polyfiles["Allowance"]:
    filename = os.path.basename(item)
    allowance_file = poly_base_path + "Allowance" + os.path.sep + filename 
    fft_file = poly_base_path + "FFTs" + os.path.sep + filename 
    periodicity_file = poly_base_path + "Periodicity" + os.path.sep + filename
    rtfi_file = poly_base_path + "RTFIs" + os.path.sep + filename
    centroid_file = poly_base_path + "SpectralCentroid" + os.path.sep + filename
    matches_file = poly_base_path + "topMatches" + os.path.sep + filename 
    dataRTFI = np.genfromtxt(rtfi_file)
    dataFFT = np.genfromtxt(fft_file)
    allowance = np.genfromtxt(allowance_file)
    periodicity = np.genfromtxt(periodicity_file)
    topMatches = np.genfromtxt(matches_file) 
    spectralCentroid = np.genfromtxt(centroid_file)
    print("    loaded {}".format(filename))

sys.exit()
#TODO use LogicPiano 
plotters.continuous_plot(instrument, fft_file, centroid_file,matches_file,rtfi_file,periodicity_file,allowance_file)