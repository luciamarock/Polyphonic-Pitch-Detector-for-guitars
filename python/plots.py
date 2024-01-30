#import os
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import utilFunctions as UF
import analyzer

def candidates_for_instrument(rtfi_avg, fft_current,instrument):
    """ finds the peaks of the spectrum which are best notes candidates"""
    if instrument == "piano":
        sens = 0.5
        pFmax = (1.25153 - 1)*2.*sens 
        pFmin = (1 - 0.8881)*2.*sens
        pSmax = (1.2316 - 1)*2.*sens
        pSmin = (1 - 0.8655)*2.*sens
        Fmax = 1 + pFmax
        Fmin = 1 - pFmin
        Smax = 1 + pSmax
        Smin = 1 - pSmin 
    elif instrument == "guitar":
        sens = 0.5
        pFmax = (1.1346 - 1)*2.*sens 
        pFmin = (1 - 0.95058)*2.*sens
        pSmax = (1.1331 - 1)*2.*sens
        pSmin = (1 - 0.9335)*2.*sens
        Fmax = 1 + pFmax
        Fmin = 1 - pFmin
        Smax = 1 + pSmax
        Smin = 1 - pSmin 
    rtfi_idx = UF.find_max_rel(rtfi_avg)
    fft_idx = UF.find_max_rel(fft_current)
    candidates_idx = analyzer.detect(rtfi_idx, fft_idx, rtfi_avg, Fmax, Fmin, Smax, Smin)
    return candidates_idx

def sum_plot(instrument, datafft_file, centroid_file,topMatches,rtfi_file,periodicity_file,allowance_file):
    duration = 40
    if instrument == "piano":
        fftpoints = 108
        midi_starts = 20        
    elif instrument == "guitar":
        fftpoints = 70
        midi_starts = 39
    else:
        sys.exit()
    p = 0.5  # == sens
    abscissa = np.array(list(range(midi_starts, midi_starts + fftpoints)))
    wheights_prev = np.zeros(fftpoints)
    dataFFT = np.genfromtxt(datafft_file)
    spectralCentroid = np.genfromtxt(centroid_file)
    midiCentroid = UF.freq_to_midi_general_array(spectralCentroid)
    top_matches = np.genfromtxt(topMatches)
    dataRTFI = np.genfromtxt(rtfi_file)
    periodicity = np.genfromtxt(periodicity_file)
    allowance = np.genfromtxt(allowance_file)
    counter = 0
    frames = 0 
    detection_vect = np.zeros(len(abscissa))
    while counter < len(allowance) and frames < duration:
        if allowance[counter] > 0.:
            avg_rtfi, avg_simple_rtfi = UF.harmonics_avg(dataRTFI[counter])
            avg_fft, avg_simple_fft = UF.harmonics_avg(dataFFT[counter])
            candidates_idx = candidates_for_instrument(avg_rtfi,dataFFT[counter],instrument)
            min_value = np.min(avg_rtfi)
            rtfi_last_idx = len(avg_rtfi) - 1
            pad_width = fftpoints - len(avg_rtfi)
            extendedRTFI = np.pad(avg_rtfi, (0, pad_width), mode='linear_ramp', end_values=(avg_rtfi[rtfi_last_idx], min_value))
            extendedRTFI = extendedRTFI - 0.75
            matches = np.zeros(fftpoints)
            wheights_current = np.zeros(fftpoints)
            wavelength = np.zeros(fftpoints)
            waveindex = int(periodicity[counter] - midi_starts)
            try: 
                wavelength[waveindex] = extendedRTFI[waveindex]
                wheights_current[waveindex] += 2
            except:
                print("waveindex = {}".format(waveindex))
            for j in range(len(top_matches[counter])):
                index = int(top_matches[counter][j] - midi_starts)
                matches[index] = dataFFT[counter][index]
                wheights_current[index] += 2.
            for index in candidates_idx:
                wheights_current[index] += 2.
            for k in range(len(wheights_current)):
                value = p * wheights_current[k] + (1 - p) * wheights_prev[k]
                wheights_current[k] = value 
                wheights_prev[k] = value
            wheights_current = wheights_current * p
            energyvect = avg_simple_fft*extendedRTFI*3.75*wheights_current # dataFFT[i] extend also avg_simple_rtfi ?
            wheights_current = energyvect * extendedRTFI * 7.75 # la ragione e' che sul breve termine pesano i "pesi" sul lungo l'RTFI
            index = int(midiCentroid[counter] - midi_starts) # index mi da la separazione tra parte sinistra e parte destra del vettore energia
            left_part = energyvect[:index + 1]
            right_part = energyvect[index:]
            energy_threshold = (np.max(left_part) + np.max(right_part)) / 2. # no la soglia non si deve calcolare cosi' (ma e' un inizio)
            
            for cc in range(len(wheights_current)):
                if wheights_current[cc] > energy_threshold:
                    detection_vect[cc] += 1
            
            frames += 1
        counter += 1
    detection_vect = detection_vect / np.max(detection_vect)
    plt.plot(abscissa,detection_vect)
    plt.show()

