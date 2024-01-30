import matplotlib.pyplot as plt
from time import sleep

names = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]
pause=0.09
dummywarn=0
baseline = [0]*89
redline = [0]*89
scndharmthline = [0]*89
rtfithresholdline = [0]*89

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

def print_correspondence(index,freq):
    q,r = divmod(index,12)
    note_name = names[r-1]
    print("j = {}, corresponding to {} at {}Hz, MIDI {}".format(index,note_name, round(freq[index],2),index+20))
    print("")

def diagnose(i,energymin,bluemax,firstharmth,scndharmth,vect,vectnote,vectfft,fftmin,freq,_event_buffer):    
        print("----------- i = {} -----------".format(i))
        #print_correspondence(j2monitor) # j = 19 (key number piano) = MIDI note number 39 = Eb2 = 77.78 Hz
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

def make_graph(i,freq,bluemax,AVenergymin,energymin,firstharmth,scndharmth,vectplot,vectnote,jvect,vect,exist,blueidx,env,attack,activenotes,vectgrey,memory,cppout,time,note):
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