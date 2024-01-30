import numpy as n 
from numpy import genfromtxt
import matplotlib.pyplot as plt
from time import sleep
import sys
## note and instrument are useful to compose the name of the score file to load. 
#
# The scores are generated from the C++ algorithm and are moved to their folder by a script 
# Here we are calling the four scores and extracting the data from them using the python module genfromtxt 
note="Beat_It_cut" # score choice GBD_B

names = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]

instrument="piano"
freq=genfromtxt("./algo_outputs/notes_piano.txt") # notes of the piano 
arg1="./scores/" + instrument + "/" + note + "_filefft.out"
arg2="./scores/" + instrument + "/" + note + "_filefilter.out"
arg4="./scores/" + instrument + "/" + note + "_integer.out"
datafft=genfromtxt(arg1)
data=genfromtxt(arg2)
env=genfromtxt(arg4) # used for calculating the envelope follower 
data=n.array(data)
datafft=n.array(datafft)

''' --------------------------------- NOT USED ------------------------------------- '''
#cppout = genfromtxt("/home/luciamarock/Documents/cpp_tests/PitchDetector/src/monodet.out")
#cppout=n.array(cppout)
#cppout = cppout + 0.1
''' ---------------------------------------------------------------------------------- '''
scoreout = open("/home/luciamarock/Dropbox/shared/dev/PitchDetector/src/integer.out", "r")
#scoreout = open("/home/luciamarock/Documents/AudioAnalyzer/algo_outputs/integer.out", "r")
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


envprev=10.0 # memory of the previous value of the env follower (used for calculating attack and allowance)
noise_threshold = 3.0   # 1 to 10
sens = 5.0              # 1 to 10
firstharmth=4.3/sens
scndharmth = 3.999/sens 
rtfithreshold = 4.601162791/sens
stability_threshold = 3.5 / sens

vectgrey = [0]*89
vectnote = [0]*89
vectplot = [0]*89
_event_buffer = [0]*89
_errors_buffer = [0]*89
memory = [0]*89
exist = [0]*89
not_presence = [0]*89
allowance=0.0 # disciminates between noise and sound, enables the detection (based attack)
activenotes = 0

''' ------------------- plot only variables ------------------- '''

pause=0.09
dummywarn=0
jvect = [1.4]*89
vectfft = [0]*89
vect = [0]*89
baseline = [0]*89
redline = [0]*89
scndharmthline = [0]*89
rtfithresholdline = [0]*89

''' ------------------- end plot only vars ------------------- '''
exclude = 1 # to be used when educational purposes 
i2monitor = -1 #943
j2monitor = 42
out_f = open("vectplot_printout.txt", "w")
out_n = open("output_evaluated_printout.txt", "w")
out_s = open("midiscore_printout.txt", "w")

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

def print_folding(segment,all_data):    
    energy_vect = []
    for idx in range(1,13):
        counter = 0
        newidx = idx
        all_harm_energy = 0
        while newidx < 88:
            all_harm_energy = all_harm_energy + all_data[segment,newidx]
            newidx = newidx + 12
            counter = counter + 1
        value = all_harm_energy/counter
        energy_vect.append(round(value,2))
    print(energy_vect)
    print(names)

def print_correspondence(index):
    q,r = divmod(index,12)
    note_name = names[r-1]
    print("j = {}, corresponding to {} at {}Hz, MIDI {}".format(index,note_name, round(freq[index],2),index+20))
    print("")

#print(' ---- this file is {} rows long ----'.format(len(data)))
print('  ')
## Portion is used to establish the duration of the plot 
#
# It is defined as a fraction of the duration of the audiofile 
# If we want to analyze a precise number of chunks, we need to insert that integer number 
portion = int(len(midiscore)/1.)   # all the file corresponds to len(data)
plot_duration = 390
scarto = 0
for i in range (portion):
    bluemax = 0
    blueidx = -1
    fftmax = 0

    if allowance > 0. and scarto == 0:        
        scarto = i - 2
    if allowance > 0.:
        time = (i-scarto) * 256 / 44100. * 1000
    else:
        time = 0.
## For each chunk (i) we iterate over the 89 notes (j)
#
# data.T is data transposed meaning the 89 possible notes \n
# I create the vector of relative maximums vectnote and then I 
# check the memory variable to evaluate if increasing or not the stability index exist
    for j in range(len(data.T)):
        vect[j]=data[i,j]/170 # only for plotting purposes, in C++ this does not exist 
        vectfft[j]=datafft[i,j]*3.75 # in C++ vectfft does not exist, datafft is already scaled 
        if vectfft[j] > fftmax:
            fftmax = vectfft[j]
        if (j>0 and j<(len(data.T)-1)): # in C++ this is not used because the loop is already between 0 and NNOTES - 1
            if (data[i,j]-data[i,j-1]>0 and data[i,j]-data[i,j+1]>0):
                vectnote[j] = data[i,j]/170 # take note of the local maximum point, in C++ data is dataRTFI and it's already scaled
                if vectnote[j] > bluemax:
                    bluemax = vectnote[j]
                    blueidx = j
                jvect[j] = j                        # this is only for plotting purposes  
                if (memory[j] > 0 and exist[j]<4): 
                    exist[j]=exist[j]+1
            else:
                memory[j] = 0
                exist[j] = 0
                # in C++ viene messo a zero anche vectbote perche' non viene resettato alla fine (come qui)

