# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 12:19:33 2023

@author: luciamarock
"""

# this script performs analysis, tests and eventually parameters estimation 
import os 
import sys
import re
import json
import numpy as np
import matplotlib.pyplot as plt
import python.utilFunctions as UF
import python.plots as plotters
import python.analyzer as analyze

if len(sys.argv) < 2:
    print("Usage: python study.py <instrument> (guitar or piano), + plot if plotting only")
    sys.exit()

instrument = sys.argv[1]

working_dir = os.getcwd()
scores_root = "/home/luciamarock/Documents/AudioAnalyzer/scores/"
notes_file = working_dir + os.path.sep + "algo_outputs" + os.path.sep + "notes_" + instrument + ".txt"
info_file = working_dir + os.path.sep + "resources" + os.path.sep + "note_struct.json"
if os.path.isfile(notes_file) and os.path.isfile(info_file):
    notes_array = np.genfromtxt(notes_file)
    MIDI_array = UF.freq_to_MIDI(notes_array,instrument)
    names_array = []
    with open(info_file, 'r') as IF:
        data = json.load(IF)
        IF.close()
    for note in MIDI_array:
        key = str(note)
        names_array.append(data[key]["name"])
else:
    sys.exit()

# at this point we have notes_array, MIDI_array and names_array
if len(sys.argv) > 2:
    plt.plot(MIDI_array, notes_array,"o")
    for i, label in enumerate(names_array):
        plt.annotate(label, (MIDI_array[i], notes_array[i]), textcoords="offset points", xytext=(0, 10), ha='center')
    plt.xlabel('MIDI numbers')
    plt.ylabel('Frequencies')
    plt.title(instrument + " note visualization")
    plt.show()
    sys.exit()

if instrument == "piano":
    features_dir = scores_root + instrument + os.path.sep
    items = os.listdir(features_dir)
    features = []
    for item in items:
        item_path = os.path.join(features_dir, item)
        if not os.path.isfile(item_path):
            features.append(item)
    allowance_files = scores_root + instrument + os.path.sep + "Allowance" + os.path.sep
    items = os.listdir(allowance_files)
    exclude = []
    for item in items:
        item_path = os.path.join(allowance_files, item)
        allowance_vect = np.genfromtxt(item_path)
        all_zeros = np.all(allowance_vect == 0.0)
        if all_zeros:
            temp = item.split(".")
            numeric = int(float(temp[0]))
            exclude.append(numeric)
    data = {}
    for feature in features:
        data[feature] = []
        for midi_num in MIDI_array:
            if midi_num not in exclude:
                feature_file = features_dir + feature + os.path.sep + str(midi_num) + ".out"
                if os.path.isfile(feature_file):
                    data[feature].append(feature_file)
    #json_file_path = "/home/luciamarock/Dropbox/shared/dev/PitchDetector/piano_data.json"
    #with open(json_file_path, 'w') as json_file:
        #json.dump(data, json_file, indent=2)
    file_index = 10 # +21 mi da la nota MIDI (il 17 e' una merda - per fare tests grossolani vado di 10 in 10 da 0 a 80)
    print(data["FFTs"][file_index])
    #plotters.sum_plot(instrument, data["FFTs"][file_index], data["SpectralCentroid"][file_index], data["topMatches"][file_index],data["RTFIs"][file_index],data["Periodicity"][file_index],data["Allowance"][file_index])
    plotters.continuous_plot(instrument, data["FFTs"][file_index], data["SpectralCentroid"][file_index], data["topMatches"][file_index],data["RTFIs"][file_index],data["Periodicity"][file_index],data["Allowance"][file_index])
    #UF.compare_piano_methods_mono(data,40,MIDI_array)
    #analyze.find_harmonics_shape(instrument, data, MIDI_array, 30) # last arg, duration in frames after allowance 
    #analyze.find_patterns_piano(data,MIDI_array, 30)
    sys.exit()
elif instrument == "guitar":
    guitar_types = ["Ibanez","Prs"]
    features = []
    integers = {}
    for guitar_type in guitar_types:
        integers[guitar_type] = []
        directory_path = scores_root + guitar_type 
        items = os.listdir(directory_path)
        for item in items:
            item_path = os.path.join(directory_path, item)
            if os.path.isfile(item_path):
                if "integer" in item:
                    integers[guitar_type].append(item)
            else:
                if item not in features:
                    features.append(item)
    env_pairs = {}
    pattern = re.compile(r'^[A-Za-z]+(\d+)_integer\.out$')
    for key in integers.keys():
        env_pairs[key] = {}
        for intfile in integers[key]:
            match = pattern.match(intfile)
            if match:
                numeric_part = match.group(1)
                MIDI_num = UF.guitar_freq_2_MIDI(numeric_part)
                env_pairs[key][str(MIDI_num)] = intfile
else:
    sys.exit()

# at this point features contains the scores/instrument sub-folders (the six features)
# while env_pairs contains the _integer.out files associated with the MIDI number (for each guitar type)
data = {}
for guitar_type in env_pairs.keys():
    guitar_dict = env_pairs[guitar_type]
    data[guitar_type] = {}
    for midi_num in MIDI_array:
        if str(midi_num) in guitar_dict.keys():
            integer_out = scores_root + guitar_type + os.path.sep + guitar_dict[str(midi_num)]
            allowance_out = scores_root + guitar_type + os.path.sep + "allowance" + os.path.sep + str(midi_num) + ".out"
            scalar = UF.dot_product(integer_out,allowance_out)
            if scalar == 0.:
                print("{} - allowance/{}.out never enables".format(guitar_type,midi_num))
for guitar_type in data.keys():
    for feature in features:
        data[guitar_type][feature] = []
        for midi_num in MIDI_array:
            file_path = scores_root + guitar_type + os.path.sep + feature + os.path.sep + str(midi_num) + ".out"
            if os.path.isfile(file_path):
                data[guitar_type][feature].append(file_path)
"""
json_file_path = "/home/luciamarock/Dropbox/shared/dev/PitchDetector/appunti/guitar/data.json"
with open(json_file_path, 'w') as json_file:
    json.dump(data, json_file, indent=2)
"""
# at this point the data dictionary contains all the files needed for the study
file_index = 11 # will result in MIDI +40
guitar_type = "Prs"
print(data[guitar_type]["fft"][file_index])
plotters.continuous_plot(instrument, data[guitar_type]["fft"][file_index], data[guitar_type]["spectralcentroid"][file_index], data[guitar_type]["topmatches"][file_index],data[guitar_type]["rtfi"][file_index],data[guitar_type]["midipitch"][file_index])
#UF.compare_guitar_methods_mono(data,40,MIDI_array,guitar_type)
#analyze.find_harmonics_shape(instrument, data, MIDI_array, 30) # the number represent the duration in frames after allowance
#analyze.find_patterns_guitar(data,MIDI_array, 30)