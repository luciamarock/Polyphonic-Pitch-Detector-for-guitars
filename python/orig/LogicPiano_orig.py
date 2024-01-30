# Constants from consts.h
NNOTES = 89
sens = 5 # between 1 and 10
rtfithreshold = 4.601162791 / sens
stability_threshold = 3.5 / sens
firstharmth = 4.3 / sens
scndharmth = 3.999 / sens
op_wait = 9

class LogicPiano:
    def __init__(self):
        # Constructor (if needed)
        self.vectnote = [0.0] * NNOTES
        self.vectplot = [0.0] * NNOTES
        self.energymin = 0.0
        self.avfft = 0.0
        self.avrfti = 0.0
        self.totalenergy = 0.0
        self.AVenergymin = 0.0
        self.NOpattern = 0
        self.exist = [0] * NNOTES
        self.not_presence = [0] * NNOTES
        self.activenotes = 0
        self.a_logic = [0] * NNOTES
        self._event_buffer = [0] * NNOTES
        self._errors_buffer = [0] * NNOTES

    def process_logic(self, data_rtfi, data_fft, allowance, a_score, m_strict_mode, a_towrite, periodicity, top_matches):
        bluemax, blueidx = self.find_max(data_rtfi)
        self.energymin = bluemax * rtfithreshold
        redmax = 0.0
        self.process_vect_note_and_vect_plot(data_fft, data_rtfi, self.energymin, blueidx, redmax, allowance)
        self.AVenergymin = redmax * stability_threshold
        self.activenotes = 0
        self.a_logic = [0] * NNOTES
        a_relmax = [0] * NNOTES

        self.prepare_for_evaluation(a_towrite, top_matches)
        activation_energy = bluemax * scndharmth * self.energymin
        self.evaluation(a_score, activation_energy, a_relmax, m_strict_mode, data_rtfi, a_towrite)

    def find_max(self, data_rtfi):
        bluemax = 0.0
        blueidx = -1
        for j in range(1, NNOTES - 1):
            if data_rtfi[j] - data_rtfi[j - 1] > 0.0 and data_rtfi[j] - data_rtfi[j + 1] > 0.0:
                self.vectnote[j] = data_rtfi[j]
                if self.vectnote[j] > bluemax:
                    bluemax = self.vectnote[j]
                    blueidx = j
                if self.memory[j] > 0.0 and self.exist[j] < 4:
                    self.exist[j] += 1
            else:
                self.vectnote[j] = 0.0
                self.memory[j] = 0.0
                self.exist[j] = 0
        return bluemax, blueidx

    def process_vect_note_and_vect_plot(self, data_fft, data_rtfi, energymin, blueidx, redmax, allowance):
        for j in range(NNOTES):
            if self.vectnote[j] > 0.0 and allowance > 0.0:
                self.NOpattern = 0
                if j < 70:
                    if vectnote[j+6] > energymin or vectnote[j+8] > energymin:
                        if self.activenotes > 0:
                            self.NOpattern = 1
                    self.avfft = (data_fft[j] + data_fft[j+12] + data_fft[j+19]) / 3.0
                    self.avrfti = (self.vectnote[j] + self.vectnote[j+12] + data_rtfi[j+19]) / 3.0
                elif j >= 70 and j < 77:
                    self.avfft = (data_fft[j] + data_fft[j+12]) / 2.0
                    self.avrfti = (self.vectnote[j] + self.vectnote[j+12]) / 2.0
                else:
                    self.avfft = data_fft[j]
                    self.avrfti = self.vectnote[j]
                self.totalenergy = self.avrfti * self.avfft * 2.0

                if j < 70 and self.vectnote[j+12] > self.vectnote[j] * firstharmth and self.vectnote[j+19] > self.vectnote[j] * scndharmth:
                    self.not_presence[j] = 0
                    if self.vectnote[j] > energymin:
                        self.vectplot[j] = self.totalenergy
                        self.memory[j] = self.totalenergy
                    else:
                        self.vectplot[j] = 0.0
                        self.memory[j] = 0.0
                        self.exist[j] = 0
                elif j < 70 and self.vectnote[j] > energymin and self.vectnote[j+12] > self.vectnote[j] * firstharmth and self.NOpattern > 0:
                    self.not_presence[j] = 0
                    self.vectplot[j] = self.totalenergy
                    self.memory[j] = self.totalenergy
                elif j >= 70 and j < 77 and self.vectnote[j+12] > self.vectnote[j] * firstharmth:
                    self.not_presence[j] = 0
                    if self.vectnote[j] > energymin:
                        self.vectplot[j] = self.totalenergy
                        self.memory[j] = self.totalenergy
                    else:
                        self.vectplot[j] = 0.0
                        self.memory[j] = 0.0
                        self.exist[j] = 0
                elif j >= 77 and self.vectnote[j] > energymin:
                    self.not_presence[j] = 0
                    self.vectplot[j] = self.totalenergy
                    self.memory[j] = self.totalenergy
                elif self.memory[j] > 0.0:
                    self.vectplot[j] = self.memory[j]
                    if self.not_presence[j] < 4:
                        self.not_presence[j] += 1

                    if j != blueidx or self.not_presence[j] > 3:
                        self.memory[j] = 0.0
                        self.not_presence[j] = 0
                elif self.exist[j] > 3 and using_score == 0:
                    self.vectplot[j] = self.totalenergy
                    self.memory[j] = 0.0
                    self.not_presence[j] = 0
                else:
                    self.vectplot[j] = 0.0
                    self.memory[j] = 0.0
                    self.exist[j] = 0
                    self.not_presence[j] = 0
            else:
                self.vectplot[j] = 0.0
                self.memory[j] = 0.0
                self.exist[j] = 0
                self.not_presence[j] = 0
            if self.vectplot[j] > redmax:
                redmax = self.vectplot[j]

    def prepare_for_evaluation(self, a_towrite, top_matches):
        for j in range(NNOTES):
            if self.vectplot[j] < self.AVenergymin and self.vectplot[j] > 0.0:
                if self.exist[j] < 4:
                    self.vectplot[j] = 0.0
            if self.vectplot[j] > 0.0:
                self.activenotes += 1
            if self.vectplot[j] > 0:
                self.a_logic[j] = j + 20

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

    def _find_element(self, to_search, vector_to_search):
        return to_search in vector_to_search

    def get_value_for_index(self, index):
        if index < NNOTES:
            return self.a_logic[index]
        return 0



