import numpy as n 
from numpy import genfromtxt
import matplotlib.pyplot as plt
from time import sleep
## nota and chitarra are useful to compose the name of the score file to load. 
#
# The scores are generated from the C++ algorithm and are moved to their folder by a script 
# Here we are calling the four scores and extracting the data from them using the python module genfromtxt 
nota="Amag_open" # previous G
# fraseG98triade ha 572 righe al 44 c'e' il si a 134 c'e' il re, a 186 si spegne il si
chitarra="poly"
arg1="./scores/" + chitarra + "/" + nota + "_filefft.out"
arg2="./scores/" + chitarra + "/" + nota + "_filefilter.out"
arg3="./scores/" + chitarra + "/" + nota + "_monodet.out"
arg4="./scores/" + chitarra + "/" + nota + "_integer.out"
datafft=genfromtxt(arg1)
data=genfromtxt(arg2)
fund=genfromtxt(arg3)
env=genfromtxt(arg4) # creo il vettore di envelope follower [i]
data=n.array(data)
datafft=n.array(datafft)

envprev=10.0 # valore precedente di envfoll serve per calcolare attack che serve per allowance usato nelle condizioni
freq=genfromtxt("./algo_outputs/notes.txt") # serve per dare peso alla detection monofonica, generato da C++
existsum=0 # serve a decidere quando la detection monofonica va presa in considerazione e quando no 
sens=0.1  
Pshp = 1.03 
Pshs = 1.025 
Pthp = 0.6*sens 
Pths = 0.7*sens 
vectmono = [0]*51
vectnote = [0]*51
memoria = [0]*51
exist = [0]*51
allowance=0.0 # distingue le parziali dal rumore (si basa su attack)

''' ------------------- le prossime variabili servono solo al fine di visualizzazione ------------------- '''
f=open("./algo_outputs/names.txt","r")
labels=f.readlines()
names = []
for k in range(len(labels)):
    name = str(labels[k]).split('\n')
    names.append(name[0])
pause=0.09
condizione=0
dummywarn=0
vectcond = [1.5]*51
jvect = [1.4]*51
vectplot = [0]*51
vectfft = [0]*51
vect = [0]*51
existplot = [0]*51
baseline = [0]*51
''' ------------------- fine variabili di visualizzazione ------------------- '''

print(' ---- this file is {} rows long ----'.format(len(data)))
print('  ')
## Portion is used to establish the duration of the plot 
#
# It is defined as a fraction of the duration of the audiofile 
# If we want to analyze a precise number of chunks, we need to insert that integer number 
portion = int(len(data)/4)   # tutto il file corrisponde a len(data)
scarto = 0
for i in range (23):    # qui si regola la durata del plot, portion sarebbe una porzione di tutto il file
                        # un numero intero corrisponde a nchunk
    if allowance > 0. and scarto == 0:        
        scarto = i - 2
    if allowance > 0.:
        time = (i-scarto) * 256 / 44100. * 1000
    else:
        time = 0.
## For each chunk (i) we iterate over the 51 notes (j)
#
# data.T is data transposed meaning the 51 possible notes \n
# I create the vector of relative maximums vectnote and vectplot (used only for plotting) and then I 
# check the memoria variable to evaluate if increasing or not the stability index exist
    for j in range(len(data.T)):
        if (j>0 and j<(len(data.T)-1)):
            if (data[i,j]-data[i,j-1]>0 and data[i,j]-data[i,j+1]>0):
                vectnote[j] = data[i,j]/170 #se e un punto di massimo mi scrivo il valore RTFI  
                vectplot[j] = data[i,j]/170 #questo serve solo per il plot
                jvect[j] = j
                if (memoria[j] > 0 and exist[j]<4): 
                    exist[j]=exist[j]+1
