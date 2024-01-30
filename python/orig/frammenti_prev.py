'''
        if note:
            if vectplot[note-20] == 0:
                _event_buffer[note - 20] = _event_buffer[note - 20] + 10



            if note + 20 in scoreout: # the note is preset in the score 
                out_n.write("\t" + str(note + 20))
                _event_buffer[note] = 100
            elif note + 1 in scoreout: # this could be a second harmonic 
                seconds.append(note + 20)
            elif note + 8 in scoreout and note + 27 in seconds: # this could be a first harmonic
                firsts.append(note + 20)
        elif _event_buffer[note] < 100 and _event_buffer[note]/10 > wait:
            out_n.write("\t!" + str(note + 20))
            _event_buffer[note] = 0

'''
import matplotlib.pyplot as plt
from numpy import genfromtxt
import math
import random

instrument="piano"
note="Beat_It_cut"

MOVING_AVARAGE_P = 0.1
ATTACK_FACTOR = 0.6
average = [0.] * 20

def rotate(average,new_value):
    azz = 0.
    for i in range(len(average)-1):
        average[i] = average[i+1]
        azz = azz + average[i+1]
    average[len(average)-1] = new_value
    azz = (azz + new_value)/len(average)
    return average, azz

arg4="./scores/" + instrument + "/" + note + "_integer.out"
env=genfromtxt(arg4)
moving_avg = []
moving_avg_mia = []
threshold = []
value = 0.05
real_signal = []
for i in range(1900):
    real_signal.append(random.uniform(0.003, 0.006))

for i in range(len(env)):
    real_signal[i] = real_signal[i]+env[i]

for i in range(len(real_signal)):
    p = MOVING_AVARAGE_P;
    if real_signal[i] > value:
        p = p * ATTACK_FACTOR
    value = p * real_signal[i] + (1 - p) * value
    moving_avg.append(value)
    average, value_mio = rotate(average, real_signal[i])
    moving_avg_mia.append(value_mio)
    #th = 1/math.log(pow(value,2)+3)
    th = pow(real_signal[i],2) / value_mio
    #th = pow(value_mio,2) / value
    threshold.append(th)

plt.plot(real_signal,color="cyan")
plt.plot(moving_avg,color="red")
plt.plot(moving_avg_mia)
plt.plot(threshold)
plt.show()
