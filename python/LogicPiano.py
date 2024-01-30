import math
import copy
# Constants from consts.h
NNOTES = 89
NHARMS = 108
sens = 5 # between 1 and 10
rtfithreshold = 4.601162791 / sens
stability_threshold = 3.5 / sens
firstharmth = 4.3 / sens
scndharmth = 3.999 / sens
using_score = 1
op_wait = 9
index_to_MIDI = 20

class LogicPiano:
    def __init__(self):
        # Constructor (if needed)
        self.vectnote = [0.0] * NNOTES
        self.vectfft = [0.0] * NHARMS
        self.vectplot = [0.0] * NNOTES
        self.memory = [0.0] * NNOTES
        self.energymin = 0.0
        self.avfft = 0.0
        self.avrfti = 0.0
        self.totalenergy = 0.0
        self.AVenergymin = 0.0
        self.NOpattern = 0
        self.exist = [0] * NNOTES
        self.weights_prev = [0] * NNOTES
        self.activenotes = 0
        self.a_logic = [0] * NNOTES
        self._output = [0] * NNOTES
        self._event_buffer = [0] * NNOTES
        self._errors_buffer = [0] * NNOTES
        self.conditions = [0] * NNOTES
        self.logic_temp = [0.0] * NHARMS
        self.logic_final = [0.0] * NHARMS
    
    def get_conditions(self):
        return self.conditions
    
    def get_logic_temp(self):
        return self.logic_temp
    
    def get_logic_final(self):
        return self.logic_final
    
    def get_output(self):
        return self._output
    
    def get_detection(self):
        return self.a_logic
    
    def get_avg_rtfi(self):
        return self.avg_rtfi
    
    def get_min_max_idx_peacks(self):
        return self.minp, self.maxp

    def process_logic(self, data_rtfi, data_fft, allowance, a_score, m_strict_mode, a_towrite, periodicity, top_matches, spectralCentroid):
        bluemax = 0.0
        redmax = 0.0
        if spectralCentroid > 1.:
            midi_temp = 12 * math.log(spectralCentroid/440., 2) + 69
            midiCentroid = int(round(midi_temp))
        else:
            midiCentroid = index_to_MIDI + 1
        #bluemax, blueidx = self.find_max(data_rtfi)
        self.energymin = bluemax * rtfithreshold
        fft_avg, fft_Wavg, rtfi_avg, rtfi_Wagv, rtfi_max, maxidx, rtfi_min, minidx = self.new_find_max(data_rtfi, data_fft)
        value = (rtfi_max + rtfi_min)/2.
        #formatted_value = "%.6f" % value
        #print("{} test".format(formatted_value))
        self.avg_rtfi = value
        self.minp = minidx
        self.maxp = maxidx
        weights_current = self.vectplot_contains_candidates(rtfi_Wagv, periodicity, top_matches)
        self.logic_temp = copy.copy(self.vectplot)
        self.logic_final = rtfi_Wagv
        #redmax = self.process_vect_note_and_vect_plot(data_fft, data_rtfi, self.energymin, blueidx, allowance,top_matches, periodicity)
        self.AVenergymin = redmax * stability_threshold
        self.activenotes = 0
        self.a_logic = [0] * NNOTES
        #a_relmax = [0] * NNOTES
        #self.prepare_for_evaluation(a_towrite, top_matches, allowance, a_relmax)
        #activation_energy = bluemax * scndharmth * self.energymin
        #self.evaluation(a_score, activation_energy, a_relmax, m_strict_mode, data_rtfi, a_towrite)
    
    def new_find_max(self, data_rtfi, data_fft):
        fft_avg = []
        fft_Wavg = []
        rtfi_avg = []
        rtfi_Wagv = []
        rtfi_max = 0.
        maxidx = 0
        rtfi_min = 1000.
        minidx = 0
        for i in range(NHARMS):
            if i > 0 and i < NHARMS - 1:
                sx = data_fft[i] - data_fft[i-1]
                dx = data_fft[i] - data_fft[i+1]
                if sx > 0 and dx > 0:
                    self.vectfft[i] = data_fft[i]
                else:
                    self.vectfft[i] = 0.0
            fftW1 = NHARMS - i
            fftW2 = NHARMS - 12 - i 
            fftW3 = NHARMS - 19 - i 
            if fftW3 > 0:
                AVG = (fftW1*data_fft[i] + fftW2*data_fft[i+12] + fftW3*data_fft[i+19])/(fftW1 + fftW2 + fftW3)
                AVGs = (data_fft[i] + data_fft[i+12] + data_fft[i+19])/3.
            elif fftW2 > 0:
                AVG = (fftW1*data_fft[i] + fftW2*data_fft[i+12])/(fftW1 + fftW2)
                AVGs = (data_fft[i] + data_fft[i+12])/2.
            else: 
                AVG = data_fft[i]
                AVGs = data_fft[i]
            fft_avg.append(AVGs)
            fft_Wavg.append(AVG)
            if i < NNOTES:
                if i > 0 and i < NNOTES - 1:
                    sx = data_rtfi[i] - data_rtfi[i-1]
                    dx = data_rtfi[i] - data_rtfi[i+1]
                    if sx > 0 and dx > 0:
                        self.vectnote[i] = data_rtfi[i]
                        if data_rtfi[i] > rtfi_max:
                            rtfi_max = data_rtfi[i]
                            maxidx = i
                        if data_rtfi[i] < rtfi_min:
                            rtfi_min = data_rtfi[i]
                            minidx = i
                    else:
                        self.vectnote[i] = 0.0
                rtfiW1 = NNOTES - i
                rtfiW2 = NNOTES - 12 - i
                rtfiW3 = NNOTES - 19 - i
                if rtfiW3 > 0:
                    AVG = (rtfiW1*data_rtfi[i] + rtfiW2*data_rtfi[i+12] + rtfiW3*data_rtfi[i+19])/(rtfiW1 + rtfiW2 + rtfiW3)
                    AVGs = (data_rtfi[i] + data_rtfi[i+12] + data_rtfi[i+19])/3.
                elif rtfiW2 > 0:
                    AVG = (rtfiW1*data_rtfi[i] + rtfiW2*data_rtfi[i+12])/(rtfiW1 + rtfiW2)
                    AVGs = (data_rtfi[i] + data_rtfi[i+12])/2.
                else:
                    AVG = data_rtfi[i]
                    AVGs = data_rtfi[i]
                rtfi_avg.append(AVGs)
                rtfi_Wagv.append(AVG)
        
        return fft_avg, fft_Wavg, rtfi_avg, rtfi_Wagv, rtfi_max, maxidx, rtfi_min, minidx

    def vectplot_contains_candidates(self, rtfi_Wavg, periodicity, top_matches):   
        weights_current = [0.0] * NHARMS
        waveindex = int(periodicity) - index_to_MIDI
        if waveindex > -1 and waveindex < NHARMS:
            weights_current[waveindex] = weights_current[waveindex] + 2.0
        for j in range(len(top_matches)):
            index = int(top_matches[j]) - index_to_MIDI
            weights_current[index] = weights_current[index] + 2.
        local_sens = sens / 10. 
        pFmax = (1.25153 - 1)*2.*local_sens 
        pFmin = (1 - 0.8881)*2.*local_sens
        pSmax = (1.2316 - 1)*2.*local_sens
        pSmin = (1 - 0.8655)*2.*local_sens
        Fmax = 1 + pFmax
        Fmin = 1 - pFmin
        Smax = 1 + pSmax
        Smin = 1 - pSmin 
        for i in range(NHARMS):
            if i > 0 and i < NNOTES - 1:
                sx = rtfi_Wavg[i] - rtfi_Wavg[i-1]
                dx = rtfi_Wavg[i] - rtfi_Wavg[i+1]
                if sx > 0 and dx >0:
                    first_max = rtfi_Wavg[i]/Fmin 
                    first_min = rtfi_Wavg[i]/Fmax
                    second_max = rtfi_Wavg[i]/Smin
                    second_min = rtfi_Wavg[i]/Smax
                    if i + 19 < NNOTES - 1:
                        if (self.vectnote[i+12] > 0 or self.vectfft[i+12] > 0) and (self.vectnote[i+19] > 0 or self.vectfft[i+19]>0):
                            if rtfi_Wavg[i+12] > first_min and rtfi_Wavg[i+12] < first_max and rtfi_Wavg[i+19] > second_min and rtfi_Wavg[i+19] < second_max:
                                self.vectplot[i] = rtfi_Wavg[i]
                                weights_current[i] = weights_current[i] + 2.
                            else:
                                self.vectplot[i] = 0.0
                        else:
                            self.vectplot[i] = 0.0
                    elif i + 12 < NNOTES - 1:
                        if self.vectnote[i+12] > 0 or self.vectfft[i+12] > 0:
                            if rtfi_Wavg[i+12] > first_min and rtfi_Wavg[i+12] < first_max:
                                self.vectplot[i] = rtfi_Wavg[i]
                                weights_current[i] = weights_current[i] + 2.
                            else:
                                self.vectplot[i] = 0.0
                        else:
                            self.vectplot[i] = 0.0
                    else:
                        self.vectplot[i] = rtfi_Wavg[i]
                        weights_current[i] = weights_current[i] + 2.
                else:
                    self.vectplot[i] = 0.0
            elif i < NNOTES:
                self.vectplot[i] = 0.0
            else:
                self.vectfft[i] = self.vectfft[i] * 1.0

        return weights_current


    def prepare_for_evaluation(self, a_towrite, top_matches,allowance, a_relmax):
        for j in range(NNOTES):
            if self.vectplot[j] < self.AVenergymin and self.vectplot[j] > 0.0:
                if self.exist[j] < 4:
                    self.vectplot[j] = 0.0
            if self.vectplot[j] > 0.0:
                self.activenotes += 1
                self.a_logic[j] = j + 20
            if self.vectnote[j] > 0. and allowance > 0.:
                a_relmax[j] = j + 20

    def evaluation(self, a_score, activation_energy, a_relmax, m_strict_mode, data_rtfi, a_towrite):
        ghost_notes = [0] * NNOTES
        for i in range(NNOTES):
            if a_score[i] > 0:
                if self._find_element(a_score[i], self.a_logic if m_strict_mode else a_relmax):
                    a_towrite[i] = a_score[i]
                    self._event_buffer[i] = a_score[i]
                    ghost_notes[i] = 1
                    self._errors_buffer[i] = 0
                elif self._find_element(a_score[i] + 12, self.a_logic if m_strict_mode else a_relmax) or self._find_element(a_score[i] + 19, self.a_logic if m_strict_mode else a_relmax):
                    if data_rtfi[i] > activation_energy:
                        a_towrite[i] = a_score[i]
                        self._event_buffer[i] = a_score[i]
                        ghost_notes[i] = 1
                        self._errors_buffer[i] = 0
                    else:
                        a_towrite[i] = -100
                else:
                    self._errors_buffer[i] += 1
                    if self._errors_buffer[i] > op_wait:
                        a_towrite[i] = a_score[i] * (-1)
            else:
                if self._errors_buffer[i] > 0:
                    self._errors_buffer[i] = 0

            if self.a_logic[i] > 0:
                if self._find_element(self.a_logic[i], self._event_buffer):
                    ghost_notes[i] = 1
                elif self._find_element(self.a_logic[i - 12], self._event_buffer):
                    ghost_notes[i - 12] = 1
                elif self._find_element(self.a_logic[i - 19], self._event_buffer):
                    ghost_notes[i - 19] = 1
                elif self._find_element(self.a_logic[i - 24], self._event_buffer):
                    ghost_notes[i - 24] = 1
                elif self._find_element(self.a_logic[i - 28], self._event_buffer):
                    ghost_notes[i - 28] = 1
                elif self._find_element(self.a_logic[i - 43], self._event_buffer):
                    ghost_notes[i - 43] = 1
                elif self._find_element(self.a_logic[i - 47], self._event_buffer):
                    ghost_notes[i - 47] = 1
                else:
                    self._errors_buffer[i] -= 1
                    if self._errors_buffer[i] < op_wait * (-1):
                        a_towrite[i] = self.a_logic[i] * (-0.1)
            else:
                if self._errors_buffer[i] < 0:
                    self._errors_buffer[i] = 0

        for i in range(NNOTES):
            if ghost_notes[i] == 0:
                self._event_buffer[i] = 0
        # uncomment here to print on terminal (and eventually redirecting the output on a file > ...)
        """
        to_print = ""
        for elem in a_towrite:
            if elem != 0:
                to_print = to_print + "\t" + str(int(elem))
        print(to_print)
        """
        self._output = a_towrite

    def _find_element(self, to_search, vector_to_search):
        return to_search in vector_to_search

    def get_value_for_index(self, index):
        if index < NNOTES:
            return self.a_logic[index]
        return 0