## Then I iterate againg over the possible notes 
#
# for evaluating the various conditions 
    for j in range(len(data.T)):
        vect[j]=data[i,j]/170 #questo serve solo per il plot
        vectfft[j]=datafft[i,j]*3.75   
        ''' a causa della seguente condizione, a partire dal E330 non posso piu' contare sulla monodet'''
        if (abs(freq[j]-fund[i])<0.01 and fund[i]<320): 
            vectmono[j]=data[i,j]/170 #se la detection monofonica rileva note plausibili ci scrivo il valore della fft
        # CONDIZIONE 1 basata sugli armonici 
        if (j<(len(data.T)-20) and vectnote[j]>0.0 and allowance > 0.0 and vectnote[j+12]<vectnote[j]*Pshp*(1.0+Pthp) and vectnote[j+12]>vectnote[j]*Pshp*(1.0-Pthp) and vectnote[j+19]<vectnote[j]*Pshs*(1.0+Pths) and vectnote[j+19]>vectnote[j]*Pshs*(1.0-Pths)):
            vectnote[j]=data[i,j]/170 # valutare se e il caso di correggere questa assegnazione sulla base di un vectmono adiacente
            memoria[j]=data[i,j]/170
            condizione=1
            vectcond[j]=condizione
            if (exist[j]==4 and dummywarn==0):                
                print('--> nota {} fissata con condizione 1 @ nchunk = {}'.format(names[j],str(i+1)))
                #print('--> j = {}'.format(str(j)))
                dummywarn=1
            ''' ESPERIMENTO SU CONDIZIONE 1 (condizione 11)'''
            if (j<19 and exist[j]<2):
                if (datafft[i,j]<datafft[i,j+19]/6.0 or datafft[i,j+19]<datafft[i,j]/6.0):
                    vectnote[j]=0.0
                    memoria[j]=0.0
                    condizione=11
                    vectcond[j]=condizione
                    print('{}. ammazzato {} con la condizione 11' .format(str(i+1),str(names[j])))
        # CONDIZIONE 2    basata sull'algoritmo di detection della waveform
        elif (j<(len(data.T)-20) and existsum<5 and vectmono[j]>0.0 and allowance > 0.0 and vectnote[j+12] < vectmono[j]*Pshp*(1.0+Pthp) and vectnote[j+12]>vectmono[j]*Pshp*(1.0-Pthp)): # and vectnote[j+19]>0.03
            ''' STAMPA MOTIVI DECADIMENTO COND 1 ''' # existsum fa in modo che la det temp viene ignorata quando viene riconosciuta la prima nota + 1 un'altra sospettata di esistere 
            if (vectnote[j]>0.0 and vectnote[j+12]>=vectnote[j]*Pshp*(1.0+Pthp)):
                print('{}. primo armonico di {} sfora la soglia superiore' .format(str(i+1),names[j]))
            elif (vectnote[j+12]>0.0 and vectnote[j+12]<=vectnote[j]*Pshp*(1.0-Pthp)):
                print('{}. primo armonico di {} sfora la soglia inferiore' .format(str(i+1),names[j]))
            elif (vectnote[j]>0.0 and vectnote[j+19]>=vectnote[j]*Pshs*(1.0+Pths)):
                print('{}. secondo armonico di {} sfora la soglia superiore' .format(str(i+1),names[j]))
            elif (vectnote[j+19]>0.0 and vectnote[j+19]<=vectnote[j]*Pshs*(1.0-Pths)):
                print('{}. secondo armonico di {} sfora la soglia inferiore' .format(str(i+1),names[j]))
            
            vectnote[j]=data[i,j]/170
            memoria[j]=data[i,j]/170
            condizione=2
            vectcond[j]=condizione
         
        
        # CONDIZIONI 3 e 4 per note acute
        elif (j>27 and j<38 and vectnote[j]>0.0 and vectnote[j]>data[i,j-12]/170*1.15 and vectnote[j]>data[i,j-19]/170*1.15 and allowance > 0.0 and vectnote[j+12]>vectnote[j]*0.75 and vectnote[j+12]<vectnote[j]*1.25):            
            vectnote[j]=data[i,j]/170
            memoria[j]=data[i,j]/170
            condizione=3
            vectcond[j]=condizione
            if (exist[j]==4 and dummywarn==0):                
                print('--> nota {} fissata con condizione 3 @ nchunk = {}'.format(names[j],str(i+1)))
                #print('--> j = {}'.format(str(j)))
                dummywarn=1
        elif (j>37 and j<51 and vectnote[j]>0.0 and vectnote[j]>data[i,j-12]/170*1.15 and vectnote[j]>data[i,j-19]/170*1.15 and allowance > 0.0 and (datafft[i,j]+datafft[i,j+12]+datafft[i,j+19])>(datafft[i,j-12]+datafft[i,j]+datafft[i,j+7])*0.75 and (datafft[i,j]+datafft[i,j+12]+datafft[i,j+19])>(datafft[i,j-19]+datafft[i,j-7]+datafft[i,j])*0.75):
            vectnote[j]=data[i,j]/170
            memoria[j]=data[i,j]/170
            condizione=4
            vectcond[j]=condizione
            if (exist[j]==4 and dummywarn==0):                
                print('--> nota {} fissata con condizione 4 @ nchunk = {}'.format(names[j],str(i+1)))
                #print('--> j = {}'.format(str(j)))
                dummywarn=1
                
                ''' CONDIZIONI POLIFONICHE '''        
        
        elif(j>6 and j<39 and vectnote[j]>0.93*(vectnote[j-7]+vectnote[j+5])*0.5 and exist[j-7]>0 and datafft[i,j+12]>0.66*datafft[i,j-7]): 
            vectnote[j]=data[i,j]/170
            memoria[j]=data[i,j]/170
            ratio2=(datafft[i,j+12]+datafft[i,j+19])*0.5/datafft[i,j-7]
            ratio1=datafft[i,j+12]/datafft[i,j-7]
            if exist[j]<4:
                print('QUINTA @ nchunk = {} --> {}'.format(str(i+1),names[j]))
                #print('con 2 armonici = {}, con uno = {}'.format(round(ratio2,3),round(ratio1,3)))
            condizione = 5
            vectcond[j]=condizione
        elif (j>15 and j<47 and ((exist[j-16]>0 and exist[j-4]>0 and exist[j+3]>0 and vectnote[j]>0.93*(vectnote[j-16]+vectnote[j-4]+vectnote[j+3])/3.) or (exist[j-15]>0 and exist[j-3]>0 and exist[j+4]>0 and vectnote[j]>0.93*(vectnote[j-15]+vectnote[j-3]+vectnote[j+4])/3.))):
            if exist[j]<4:
                print('TERZA @ nchunk = {} --> {}'.format(str(i+1),names[j]))
            vectnote[j]=data[i,j]/170
            memoria[j]=data[i,j]/170
            condizione = 6
            vectcond[j]=condizione
       
        else:            # commento il primo if elif perche' si riferisce alla condizione monofonica, invece adesso io studio le cond polifoniche
            #if (vectmono[j]>0.03 and vectnote[j+12] >= vectmono[j]*Pshp*(1.0+Pthp)):
                #print('{}. cond 0, primo armonico di {} sfora la soglia superiore' .format(str(i+1),names[j]))
            #elif (vectmono[j]>0.03 and vectnote[j+12]>0.0 and vectnote[j+12]<=vectmono[j]*Pshp*(1.0-Pthp)):
                #print('{}. cond 0, primo armonico di {} sfora la soglia inferiore' .format(str(i+1),names[j]))
                
            vectnote[j]=0            
            if (memoria[j]>0.03):
                vectnote[j]=memoria[j]
                memoria[j]=0
                condizione = 10  # recupero grazie a memoria
                vectcond[j]=condizione
                if (exist[j] < 4):
                    exist[j]=0
                
            elif (exist[j]>3 and datafft[i,j]*3.75 > 0.03 and data[i,j]-data[i,j-1]>0 and data[i,j]-data[i,j+1]>0):
                vectnote[j]=data[i,j]/170
                memoria[j]=data[i,j]/170
                
            else:
                exist[j]=0
