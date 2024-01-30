
out_f = open("vectplot_printout.txt", "w")
out_n = open("output_evaluated_printout.txt", "w")
out_s = open("midiscore_printout.txt", "w")


_event_buffer = [0]*89
_errors_buffer = [0]*89

def evaluation(nbuffer,scoreout,vectplot,vectnote,vactmaxrel,energymin,fftmin,wait=8):
    global out_f
    global out_s
    global out_n
    global _event_buffer
    global _errors_buffer
    a_score = [0]*89    # written in midiscore_printout.txt
    a_logic = [0]*89    # written in vectplot_printout.txt
    a_maxrel = [0]*89    # written in vectplot_printout.txt
    a_towrite = [0]*89  # comparison result --> written in output_evaluated_printout.txt
    ghost_notes = [0]*89  # used for resetting _event_buffer
    # ---------- composing score vector ----------
    for note in scoreout:
        if note:
            out_s.write("\t" + str(note))
            a_score[note - 20] = note
    out_s.write("\n")
    # ---------- composing analysis vector ----------
    for note in range(len(vectplot)):
        if vectplot[note] > 0.:
            out_f.write("\t" + str(note + 20))
            a_logic[note] = note + 20
        if vactmaxrel[note] > 0.:
            a_maxrel[note] = note + 20
    out_f.write("\n")
    # ---------- decision making ----------
    for idx in range(len(a_towrite)):
        if a_score[idx] > 0:
            if a_score[idx] + 12 in a_maxrel or  a_score[idx] + 19 in a_maxrel:
                if vectnote[idx] > energymin:
                    a_towrite[idx] = a_score[idx]
                    _event_buffer[idx] = a_score[idx]
                    ghost_notes[idx] = 1 
                    _errors_buffer[idx] = 0
                else:
                    a_towrite[idx] = -100
            elif a_score[idx] in a_maxrel:
                a_towrite[idx] = a_score[idx]
                _event_buffer[idx] = a_score[idx]
                ghost_notes[idx] = 1 
                _errors_buffer[idx] = 0
            else:
                _errors_buffer[idx] = _errors_buffer[idx] + 1
                if _errors_buffer[idx] > wait:
                    a_towrite[idx] = a_score[idx] * (-1)
        else:
            if _errors_buffer[idx] > 0:
                _errors_buffer[idx] = 0
        if a_logic[idx] > 0:
            if a_logic[idx] in _event_buffer:
                ghost_notes[idx] = 1 
            elif a_logic[idx] -12 in _event_buffer:
                ghost_notes[idx - 12] = 1
            elif a_logic[idx] -19 in _event_buffer:
                ghost_notes[idx - 19] = 1
            elif a_logic[idx] -24 in _event_buffer:
                ghost_notes[idx - 24] = 1
            elif a_logic[idx] -28 in _event_buffer:
                ghost_notes[idx - 28] = 1
            elif a_logic[idx] -43 in _event_buffer:
                ghost_notes[idx - 43] = 1
            elif a_logic[idx] -47 in _event_buffer:
                ghost_notes[idx - 47] = 1
            else:
                _errors_buffer[idx] = _errors_buffer[idx] - 1
                if _errors_buffer[idx] < wait * (-1):
                    a_towrite[idx] = a_logic[idx] * (-0.1)
        else:
            if _errors_buffer[idx] < 0:
                _errors_buffer[idx] = 0
    for i in range(89):
        if ghost_notes[i] == 0:
            _event_buffer[i] = 0
    # ---------- printing out the output vector ----------
    for idx in range(len(a_towrite)):
        if a_towrite[idx] != 0 : # non-zero numbers have meaning 
            out_n.write("\t" + str(a_towrite[idx]))
    out_n.write("\n")

def get_score():
    scoreout = open("/home/luciamarock/Dropbox/shared/dev/PitchDetector/src/integer.out", "r")
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

''' --------------------------------- NOT USED ------------------------------------- '''
#cppout = genfromtxt("/home/luciamarock/Documents/cpp_tests/PitchDetector/src/monodet.out")
#cppout=n.array(cppout)
#cppout = cppout + 0.1
''' ---------------------------------------------------------------------------------- '''