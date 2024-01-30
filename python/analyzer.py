# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 09:59:55 2023

@author: luciamarock
"""
import numpy as np 
import re
import utilFunctions as UF
import matplotlib.pyplot as plt

def verify_pattern(counter, idx_toFind, rtfi_avg, Fmax, Fmin, Smax, Smin):
    if idx_toFind + 19 < len(rtfi_avg):
        FOF = rtfi_avg[idx_toFind] / rtfi_avg[idx_toFind+12]
        if FOF > Fmax:
            print("First above the max threshold at chunk {}".format(counter))
        elif FOF < Fmin:
            print("First below the min threshold at chunk {}".format(counter))
        FOS = rtfi_avg[idx_toFind] / rtfi_avg[idx_toFind+19]
        if FOS > Smax:
            print("Second above the max threshold at chunk {}".format(counter))
        elif FOS < Smin:
            print("Second below the min threshold at chunk {}".format(counter))
    elif idx_toFind + 12 < len(rtfi_avg):
        FOF = rtfi_avg[idx_toFind] / rtfi_avg[idx_toFind+12]
        if FOF > Fmax:
            print("First above the max threshold at chunk {}".format(counter))
        elif FOF < Fmin:
            print("First below the min threshold at chunk {}".format(counter))
    else:
        pass

def detect(rtfi_idx, fft_idx, rtfi_avg, Fmax, Fmin, Smax, Smin):
    plausible = []
    for index in rtfi_idx:
        if index + 19 < len(rtfi_avg)-1:
            #if index + 19 in rtfi_idx  and index + 12 in rtfi_idx:
            if (index + 19 in rtfi_idx or index + 19 in fft_idx)  and (index + 12 in rtfi_idx or index + 12 in fft_idx):
                if (rtfi_avg[index+12] > rtfi_avg[index]/Fmax and # avoid to do this, first calculate FOF and FOS, then
                    rtfi_avg[index+12] < rtfi_avg[index]/Fmin and # apply the conditions on the thresholds 
                    rtfi_avg[index+19] > rtfi_avg[index]/Smax and 
                    rtfi_avg[index+19] < rtfi_avg[index]/Smin):
                    plausible.append(index)
        elif index + 12 < len(rtfi_avg)-1:
            #if index + 12 in rtfi_idx:
            if index + 12 in rtfi_idx or index + 12 in fft_idx:
                if rtfi_avg[index+12] > rtfi_avg[index]/Fmax and rtfi_avg[index+12] < rtfi_avg[index]/Fmin:
                    plausible.append(index)
        else: 
            plausible.append(index)
    return plausible 

def find_patterns_guitar(data,abscissa,duration):
    midi_starts = 39
    sens = 0.5 # increasing the sensitivity widen the thresholds 
    # thresholds are built upon the averaged RTFI (using the harmonics) which proven to give better results on prior studies 
    pFmax = (1.1346 - 1)*2.*sens 
    pFmin = (1 - 0.95058)*2.*sens
    pSmax = (1.1331 - 1)*2.*sens
    pSmin = (1 - 0.9335)*2.*sens
    Fmax = 1 + pFmax
    Fmin = 1 - pFmin
    Smax = 1 + pSmax
    Smin = 1 - pSmin 
    """ old thresholds """
    #Fmax = 1.032844453625284
    #Fmin = 0.9159186664224216
    #Smax = 1.049042748492001
    #Smin = 0.9117848187827674
    for key in data:
        for i in range(len(data[key]["allowance"])): # piano would start here 
            numeric_part = re.search(r'\d+', data[key]["allowance"][i]).group()
            note = int(numeric_part)
            idx_toFind = note - midi_starts
            #print("{}:{}".format(key,abscissa[idx_toFind]))
            allowance = np.genfromtxt(data[key]["allowance"][i])
            dataRTFI = np.genfromtxt(data[key]["rtfi"][i])
            dataFFT = np.genfromtxt(data[key]["fft"][i])
            frames = 0
            counter = 0
            attack_at = 0
            to_update = True
            while frames < duration and counter < len(allowance):
                if allowance[counter] > 0:
                    rtfi_avg, not_used = UF.harmonics_avg(dataRTFI[counter])
                    rtfi_idx = UF.find_max_rel(rtfi_avg)
                    fft_idx = UF.find_max_rel(dataFFT[counter])
                    a_relmax = []
                    for index in rtfi_idx:
                        a_relmax.append(abscissa[index])
                    candidates_idx = detect(rtfi_idx, fft_idx, rtfi_avg, Fmax, Fmin, Smax, Smin)
                    candidates = []
                    for index in candidates_idx:
                        candidates.append(abscissa[index])
                    if to_update:
                        attack_at = counter 
                        to_update = False
                    #print("candidates = {}, expected {}".format(candidates,note))
                    #print("a_relmax = {}".format(a_relmax))
                    if idx_toFind in rtfi_idx:
                        verify_pattern(counter, idx_toFind, rtfi_avg, Fmax, Fmin, Smax, Smin) # inutile per ora 
                        if idx_toFind not in   candidates_idx:
                            print("{}:{} not detected at chunk {}, attack was at chunk {}".format(key,abscissa[idx_toFind],counter,attack_at))
                    #else:
                        #print("peak not present at chunk {}".format(counter))
                        #print(rtfi_idx)
                    frames += 1
                counter += 1
            #print("attack at chunk number {}, exit at chunk number {}".format(attack_at,counter))

def find_patterns_piano(data,abscissa,duration):
    midi_starts = 20
    sens = 0.5
    pFmax = (1.25153 - 1)*2.*sens 
    pFmin = (1 - 0.8881)*2.*sens
    pSmax = (1.2316 - 1)*2.*sens
    pSmin = (1 - 0.8655)*2.*sens
    Fmax = 1 + pFmax
    Fmin = 1 - pFmin
    Smax = 1 + pSmax
    Smin = 1 - pSmin 
    """ old thresholds """
    #Fmax = 1.16279
    #Smax = 1.2503
    for i in range(len(data["Allowance"])):
        numeric_part = re.search(r'\d+', data["Allowance"][i]).group()
        note = int(numeric_part)
        idx_toFind = note - midi_starts
        #print("{}".format(abscissa[idx_toFind]))
        allowance = np.genfromtxt(data["Allowance"][i])
        dataRTFI = np.genfromtxt(data["RTFIs"][i])
        dataFFT = np.genfromtxt(data["FFTs"][i])
        frames = 0 
        counter = 0 
        to_update = True
        attack_at = 0
        while frames < duration and counter < len(allowance):
            if allowance[counter] > 0:
                rtfi_avg, not_used = UF.harmonics_avg(dataRTFI[counter])
                rtfi_idx = UF.find_max_rel(rtfi_avg)
                fft_idx = UF.find_max_rel(dataFFT[counter])
                candidates_idx = detect(rtfi_idx, fft_idx, rtfi_avg, Fmax, Fmin, Smax, Smin)
                candidates = []
                for index in candidates_idx:
                    candidates.append(abscissa[index])
                print("candidates = {}, expected {}".format(candidates,note))
                if idx_toFind in rtfi_idx and idx_toFind not in   candidates_idx:
                    print("{} not detected at chunk {}, attack was at chunk {}".format(abscissa[idx_toFind],counter,attack_at))
                if to_update:
                    attack_at = counter 
                    to_update = False
                frames += 1
            counter += 1
        #print("note {}, attack at chunk number {}, exit at chunk number {}".format(note,attack_at,counter))

def calculate_ratios(rtfi,index):
    rtfi_avg, not_used = UF.harmonics_avg(rtfi)
    if index + 12 < len(rtfi):
        FOF = rtfi[index]/rtfi[index+12]
        FOFAVG = rtfi_avg[index]/rtfi_avg[index+12]
    else:
        FOF = None
        FOFAVG = None
    if index + 19 < len(rtfi):
        FOS = rtfi[index]/rtfi[index+19]
        FOSAVG = rtfi_avg[index]/rtfi_avg[index+19]
    else:
        FOS = None
        FOSAVG = None

    return FOF, FOFAVG, FOS, FOSAVG

def find_min_max_avg(array):
    max_value = 0.
    min_value = 1000.
    avg_value = 0.
    for i in range(len(array)):
        if array[i] > max_value:
            max_value = array[i]
        if array[i] < min_value:
            min_value = array[i]
        avg_value += array[i] / float(len(array))
    return max_value, min_value, avg_value 

def find_harmonics_shape(instrument, data, abscissa, duration):
    if instrument == "piano":
        absolute_max_first = 0.
        absolute_min_first = 1000.
        absolute_max_second = 0.
        absolute_min_second = 1000.
        FOF_vect = np.zeros(len(abscissa))
        FOFmin_vect = np.zeros(len(abscissa))
        FOFmax_vect = np.zeros(len(abscissa))
        av_FOF_vect = np.zeros(len(abscissa))
        av_FOF_vect = np.zeros(len(abscissa))
        av_FOFmax_vect = np.zeros(len(abscissa))
        av_FOFmin_vect = np.zeros(len(abscissa))
        FOS_vect = np.zeros(len(abscissa))
        FOSmin_vect = np.zeros(len(abscissa))
        FOSmax_vect = np.zeros(len(abscissa))
        av_FOS_vect = np.zeros(len(abscissa))
        av_FOSmin_vect = np.zeros(len(abscissa))
        av_FOSmax_vect = np.zeros(len(abscissa))
        midistarts = 20
        allowance_files_list = data["Allowance"]
        rtfi_files_list = data["RTFIs"]
        for i in range(len(allowance_files_list)):
            numeric_part = re.search(r'\d+', allowance_files_list[i]).group()
            index = int(numeric_part) - midistarts
            allowance = np.genfromtxt(allowance_files_list[i])
            rtfi = np.genfromtxt(rtfi_files_list[i])
            counter = 0
            frame = 0
            fof = []
            av_fof = []
            fos = []
            av_fos = []
            while frame < duration and counter < len(allowance):
                if allowance[counter] > 0.:
                    FOF, FOFAVG, FOS, FOSAVG = calculate_ratios(rtfi[counter], index)
                    if FOF and FOFAVG:
                        fof.append(FOF)
                        av_fof.append(FOFAVG)
                    if FOS and FOSAVG:
                        fos.append(FOS)
                        av_fos.append(FOSAVG)
                    frame += 1
                counter += 1
            if len(fof) > 0:
                fofmax, fofmin, fofavg = find_min_max_avg(fof)
                FOFmax_vect[index] = fofmax
                FOFmin_vect[index] = fofmin
                FOF_vect[index] = fofavg
                fofmax, fofmin, fofavg = find_min_max_avg(av_fof)
                if fofmax > absolute_max_first:
                    absolute_max_first = fofmax
                if fofmin < absolute_min_first:
                    absolute_min_first = fofmin
                av_FOFmax_vect[index] = fofmax
                av_FOFmin_vect[index] = fofmin
                av_FOF_vect[index] = fofavg
            if len(fos) > 0:
                fosmax, fosmin, fosavg = find_min_max_avg(fos)
                FOSmax_vect[index] = fosmax
                FOSmin_vect[index] = fosmin
                FOS_vect[index] = fosavg
                fosmax, fosmin, fosavg = find_min_max_avg(av_fos)
                if fosmax > absolute_max_second:
                    absolute_max_second = fosmax
                if fosmin < absolute_min_second:
                    absolute_min_second = fosmin
                av_FOSmax_vect[index] = fosmax
                av_FOSmin_vect[index] = fosmin
                av_FOS_vect[index] = fosavg
        print("first harm limits {}-{}".format(absolute_max_first,absolute_min_first))
        print("second harm limits {}-{}".format(absolute_max_second,absolute_min_second))
        #plt.plot(abscissa,FOF_vect,color="blue")
        #plt.plot(abscissa,FOFmax_vect,"--",color="blue")
        #plt.plot(abscissa,FOFmin_vect,"--",color="blue")
        #plt.plot(abscissa,av_FOF_vect,color="blue")
        plt.plot(abscissa,av_FOFmax_vect,"--",color="blue")
        plt.plot(abscissa,av_FOFmin_vect,"--",color="blue")
        #plt.plot(abscissa,FOS_vect,color="green")
        #plt.plot(abscissa,FOSmax_vect,"--",color="green")
        #plt.plot(abscissa,FOSmin_vect,"--",color="green")
        #plt.plot(abscissa,av_FOS_vect,color="green")
        plt.plot(abscissa,av_FOSmax_vect,"--",color="green")
        plt.plot(abscissa,av_FOSmin_vect,"--",color="green")
        plt.title("second averaged")
        plt.show()
        #find_patterns_piano()
    elif instrument == "guitar":
        midistarts = 39
        for key in data:
            absolute_max_first = 0.
            absolute_min_first = 1000.
            absolute_max_second = 0.
            absolute_min_second = 1000.
            FOF_vect = np.zeros(len(abscissa))
            FOFmin_vect = np.zeros(len(abscissa))
            FOFmax_vect = np.zeros(len(abscissa))
            av_FOF_vect = np.zeros(len(abscissa))
            av_FOF_vect = np.zeros(len(abscissa))
            av_FOFmax_vect = np.zeros(len(abscissa))
            av_FOFmin_vect = np.zeros(len(abscissa))
            FOS_vect = np.zeros(len(abscissa))
            FOSmin_vect = np.zeros(len(abscissa))
            FOSmax_vect = np.zeros(len(abscissa))
            av_FOS_vect = np.zeros(len(abscissa))
            av_FOSmin_vect = np.zeros(len(abscissa))
            av_FOSmax_vect = np.zeros(len(abscissa))
            allowance_files_list = data[key]["allowance"]
            rtfi_files_list = data[key]["rtfi"]
            for i in range(len(allowance_files_list)):
                numeric_part = re.search(r'\d+', allowance_files_list[i]).group()
                index = int(numeric_part) - midistarts
                allowance = np.genfromtxt(allowance_files_list[i])
                rtfi = np.genfromtxt(rtfi_files_list[i])
                counter = 0
                frame = 0
                fof = []
                av_fof = []
                fos = []
                av_fos = []
                while frame < duration and counter < len(allowance):
                    if allowance[counter] > 0.:
                        FOF, FOFAVG, FOS, FOSAVG = calculate_ratios(rtfi[counter], index)
                        if FOF and FOFAVG:
                            fof.append(FOF)
                            av_fof.append(FOFAVG)
                        if FOS and FOSAVG:
                            fos.append(FOS)
                            av_fos.append(FOSAVG)
                        frame += 1
                    counter += 1
                if len(fof) > 0:
                    fofmax, fofmin, fofavg = find_min_max_avg(fof)
                    FOFmax_vect[index] = fofmax
                    FOFmin_vect[index] = fofmin
                    FOF_vect[index] = fofavg
                    fofmax, fofmin, fofavg = find_min_max_avg(av_fof)
                    if fofmax > absolute_max_first:
                        absolute_max_first = fofmax
                    if fofmin < absolute_min_first:
                        absolute_min_first = fofmin
                    av_FOFmax_vect[index] = fofmax
                    av_FOFmin_vect[index] = fofmin
                    av_FOF_vect[index] = fofavg
                if len(fos) > 0:
                    fosmax, fosmin, fosavg = find_min_max_avg(fos)
                    FOSmax_vect[index] = fosmax
                    FOSmin_vect[index] = fosmin
                    FOS_vect[index] = fosavg
                    fosmax, fosmin, fosavg = find_min_max_avg(av_fos)
                    if fosmax > absolute_max_second:
                        absolute_max_second = fosmax
                    if fosmin < absolute_min_second:
                        absolute_min_second = fosmin
                    av_FOSmax_vect[index] = fosmax
                    av_FOSmin_vect[index] = fosmin
                    av_FOS_vect[index] = fosavg
            print("{}: first harm limits {}-{}".format(key,absolute_max_first,absolute_min_first))
            print("{}: second harm limits {}-{}".format(key,absolute_max_second,absolute_min_second))
            #plt.plot(abscissa,FOF_vect,color="blue")
            #plt.plot(abscissa,FOFmax_vect,"--",color="blue")
            #plt.plot(abscissa,FOFmin_vect,"--",color="blue")
            #plt.plot(abscissa,av_FOF_vect,color="blue")
            plt.plot(abscissa,av_FOFmax_vect,"--",color="blue")
            plt.plot(abscissa,av_FOFmin_vect,"--",color="blue")
            #plt.plot(abscissa,FOS_vect,color="green")
            #plt.plot(abscissa,FOSmax_vect,"--",color="green")
            #plt.plot(abscissa,FOSmin_vect,"--",color="green")
            #plt.plot(abscissa,av_FOS_vect,color="green")
            plt.plot(abscissa,av_FOSmax_vect,"--",color="green")
            plt.plot(abscissa,av_FOSmin_vect,"--",color="green")
            plt.title(key + " first averaged")
            plt.show()

    else:
        print("no instrument found")