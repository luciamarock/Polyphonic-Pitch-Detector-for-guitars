# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 12:41:09 2023

@author: luciamarock
"""

import math
import numpy as np
import re
import matplotlib.pyplot as plt

def freq_to_midi_general_array(numpy_array):
    MIDI_array = []
    midi_num = 0
    for note_freq in numpy_array:
        if note_freq > 0.:
            midi_temp = 12 * math.log(note_freq/440., 2) + 69
            midi_num = int(round(midi_temp))
        MIDI_array.append(midi_num)
    midi_array = np.array(MIDI_array)
    return midi_array

def freq_to_MIDI(numpy_array, instrument):
    MIDI_array = []
    if instrument == "piano":
        index_to_MIDI = 20
    elif instrument == "guitar":
        index_to_MIDI = 39
    else: 
        return MIDI_array
    for note_freq in numpy_array:
        ratio = note_freq / numpy_array[0]
        midi_num = 12 * math.log(ratio, 2) + index_to_MIDI
        midi_num = int(round(midi_num))
        MIDI_array.append(midi_num)
    
    return MIDI_array

def guitar_freq_2_MIDI(number):
    note_freq = float(number)
    ratio = note_freq / 77.781998
    midi_num = 12 * math.log(ratio, 2) + 39
    midi_num = int(round(midi_num))
    
    return midi_num

def dot_product(file1, file2):
    vector1 = np.genfromtxt(file1)
    vector2 = np.genfromtxt(file2)
    min_length = min(len(vector1), len(vector2))
    trimmed_vector1 = vector1[:min_length]
    trimmed_vector2 = vector2[:min_length]
    dot_product = np.dot(trimmed_vector1, trimmed_vector2)
    
    return dot_product

def find_max_rel(vector):
    indexes = []
    for i in range(1,len(vector)-1):
        sx = vector[i] - vector[i-1]
        dx = vector[i] - vector[i+1]
        if sx > 0 and dx > 0:
            indexes.append(i)
    return indexes

def harmonics_avg(vectRTFI):
    avg_vect = []
    avg_simple = []
    L = len(vectRTFI)
    for i in range(L):
        w1 = L - i
        w2 = L - 12 - i 
        w3 = L - 19 - i 
        if w3 > 0:
            AVG = (w1*vectRTFI[i] + w2*vectRTFI[i+12] + w3*vectRTFI[i+19])/(w1 + w2 + w3)
            AVGs = (vectRTFI[i] + vectRTFI[i+12] + vectRTFI[i+19])/3.
        elif w2 > 0:
            AVG = (w1*vectRTFI[i] + w2*vectRTFI[i+12])/(w1 + w2)
            AVGs = (vectRTFI[i] + vectRTFI[i+12])/2.
        else: 
            AVG = vectRTFI[i]
            AVGs = vectRTFI[i]
        avg_vect.append(AVG)
        avg_simple.append(AVGs)
    avg_vect = np.array(avg_vect)
    return avg_vect, avg_simple

def compare_piano_methods_mono(data,duration,abscissa):
    midi_starts = 20
    rtfi = np.zeros_like(abscissa)
    fft  = np.zeros_like(abscissa)
    wave = np.zeros_like(abscissa)
    match = np.zeros_like(abscissa)
    for i in range(len(data["Allowance"])):
        numeric_part = re.search(r'\d+', data["Allowance"][i]).group()
        allowance = np.genfromtxt(data["Allowance"][i])
        periodicity = np.genfromtxt(data["Periodicity"][i])
        dataRTFI = np.genfromtxt(data["RTFIs"][i])
        dataFFT = np.genfromtxt(data["FFTs"][i])
        top_matches = np.genfromtxt(data["topMatches"][i])
        frames = 0
        counter = 0
        note = int(numeric_part)
        while frames < duration and counter < len(allowance):
            if allowance[counter] > 0:
                rtfi_avg, not_used = harmonics_avg(dataRTFI[counter])
                rtfi_idx = find_max_rel(rtfi_avg)
                fft_idx = find_max_rel(dataFFT[counter])
                idx_toFind = note - midi_starts
                if idx_toFind in rtfi_idx:
                    rtfi[idx_toFind] += 1
                if idx_toFind in fft_idx:
                    fft[idx_toFind] += 1
                if float(note) in top_matches[counter]:
                    match[idx_toFind] += 1
                if float(note) == periodicity[counter]:
                    wave[idx_toFind] += 1
                frames += 1
            counter += 1
    plt.plot(abscissa,rtfi,color="blue")
    plt.plot(abscissa,rtfi,"o",color="blue")
    #plt.plot(abscissa,fft,color="green")
    #plt.plot(abscissa,fft,"o",color="green")
    #plt.plot(abscissa,wave,color="red")
    #plt.plot(abscissa,wave,"o",color="red")
    plt.plot(abscissa,match,color="black")
    plt.plot(abscissa,match,"o",color="black")
    plt.xlim(18, None)
    plt.ylim(0, duration+3)
    plt.title("First " + str(duration) + " frames of all the MIDI notes")
    plt.show()

def compare_guitar_methods_mono(data,duration,abscissa,guitar_type):
    midi_starts = 39
    rtfi = np.zeros_like(abscissa)
    fft  = np.zeros_like(abscissa)
    wave = np.zeros_like(abscissa)
    match = np.zeros_like(abscissa)
    for i in range(len(data[guitar_type]["allowance"])):
        numeric_part = re.search(r'\d+', data[guitar_type]["allowance"][i]).group()
        allowance = np.genfromtxt(data[guitar_type]["allowance"][i])
        periodicity = np.genfromtxt(data[guitar_type]["midipitch"][i])
        dataRTFI = np.genfromtxt(data[guitar_type]["rtfi"][i])
        dataFFT = np.genfromtxt(data[guitar_type]["fft"][i])
        top_matches = np.genfromtxt(data[guitar_type]["topmatches"][i])
        frames = 0
        counter = 0
        note = int(numeric_part)
        while frames < duration and counter < len(allowance):
            if allowance[counter] > 0:
                rtfi_avg, not_used = harmonics_avg(dataRTFI[counter])
                rtfi_idx = find_max_rel(rtfi_avg)
                fft_idx = find_max_rel(dataFFT[counter])
                idx_toFind = note - midi_starts
                if idx_toFind in rtfi_idx:
                    rtfi[idx_toFind] += 1
                if idx_toFind in fft_idx:
                    fft[idx_toFind] += 1
                if float(note) in top_matches[counter]:
                    match[idx_toFind] += 1
                if float(note) == periodicity[counter]:
                    wave[idx_toFind] += 1
                frames += 1
            counter += 1
    plt.plot(abscissa,rtfi,color="blue")
    plt.plot(abscissa,rtfi,"o",color="blue")
    #plt.plot(abscissa,fft,color="green")
    #plt.plot(abscissa,fft,"o",color="green")
    plt.plot(abscissa,wave,color="red")
    plt.plot(abscissa,wave,"o",color="red")
    plt.plot(abscissa,match,color="black")
    plt.plot(abscissa,match,"o",color="black")
    plt.xlim(18, None)
    plt.ylim(0, duration+3)
    plt.title("First " + str(duration) + " frames of all the MIDI notes")
    plt.show()