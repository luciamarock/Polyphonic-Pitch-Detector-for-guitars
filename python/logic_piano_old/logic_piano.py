## note and instrument are useful to compose the name of the score file to load. 
#
# The scores are generated from the C++ algorithm and are moved to their folder by a script 
# Here we are calling the four scores and extracting the data from them using the python module genfromtxt 

import numpy as n 
from numpy import genfromtxt
import midi
import monitoring

note="Beat_It_cut" # score choice GBD_B
instrument="piano"

freq=genfromtxt("../algo_outputs/notes_piano.txt") # notes of the piano 

arg1="../appunti/visualizationTools/scores/" + instrument + "/" + note + "_filefft.out"
arg2="../appunti/visualizationTools/scores/" + instrument + "/" + note + "_filefilter.out"
arg4="../appunti/visualizationTools/scores/" + instrument + "/" + note + "_integer.out"
datafft=genfromtxt(arg1)
datafft=n.array(datafft)
data=genfromtxt(arg2)
data=n.array(data)

env=genfromtxt(arg4) # used for calculating the envelope follower 

midiscore = midi.get_score()

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
memory = [0]*89
exist = [0]*89
not_presence = [0]*89
allowance=0.0 # disciminates between noise and sound, enables the detection (based attack)
activenotes = 0
exclude = 1 # to be used when educational purposes 
i2monitor = -1 #943
j2monitor = 42

''' ------------------- plot only variables ------------------- '''

jvect = [1.4]*89
vectfft = [0]*89
vect = [0]*89

''' ------------------- end plot only vars ------------------- '''

## Portion is used to establish the duration of the plot 
#
# It is defined as a fraction of the duration of the audiofile 
# If we want to analyze a precise number of chunks, we need to insert that integer number 
portion = int(len(midiscore)/1.)
scarto = 0
for i in range (portion):   # loop over the chunks (their analysis vectors)
    bluemax = 0
    blueidx = -1
    fftmax = 0
    # song time (used in plot)
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
            """ START CONDITIONS """
            if j<70 and vectnote[j+12] > vectnote[j]*firstharmth and vectnote[j+19] > vectnote[j]*scndharmth:
                not_presence[j] = 0
                if vectnote[j] > energymin:
                    vectplot[j] = totalenergy   
                    memory[j] = totalenergy 
                else:
                    vectplot[j] = 0 
                    memory[j] = 0
                    exist[j] = 0
            elif j<70 and vectnote[j] > energymin and vectnote[j+12] > vectnote[j]*firstharmth and NOpattern:   
                not_presence[j] = 0
                vectplot[j] = totalenergy
                memory[j] = totalenergy
            elif j >= 70 and j < 77 and vectnote[j+12] > vectnote[j]*firstharmth: # firstharmth  # rtfithreshold
                not_presence[j] = 0
                if vectnote[j] > energymin:
                    vectplot[j] = totalenergy   
                    memory[j] = totalenergy 
                else:
                    vectplot[j] = 0 
                    memory[j] = 0
                    exist[j] = 0
            elif j>= 77 and vectnote[j] > energymin:
                not_presence[j] = 0
                vectplot[j] = totalenergy   
                memory[j] = totalenergy 
            elif memory[j] > 0:
                vectplot[j] = memory[j]
                if not_presence[j] < 4:
                    not_presence[j] = not_presence[j] + 1
                if j != blueidx or not_presence[j] > 3:
                    memory[j] = 0
                    not_presence[j] = 0
            elif exist[j] > 3 and exclude == 0:
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
                vectgrey[j] = vectplot[j] # vectgrey non esiste in C++
                vectplot[j] = 0

## calculating the attack based on the enevelopes at the current chunck and the one before 
    attack=env[i]/envprev*0.5
    envprev=env[i]
## using the attack to enable / disable the allowance 
    if attack > 2.72/noise_threshold and env[i] > noise_threshold/100.:  # attack > 1.46
        allowance=env[i]
        time_from_beginning = (i+1)/44100. * 256
    if env[i]<allowance*0.1: # aggiungere or con il valore assoluto di env[i] < noise_threshold/100.
        allowance=0.0

    activenotes = 0 
    for k in range(len(vectplot)): # in C++ questo e' stato fatto nel loop precedente 
        if vectplot[k] > 0:
            activenotes = activenotes + 1
    # diagnosi, sta anche in C++
    if i == i2monitor:
        monitoring.diagnose() # pass some arguments 

    midi.evaluation(i+1,midiscore[i],vectplot,vect,vectnote,bluemax*scndharmth*energymin,fftmin) # cppout[i]

## Resetting the variables 
    vectcond = [1.5]*89
    jvect = [1.4]*89
    vectmono = [0]*89
    vectnote = [0]*89
    vectplot = [0]*89
    vectgrey = [0]*89

midi.out_f.close()
midi.out_n.close()
midi.out_s.close()
