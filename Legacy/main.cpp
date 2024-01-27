/**
 * @file main.cpp
 * @brief Description of the main program.
 *
 * 
 *Envelope Calculation:
 *  - The loop calculates the envelope of the current chunk. The envelope is a smooth curve that captures the shape of the audio waveform. It's often used to emphasize the overall shape or magnitude of a signal.
 *  - The calculated envelope value is used in subsequent calculations and is written to an output file (`integer.out`).
 *
 *FFT (Fast Fourier Transform):
 *  - The loop performs FFT on the current chunk using the `fft_funct` function. FFT is a mathematical algorithm that transforms a time-domain signal (in this case, an audio chunk) into its frequency-domain representation.
 *  - The FFT result is stored in the `myfft_buffer` array for further analysis and is also used to calculate an averaged value, which is written to an output file (`filefft.out`).
 *
 *RTFI Calculation:
 *  - The loop calculates the Relative Temporal Feature Intensity (RTFI) for each RTFI note within the current chunk.
 *  - It iterates over the samples in the chunk and performs calculations involving coefficients, input audio data (`buf`), and intermediate arrays (`rey`, `imgy`, `pry`, `iry`, `energy`).
 *
 *Monophonic Detection:
 *  - The loop performs monophonic detection on the current chunk. Monophonic detection involves identifying the dominant or primary note being played in the audio signal. The loop iterates over a range of possible note frequencies and calculates a "capture" value for each note's wavelength.
 *  - The note frequency that produces the maximum capture value is considered the detected monophonic note for the chunk. The detected note frequency is recorded in an output file (`monodet.out`).
 *  - The calculated RTFI values are written to an output file (`filefilter.out`).
 *
 *
 *
 * @author luciamarock
 * @date August 7th, 2023
 */
#include <stdio.h>
#include <stdlib.h>
#include <sndfile.h>
#include <unistd.h>
#include "streamer.h"
#include "resonators.h"
#include <math.h>
#include "fft_funct.h"
#include <fftw3.h>
#define N 512

