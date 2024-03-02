# logic_main.py
"""
@brief Python script for processing piano musical data.

This module is intended to constitute the new version of python/logic_piano.py. 
It uses the class python.LogicPiano, which is a ChatGPT translation of LogicPiano.h and LogicPiano.cpp. 
In theory, the script should produce the same results as the C++ implementation.

This script loads piano note frequencies from a file, reads score data, converts it into a matrix representation, and 
generates a JSON file containing information about MIDI note numbers, note names, and frequencies.
"""

import os
import json
import math
import time
import numpy as n 
#import sys
from numpy import genfromtxt
import matplotlib.pyplot as plt
import python.LogicPiano as LP

freq=genfromtxt("./algo_outputs/notes_piano.txt") # notes of the piano 
names = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
logic = LP.LogicPiano()
NNOTES = LP.NNOTES
NHARMS = LP.NHARMS
index_to_MIDI = 20 # Added to C++ !!
m_strictMode = True

def freq_to_MIDI(numpy_array):
    """
    Converts an array of frequencies to corresponding MIDI numbers.

    Args:
        numpy_array (numpy.ndarray): An array of floating-point numbers representing frequencies in Hz.

    Returns:
        numpy.ndarray: An array of integers representing the corresponding MIDI numbers.

    Raises:
        ValueError: If any frequency in the input array is not found in the `freq` global variable.
    """
    periodicity = []
    for elem in numpy_array:
        periodicity.append(n.where(freq == elem)[0][0] + index_to_MIDI)
    periodicity = n.array(periodicity)
    return periodicity 

def get_score(score_file):
    """
    Reads and parses a musical score file into a list of lists representing MIDI data.

    Args:
        score_file (str): Path to the score file.

    Returns:
        list: A list of lists, where each inner list represents a line in the score with MIDI data.

    Raises:
        FileNotFoundError: If the score file is not found.
        IOError: If there is an error reading the file.
    """
    scoreout = open(score_file, "r")
    scoreout=scoreout.readlines()
    midiscore = []
    for line in scoreout:
        temp = line.split("\n")
        line = temp[0]
        if "\t" in line:
            elemout = []
            elem = line.split("\t")
            for ci in range(1,len(elem)):
                elemout.append(int(float(elem[ci])))
            midiscore.append(elemout)
        else:
            midiscore.append([""])
    return midiscore

def get_matrix(midiscore,freq):
    """
    Creates a matrix representing the score, where rows represent score elements and columns represent MIDI notes.

    Args:
        midiscore (list): A list of lists representing MIDI data from a score.
        freq (numpy.ndarray): An array of floating-point numbers representing frequencies in Hz.

    Returns:
        numpy.ndarray: A matrix where rows represent score elements and columns represent MIDI notes, with values indicating the presence of notes.

    Raises:
        ValueError: If any MIDI number in the `midiscore` is not found in the `freq` global variable.
    """
    matrix = n.zeros((len(midiscore), NNOTES))
    for i in range(len(midiscore)):
        for j in range(len(midiscore[i])):
            element = midiscore[i][j]
            if element:
                value = int(float(element))
                matrix[i][value - index_to_MIDI] = value 
    return matrix

midiscore = get_score("./appunti/logic/checks/resources/a_score.out")
matrixscore = get_matrix(midiscore,freq)

"""
Creates a JSON file containing information about MIDI note numbers, note names, and frequencies.

Args:
    filename (str): Path to the output JSON file.
    freq (numpy.ndarray): An array of floating-point numbers representing frequencies in Hz.

Raises:
    ValueError: If any frequency in the `freq` array is not found in the `names` global variable.
    IOError: If there is an error writing to the file.
"""

filename = "/home/luciamarock/Dropbox/shared/dev/PitchDetector/resources/note_struct.json"
if not os.path.isfile(filename):
    note_struct = {}
    for note_freq in freq:
        ratio = note_freq / freq[0]
        midi_num = 12 * math.log(ratio, 2) + index_to_MIDI
        midi_num = int(round(midi_num))
        risultato, resto = divmod(midi_num, 12)
        note_name = names[int(round(resto))] + str(int(round(risultato - 1)))
        note_struct[str(midi_num)] = {"name":note_name,"frequency":note_freq}
        #print("{} - frequency {}, midi {}".format(note_name, note_freq, midi_num))
    with open("./resources/note_struct.json", "w") as json_file:
        json.dump(note_struct, json_file, indent=4)

"""
# The following block loads the data needed for analyzing Beat It Cut 
#integer=n.array(genfromtxt("./appunti/logic/resources/integer.out"))
allowance=n.array(genfromtxt("./appunti/logic/resources/allowance.out"))
dataFFT=n.array(genfromtxt("./appunti/logic/resources/dataFFT.out"))
dataRTFI=n.array(genfromtxt("./appunti/logic/resources/dataRTFI.out"))
#spectralCentroid=n.array(genfromtxt("./appunti/logic/resources/spectralCentroid.out"))
periodicities=n.array(genfromtxt("./appunti/logic/resources/periodicity.out"))
periodicity = freq_to_MIDI(periodicities) # l'ho fatto in C++ (per la chitarra gia' uscira come MIDI)
topMatches=n.array(genfromtxt("./appunti/logic/resources/topMatches.out"))
"""

json_file_path = '/home/luciamarock/Dropbox/shared/dev/PitchDetector/appunti/study/piano_data.json'
with open(json_file_path, 'r') as file:
    data = json.load(file)