## Then I iterate againg over the possible notes 
#
# for evaluating the various conditions poses 
    energymin = bluemax*rtfithreshold
    fftmin = fftmax*firstharmth
    for j in range(len(data.T)):
        if vectnote[j] > 0 and allowance > 0:  
            NOpattern = False
            if j < 70:
                if vectnote[j+6] > energymin or vectnote[j+8] > energymin:
                    if activenotes > 0:
                        NOpattern = True
                avfft = (vectfft[j] + vectfft[j+12] + vectfft[j+19])/3.
                avrfti = (vectnote[j] + vectnote[j+12] + data[i,j+19]/170)/3.
            elif j >= 70 and j < 77:
                avfft = (vectfft[j] + vectfft[j+12])/2.
                avrfti = (vectnote[j] + vectnote[j+12] )/2.
            else:
                avfft = vectfft[j]
                avrfti = vectnote[j]
            totalenergy = avrfti * avfft * 2.
            if j<70 and vectnote[j+12] > vectnote[j]*firstharmth and vectnote[j+19] > vectnote[j]*scndharmth:
                not_presence[j] = 0
                if vectnote[j] > energymin:
                    #print("nchunk {}, found pattern and sufficient energy for note:".format(i+1))
                    #print_correspondence(j)
                    vectplot[j] = totalenergy   
                    memory[j] = totalenergy 
                else:
                    #print("nchunk {}, found pattern but INsufficient energy for note:".format(i+1))
                    #print_correspondence(j)
                    vectplot[j] = 0 
                    memory[j] = 0
                    exist[j] = 0
            elif j<70 and vectnote[j] > energymin and vectnote[j+12] > vectnote[j]*firstharmth and NOpattern:   
                not_presence[j] = 0
                #print("nchunk {}, polyphonic condition for note:".format(i+1))
                #print_correspondence(j)
                vectplot[j] = totalenergy
                memory[j] = totalenergy
            elif j >= 70 and j < 77 and vectnote[j+12] > vectnote[j]*firstharmth: # firstharmth  # rtfithreshold
                not_presence[j] = 0
                if vectnote[j] > energymin:
                    #print("nchunk {}, found high note pattern and sufficient energy for note:".format(i+1))
                    #print_correspondence(j)
                    vectplot[j] = totalenergy   
                    memory[j] = totalenergy 
                else:
                    #print("nchunk {}, found high note pattern but INsufficient energy for note:".format(i+1))
                    #print_correspondence(j)
                    vectplot[j] = 0 
                    memory[j] = 0
                    exist[j] = 0
            elif j>= 77 and vectnote[j] > energymin:
                not_presence[j] = 0
                #print("nchunk {}, found highest note with sufficient energy for note:".format(i+1))
                #print_correspondence(j)
                vectplot[j] = totalenergy   
                memory[j] = totalenergy 
            elif memory[j] > 0:
                #print("nchunk {}, recovered note with exist {} and not_presence = {}:".format(i+1,exist[j],not_presence[j]+1))
                #print_correspondence(j)
                vectplot[j] = memory[j]
                if not_presence[j] < 4:
                    not_presence[j] = not_presence[j] + 1
                if j != blueidx or not_presence[j] > 3:
                    memory[j] = 0
                    not_presence[j] = 0
            elif exist[j] > 3 and exclude == 0:
                #print("nchunk {}, stable j{}={}Hz, not_presence = {}".format(i+1,j,round(freq[j],2),not_presence[j]))
                #print_correspondence(j)
                vectplot[j] = totalenergy
                memory[j] = 0
                not_presence[j] = 0
            else:
                memory[j] = 0 
                exist[j] = 0
                not_presence[j] = 0
                vectplot[j] = 0
        else:
            vectplot[j] = 0
            memory[j] = 0
            exist[j] = 0 
            not_presence[j] = 0
            
    maxrfti = n.max(vectplot)  # in C++ questo e la line di sotto lo faccio nel loop precedente 
    maxidx = n.argmax(vectplot)
    AVenergymin = maxrfti*stability_threshold

    for j in range(len(vectplot)):
        if vectplot[j] > 0 and vectplot[j] < AVenergymin: #  or vectnote[j] < vectnote[maxidx]*0.9
            if exist[j] < 4:
                #print("nchunk {}, removing non stable note:".format(i+1))
                #print_correspondence(j)
                vectgrey[j] = vectplot[j] # vectgrey non esiste in C++
                vectplot[j] = 0
                #exist[j] = 0
            #memory[j] = 0