## calculating the attack based on the enevelopes at the current chunck and the one before 
    attack=env[i]/envprev*0.5
    envprev=env[i]
## using th attack to enable / disable the allowance 
    if attack > 1.66:
        allowance=env[i]
        print(' ')
        print('attack = {} @ nchunk = {}' .format(str(attack), str(i+1)))
    if env[i]<allowance*0.1:
        allowance=0.0
## plot-only variables 
    minimo=min(vect)
    for w in range(len(freq)):
        baseline[w]=minimo
    existsum=0    
    for z in range(len(existplot)):
        existplot[z]=exist[z]/10.
        existsum=existsum+exist[z]
    sleep(pause)
    plt.clf()
    plt.plot(freq,baseline,'--',color='black')
    for k in range(len(vectcond)):
        if vectcond[k] != 1.5:
            plt.annotate(str(vectcond[k]),(freq[k],1.5)) # annotation value, (coordinates)
        if jvect[k] != 1.4:
            plt.annotate("j"+str(jvect[k]),(freq[k],1.4))
            plt.annotate(int(freq[k]),(freq[k],1.35))
    plt.plot(freq,vect,color='cyan')
    for k in range(len(vectplot)):
        if vectplot[k]>0 and vectfft[k]>0.03:
            plt.annotate(str(names[k]),(freq[k],vect[k]))
    plt.plot(freq,vect,'o',color='blue')
    plt.plot(freq,vectfft,color='orange')
    plt.plot(freq,vectfft,'o',color='yellow')
    for k in range(len(vectnote)):
        if vectnote[k]>0:
            plt.annotate(str(vectfft[k]),(freq[k],vectfft[k]))
    plt.plot(freq,vectmono, 'D',color='red')
    plt.text(1000, 1.9, "nchunck = " + str(i+1), {'color': 'black', 'fontsize': 16})
    plt.text(1000, 1.75, "condizione " + str(condizione), {'color': 'black', 'fontsize': 16})
    plt.text(700, 1.9, "time = " + str(round(time)) + " ms", {'color': 'black', 'fontsize': 16})
    plt.text(100, 1.9, "attack = " + str(round(attack,3)), {'color': 'black', 'fontsize': 16})
    plt.text(100, 1.75, "existsum =  " + str(existsum), {'color': 'black', 'fontsize': 16})
    plt.plot(freq,vectnote, color='green')
    plt.plot(freq,memoria, 'o',color='green')
    plt.plot(freq,existplot,'d', color='black')
    for k in range(len(vectnote)):
        if vectnote[k]>0:
            plt.annotate(str(freq[k]),(freq[k],existplot[k]))
    plt.ylim(0.03,2.0) #0.03,2.0
    #plt.semilogx()
    #print(fund[i])
## Resetting the variables 
    condizione=0
    vectplot = [0]*51
    vectcond = [1.5]*51
    jvect = [1.4]*51
    vectmono = [0]*51
    vectnote = [0]*51
    plt.pause(pause) 