int main()
    {
    SNDFILE *sf;
    SF_INFO info;
    int sampvect = N/2; 
    int num, num_items;
    int *buf;
    int f,sr,c;
    int i,j;
    float scaling = 2147483648.0;
    FILE *myfft;
    FILE *monodet;
    FILE *myfile;
    FILE *integral;
    // instrument - related parameters 
    float tet  = pow(2.0, 1.0/(1.0*12.0));
    float f0 = 77.782; // piano = 25.9565436  / guitar = 77.782
    int nnotes = 51;  // piano = 89  / guitar = 51
    int nharms = 70;  // piano = 108  / guitar = 70
    char filename[] = "Cddim";  // used by the script (called at the end of this main program)
    
    /** sf is the pointer to the .wav file, library sndfile is used to open the WAV file. */
    info.format = 0;
    sf = sf_open("./audioFiles/poly/Cddim.wav",SFM_READ,&info); // piano = piano/Dmaj4  /  guitar = poly/Amag_open
    if (sf == NULL)
        {
        printf("Failed to open the file.\n");
        exit(-1);
        }
    /* Print some of the info, and figure out how much data to read. */
    f = info.frames;
    sr = info.samplerate;
    c = info.channels;
    num_items = f*c;
    
    /* Allocate space for the data to be read, then read it. */
    buf = (int *) malloc(num_items*sizeof(int));
    num = sf_read_int(sf,buf,num_items);
    sf_close(sf);
        
    /** coefficients is a tuple returned by the init function of resonators.cpp
     * the tuple contains 3 coefficients for calculating the RTFI resonators and the list 
     * of notes which are the center frequency of the resonators */
    Tuple coefficents =init(sr, f0, nnotes, tet); 
    /** The samples[] vector contains the number of samples that describe an entire wavelength associated with each RTFI note 
     * at the specific Sampling Frequency, 
     * this is used later on in the mono detection algorithm */
    int samples[nnotes];
    for (i=0; i<nnotes; ++i)
    {
        samples[i]=int(round(sr/coefficents.d[i]));
    }
    
    /** nchunks is the number of chunks contained in the read audio file 
     * and it is received from function chunker() in module streamer.cpp \n
     It bases on the sampvect which is hard-coded to be 256 (N/2) samples*/
    int nchunks;        
    nchunks = chunker(sampvect,num);
    printf("nchunks = %d \n", nchunks);
    float duration = nchunks * sampvect / (float)sr;
    printf("buffer duration = %f seconds \n", duration);
    
    /* writing waveform in a file & temporal detection & envelope follower*/
    float chunkmt[sampvect]={0};
    float chunkmd[sampvect]={0};
    float chunkmu[sampvect]={0};
    float current[sampvect];
    float integer=0.0;
    float container[sampvect*3];
    float myfft_buffer[sampvect*4];
    float fftcopy[sampvect*4];
    
    monodet = fopen("monodet.out","w");
    integral = fopen("integer.out","w");    
    myfile = fopen("filefilter.out","w");
    myfft = fopen("filefft.out","w");
    
    float rey[sampvect];
    float imgy[sampvect];
    float pry[nnotes]={0};
    float iry[nnotes]={0};
    float energy[sampvect];
    float RTFI;
    int w;
    /* Starting the real analyzer in a loop for each chunk of the input file, when in real-time 
     * this should be the algorithm cycle which bases on each input buffer  */
    for (i=0; i<nchunks; ++i)
    {
     integer=0.0;
     /** Iterating on the input buffer (of dimension 256 samples) in order to build the vectors to be analyzed, 
      * the real data are contained in the vector buf which represent the entire audio file; the samples of the buf 
      * vector are always scaled by a factor of 2147483648 which is hard-coded \n 
      The vector container[] is made of the concatenation of three consecutive buffers and it is used for the mono detection; 
      * its length is designed taking into account the maximum wavelength of the guitar which is at about 82 Hz \n
      Vector myfft_buffer[] is used for the computation of the FFT with my algorithm, it is composed by the last 4 buffers 
      * thus bringing the total amount of he vector equal to 1024 samples, so the fft is calculated on this vector. The fft 
      * is not really used to find the peaks, in fact we should have a calculation vector of 8192 to discriminate for real the partials 
      * at lowest frequencies, but it still can be relied on to find the correct amplitudes to the partials since the RTFIs take time 
      * to reflect the real amplitude of the partials, in the future the fft with parabolic interpolation can also be used for the tracking of 
      * bendings on th guitar. \n 
      * Finally integer is used to calculate the envelope of the buffers, it gets printed on a file called integer.out */
     for (j = 0; j < sampvect; ++j)
        {
         container[j]=chunkmd[j];
         container[j+sampvect]=chunkmu[j];
         container[j+(2*sampvect)]=buf[j+(i*sampvect)]/scaling; 
         current[j]=buf[j+(i*sampvect)]/scaling;
         myfft_buffer[j]=chunkmt[j];
         myfft_buffer[j+sampvect]=chunkmd[j];
         myfft_buffer[j+2*sampvect]=chunkmu[j];
         myfft_buffer[j+3*sampvect]=current[j];
        integer=integer+sqrt(pow(current[j],2)+pow(chunkmu[j],2)+pow(chunkmd[j],2));  // integer calculation
        chunkmt[j]=chunkmd[j];
        chunkmd[j]=chunkmu[j];        
        chunkmu[j]=buf[j+(i*sampvect)]/scaling;      
        }
     
     fprintf(integral,"%f ", integer/sampvect); 
     fprintf(integral,"\n");
     /** Next the fft_funct() is called which calculates the fft on the same vector that is passed to */
     fft_funct(myfft_buffer, 4*sampvect, tet, f0, nharms, sr);
     /** We then consider an averaged value with the former fft calculation and we print the values to the file filefft.out*/
     for (w = 0; w < nharms; ++w)
                {
                if (w==nharms-1)
                    {
                    fprintf(myfft,"%f",(myfft_buffer[w]+fftcopy[w])/2.0);
                    fprintf(myfft,"\n");
                    fftcopy[w]=myfft_buffer[w];
                    }
                else{
                    fprintf(myfft,"%f",(myfft_buffer[w]+fftcopy[w])/2.0);
                    fprintf(myfft,"\t");
                    fftcopy[w]=myfft_buffer[w];
                    }
                }
     
     /*mono detection: detect the wavelength which maximize the sum of two consecutive peaks*/
     float detect=0.0;
     int counter;
     int n=0;
     int k=0;
     int steps;
     float maxi;
     float capture;
     /** In the same loop of the RTFI calculation we perform also the monophonic detection. \n
      The loop is on the RTFI frequencies and for the monophonic detection there is another sub-loop that searches inside the container[] vector
      summing up the 3 samples at distance samples[k] which is the wavelength (in samples) of the current note (RTFI frequency). For each note 
      the maximum sum is memorized and then it is registered if superior of any other previous maximum. At the en of the main loop the wavelength
      * which gave he maximum sum remains registered so we can state that was the monophonic note which was detected. This algorithm might suffer 
      * spurious spikes in the waveform and it works with clean waveforms at best and with a rapid dacay  */
     for (k=0; k<nnotes; ++k)
     {
         steps=3*sampvect-samples[k]-2;        
         maxi=0.0;
         for (n=0; n<steps; ++n)
         {  // qui considerare anche la semionda negativa considerando il quadrato di capture (magari il risultato corretto si scopre prima)
             capture=(container[n]+container[n+1]+container[n+2]+container[n+samples[k]]+container[n+samples[k]+1]+container[n+samples[k]+2])/6.0;
             if (capture > maxi)
             {
                 maxi = capture;
             }
         }
         if (maxi > detect)
         {
             detect = maxi;
             counter = k;
         }
         
         // RTFI calculation
         
         RTFI=0;
         /** The RTFI calculation is performed and the values are written in the file filefilter.out \n
          The monophonic detection instead is printed on the file monodet.out*/
         for (j = 0; j < sampvect; ++j)               
            {
            rey[j]=coefficents.c[k]*buf[j+(i*sampvect)]+coefficents.a[k]*pry[k]-coefficents.b[k]*iry[k];
            imgy[j]= coefficents.a[k]*iry[k]+coefficents.b[k]*pry[k];
            pry[k]=rey[j]; 
            iry[k]=imgy[j]; 
            energy[j]=sqrt(pow(rey[j],2)+pow(imgy[j],2));
            RTFI=RTFI+pow(energy[j],2);
                   
            } // samples in sampvect
         RTFI=RTFI/sampvect;
         RTFI=10*log10(RTFI);
         
        if (k==nnotes-1){         
            //fprintf(out,"%d ",buf[j+(i*sampvect)]);
            fprintf(myfile,"%f ",RTFI);
            fprintf(myfile,"\n");
            
             }
        else{
            fprintf(myfile,"%f ",RTFI);
            fprintf(myfile,"\t");
            }
         
     }
     fprintf(monodet,"%f ",coefficents.d[counter]);
     fprintf(monodet,"\n");
    }
    //fclose(myfile);
    fclose(monodet);
    fclose(integral);
    fclose(myfile);
    fclose(myfft);
    
    //char arg1[5]="arg1";
    execlp("/bin/sh","/bin/sh","/home/luciamarock/Documents/AudioAnalyzer/script.sh","poly",filename,NULL);
    return 0;
    }