## calculating the attack based on the enevelopes at the current chunck and the one before 
    attack=env[i]/envprev*0.5
    envprev=env[i]
## using the attack to enable / disable the allowance 
    if attack > 2.72/noise_threshold and env[i] > noise_threshold/100.:  # attack > 1.46
        allowance=env[i]
        time_from_beginning = (i+1)/44100. * 256
        #print(' ')
        #print('--> attack = {} @ nchunk = {} ({} sec)' .format(str(attack), str(i+1), round(time_from_beginning,3)))
        #print("")
    if env[i]<allowance*0.1: # aggiungere or con il valore assoluto di env[i] < noise_threshold/100.
        allowance=0.0

    activenotes = 0 
    for k in range(len(vectplot)): # in C++ questo e' stato fatto nel loop precedente 
        if vectplot[k] > 0:
            activenotes = activenotes + 1
    # diagnosi, sta anche in C++
    if i == i2monitor:
        print("----------- i = {} -----------".format(i))
        print_correspondence(j2monitor) # j = 19 (key number piano) = MIDI note number 39 = Eb2 = 77.78 Hz
        #print(vectplot[j2monitor])
        #print_folding(i2monitor,data)
        print(" energymin = {}, \n firstharm = {}, \n secondharm = {}".format(energymin,bluemax*firstharmth,bluemax*scndharmth))
        plt.plot(freq,vect,"x")
        plt.plot(freq,vect,"--",color="cyan")
        th_line = []
        fft_line = []
        for idx in range(len(vectnote)):
            th_line.append(bluemax*scndharmth)
            fft_line.append(fftmin)
        plt.plot(freq,th_line)
        plt.plot(freq,vectfft,color="black")
        plt.plot(freq,fft_line)
        plt.show()
        print("")
        print(_event_buffer)
        print("-----------------------")
    evaluation(i+1,midiscore[i],vectplot,vect,vectnote,bluemax*scndharmth*energymin,fftmin) # cppout[i]
## plot-only variables 
    '''
    for w in range(len(freq)):
        baseline[w]=bluemax*firstharmth
        redline[w]=AVenergymin
        scndharmthline[w]=bluemax*scndharmth
        rtfithresholdline[w]=energymin
    sleep(pause)
    plt.clf()
    plt.plot(freq,baseline,'--',color='blue')
    plt.plot(freq,redline,'--',color='red')
    plt.plot(freq,scndharmthline,'--',color='grey')
    plt.plot(freq,rtfithresholdline,'--',color='cyan')
    for k in range(len(vectplot)):
        if jvect[k] != 1.4 and vectnote[k] > rtfithresholdline[k]:
            plt.annotate("j"+str(jvect[k]),(freq[k],1.4))
            plt.annotate(int(freq[k]),(freq[k],1.35))
            q,r = divmod(k,12)
            plt.annotate(str(names[r-1]),(freq[k],1.3))
        if exist[k] > 0:
            plt.annotate(exist[k],(freq[k],1.15))
        if vectplot[k] > 0:
            q,r = divmod(k,12)
            plt.annotate(names[r-1],(freq[k],1.6))
    q,r = divmod(blueidx,12)
    plt.annotate(str(names[r-1]) + " = " + str(round(freq[blueidx],2)),(freq[blueidx],1.2))
    plt.plot(freq,vect,color='cyan')
    plt.plot(freq,vect,'o',color='blue')
    #plt.plot(freq,vectfft,color='orange')
    #plt.plot(freq,vectfft,'o',color='yellow')
    plt.text(1300, 1.9, "nchunck = " + str(i+1), {'color': 'black', 'fontsize': 16})
    plt.text(2000, 1.9, "env = " + str(round(env[i],3)), {'color': 'black', 'fontsize': 16})
    plt.text(2800, 1.9, "attack = " + str(round(attack,3)), {'color': 'black', 'fontsize': 16})
    plt.text(3600, 1.9, "activenotes = " + str(activenotes), {'color': 'black', 'fontsize': 16})
    plt.text(700, 1.9, "time = " + str(round(time)) + " ms", {'color': 'black', 'fontsize': 16})
    plt.text(50,1.9,note + ".wav",{'color': 'black', 'fontsize': 16})
    plt.plot(freq,vectnote, 'D',color='green')
    plt.plot(freq,vectgrey,color='grey') #, 'D'
    plt.plot(freq,memory,'D',color='red')
    plt.plot(freq,vectplot,color='red') #, 'D'
    plt.plot(freq,cppout[i],"--",color="black")
    plt.ylim(0.03,2.0) #0.03,2.0
    '''
## Resetting the variables 
    vectcond = [1.5]*89
    jvect = [1.4]*89
    vectmono = [0]*89
    vectnote = [0]*89
    vectplot = [0]*89
    vectgrey = [0]*89
    #plt.pause(pause) 
out_f.close()
out_n.close()
out_s.close()