def continuous_plot(instrument, datafft_file, centroid_file,topMatches,rtfi_file,periodicity_file,allowance_file):
    if instrument == "piano":
        fftpoints = 108
        midi_starts = 20        
    elif instrument == "guitar":
        fftpoints = 70
        midi_starts = 39
    else:
        sys.exit()
    p = 0.5  # == sens
    abscissa = np.array(list(range(midi_starts, midi_starts + fftpoints)))
    wheights_prev = np.zeros(fftpoints)
    dataFFT = np.genfromtxt(datafft_file)
    spectralCentroid = np.genfromtxt(centroid_file)
    midiCentroid = UF.freq_to_midi_general_array(spectralCentroid)
    top_matches = np.genfromtxt(topMatches)
    dataRTFI = np.genfromtxt(rtfi_file)
    periodicity = np.genfromtxt(periodicity_file)
    allowance = np.genfromtxt(allowance_file)
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots()

    for i in range(len(dataFFT)):
        if i < 71 and allowance[i] > 0.: # first note in score at frame 562  
            avg_rtfi, avg_simple_rtfi = UF.harmonics_avg(dataRTFI[i])
            avg_fft, avg_simple_fft = UF.harmonics_avg(dataFFT[i])
            candidates_idx = candidates_for_instrument(avg_rtfi,dataFFT[i],instrument)     
            #max_rtfi = np.max(avg_rtfi) # will be useful at chunk 26 of note 38
            min_value = np.min(avg_rtfi)
            rtfi_last_idx = len(avg_rtfi) - 1
            pad_width = fftpoints - len(avg_rtfi)
            extendedRTFI = np.pad(avg_rtfi, (0, pad_width), mode='linear_ramp', end_values=(avg_rtfi[rtfi_last_idx], min_value))
            extendedRTFI = extendedRTFI - 0.75
            extendedRTFI[extendedRTFI < 0.] = 0.
            # mode='linear_ramp', end_values=(0, min_value) / mode='constant', constant_values=min_value
            matches = np.zeros(fftpoints)
            wheights_current = np.zeros(fftpoints)
            wavelength = np.zeros(fftpoints)
            waveindex = int(periodicity[i] - midi_starts)
            try: 
                wavelength[waveindex] = extendedRTFI[waveindex]
                wheights_current[waveindex] += 2
            except:
                print("waveindex = {}".format(waveindex))
            for j in range(len(top_matches[i])):
                index = int(top_matches[i][j] - midi_starts)
                matches[index] = dataFFT[i][index]
                wheights_current[index] += 2.
            for index in candidates_idx:
                wheights_current[index] += 2.
            
            for k in range(len(wheights_current)):
                value = p * wheights_current[k] + (1 - p) * wheights_prev[k]
                wheights_current[k] = value 
                wheights_prev[k] = value
            
            wheights_current = wheights_current * p
            energyvect = avg_simple_fft*extendedRTFI*2.75 # dataFFT[i] extend also avg_simple_rtfi ?
            simple_product = dataFFT[i] * extendedRTFI
            wheights_current = wheights_current * energyvect * extendedRTFI * 4.75 # la ragione e' che sul breve termine pesano i "pesi" sul lungo l'RTFI
            
            ax.clear()
            ax.plot(abscissa,dataFFT[i],color="green")
            ax.plot(abscissa,extendedRTFI,color="blue")
            ax.plot(abscissa,energyvect,"--",color="grey")
            ax.plot(abscissa,simple_product,"--",color="yellow")
            ax.plot(abscissa,wheights_current,"o",color="pink")
            ax.plot(abscissa,wavelength,"o",color="red")
            ax.plot(abscissa,matches,"o",color="black")
            max_value = np.max(wheights_current)
            max_index = np.argmax(wheights_current) + midi_starts
            index = int(midiCentroid[i] - midi_starts) # index mi da la separazione tra parte sinistra e parte destra del vettore energia
            left_part = energyvect[:index + 1]
            right_part = energyvect[index:]
            energy_threshold = (np.max(left_part) + np.max(right_part)) / 2. # no la soglia non si deve calcolare cosi' (ma e' un inizio)
            ax.annotate(str(max_index),xy=(max_index,max_value),xytext=(1.5, 1.5), textcoords='offset points')
            ax.vlines(x=midiCentroid[i], ymin=0, ymax=np.max(dataFFT[i]), colors='grey', linestyles='dashed')
            ax.hlines(y=energy_threshold, xmin=abscissa[0], xmax=abscissa[len(abscissa)-1], colors='grey', linestyles='dashed')
            ax.set_ylim(bottom=0)

            plt.draw()  # Redraw the plot
            fig.canvas.flush_events()  # Update the plot
            """
            detection_vect = []
            for cc in range(len(wheights_current)):
                if wheights_current[cc] > energy_threshold:
                    detection_vect.append(abscissa[cc])
            print("{}\tframe {}".format(detection_vect,i))
            """
            time.sleep(0.016)  # Pause for a moment
    
    plt.ioff()  # Turn off interactive mode
    plt.show()