""" monophonic samples """
file_index = 11 #file_index + 21 is the MIDI note number
dataRTFI = n.genfromtxt(data["RTFIs"][file_index])
dataFFT = n.genfromtxt(data["FFTs"][file_index])
allowance = n.genfromtxt(data["Allowance"][file_index])
periodicity = n.genfromtxt(data["Periodicity"][file_index])
topMatches = n.genfromtxt(data["topMatches"][file_index]) 

"""
# The following plot is static and it is used to compare the pink vector with the previous approach 
frames = 0 
counter = 0
duration = 40
absissa = n.arange(20, 109)
ordinata = n.zeros(89)
while counter < len(allowance) and frames < duration:
    if allowance[counter] > 0.:
        a_towrite = [0] * NNOTES
        a_score = matrixscore[counter]
        logic.process_logic(dataRTFI[counter], dataFFT[counter], allowance[counter], a_score, m_strictMode, a_towrite, int(periodicity[counter]), topMatches[counter])
        logic_temp = logic.get_logic_temp()
        logic_temp = n.array(logic_temp)
        indices = n.where(logic_temp > 0)
        flat_indices = indices[0]
        #flat_indices += 20
        for index in flat_indices:
            ordinata[index] += 1
        frames += 1
    counter += 1 
ordinata = ordinata / n.max(ordinata)
plt.plot(absissa,ordinata)
plt.show()
sys.exit()
"""

#abscissa = n.arange(20, 109)
abscissa = n.arange(20, 128)

""" monophonic samples """
filename = "34.out"
scores_base_path = "/home/luciamarock/Documents/AudioAnalyzer/scores/piano/"
allowance_file = scores_base_path + "Allowance" + os.path.sep + filename 

""" poliphonic samples """
#filename = "55_59_62_72.out"
#scores_base_path = "/home/luciamarock/Documents/AudioAnalyzer/scores/piano/Poly/"
#allowance_file = scores_base_path + "Allowance" + os.path.sep + filename 

print(allowance_file)

fft_file = scores_base_path + "FFTs" + os.path.sep + filename 
periodicity_file = scores_base_path + "Periodicity" + os.path.sep + filename
rtfi_file = scores_base_path + "RTFIs" + os.path.sep + filename
centroid_file = scores_base_path + "SpectralCentroid" + os.path.sep + filename
matches_file = scores_base_path + "topMatches" + os.path.sep + filename 
dataRTFI = n.genfromtxt(rtfi_file)
dataFFT = n.genfromtxt(fft_file)
allowance = n.genfromtxt(allowance_file)
periodicity = n.genfromtxt(periodicity_file)
topMatches = n.genfromtxt(matches_file) 
spectralCentroid = n.genfromtxt(centroid_file)

# Initialize the figure and axis
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots()
activate_plot = True
start = -1

for i in range(len(allowance)):
    a_towrite = [0] * NNOTES
    a_score = matrixscore[i]
    logic.process_logic(dataRTFI[i], dataFFT[i], allowance[i], a_score, m_strictMode, a_towrite, periodicity[i], topMatches[i], spectralCentroid[i])
    if allowance[i] > 0.0: # first note in score at frame 562  
        if start < 0:
            start = i
        test_vect = []  
        matches = []  # turns green when the expected notes are found in the output 
        output = logic.get_output() # a_towrite written by the Logic 
        for j in range(NHARMS):
            if j < NNOTES:
                test_vect.append(dataRTFI[i][j])
            else:
                test_vect.append(dataRTFI[i][NNOTES - 1])
        conditions = logic.get_conditions()
        logic_temp = logic.get_logic_temp()
        for k in range(NHARMS - NNOTES):
            logic_temp.append(dataRTFI[i][NNOTES - 1])
        logic_final = logic.get_logic_final() 
        test_element = logic.get_test_element()
        detection = logic.get_detection()  
        #string = "test " + str(test_vect[35])
        #print(string)
        if activate_plot and i < 20 + start:
            th = logic.get_avg_rtfi()
            minp, maxp = logic.get_min_max_idx_peacks()
            ax.clear()
            ax.plot(abscissa,test_vect)
            #ax.plot(abscissa,logic_temp)
            ax.plot(abscissa,logic_final)
            ax.plot(abscissa,detection,"o")
            ax.axhline(y=th, color='grey', linestyle='--')
            ax.axhline(y=test_element, color='grey', linestyle='--')
            #ax.axvline(abscissa[minp], color='pink', linestyle='--')
            #ax.axvline(abscissa[maxp], color='pink', linestyle='--')
            plt.draw()  # Redraw the plot
            fig.canvas.flush_events()  # Update the plot
            time.sleep(0.016)  # Pause for a moment
        elif activate_plot:
            string = ""
            for k in range(len(detection)):
                if detection[k] > 0.:
                    string = string + str(k + 20) + " - "
                    #formatted_value = "%.6f" % round(value,6)
                    #string = string + formatted_value + " "
            print("detection {}".format(string))
plt.ioff()  # Turn off interactive mode
plt.show()


"""
# only useful when analyzing a song in sync with the score 
ax.plot(test_vect,'d',color="red")
for k in range(len(test_vect)):
    if test_vect[k] > 0:
        ax.annotate(str(conditions[k]),xy=(k,dataRTFI[i][k]),xytext=(1.5, 1.5), textcoords='offset points')
        ax.vlines(x=k, ymin=0, ymax=test_vect[k], colors='grey', linestyles='dashed')
    if logic_temp[k] > 0:
        ax.annotate(str(conditions[k]),xy=(k,logic_temp[k]),xytext=(1.5, 1.5), textcoords='offset points')
ax.plot(matches,'d',color="green")
"""

