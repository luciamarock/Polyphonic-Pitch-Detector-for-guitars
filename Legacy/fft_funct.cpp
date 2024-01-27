/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "fft_funct.h" // definition of fft_funct
#include "parabola.h"
#define PI 3.14159265358979323
#define Ns 2048   // maximum number of samples

// coefficients
double Wre[Ns/2];
double Wim[Ns/2];
// CalcolaW() declaration
void CalcolaW(int n);

void fft_funct(float * buffer, int size, float tet, float f0, int nharms, int Fs)
{    
    int posizioni[Ns] = {0};
    int i,j;
    int numerobit;
    int appoggio=0;
    int NC;
    float scarto;
    // variables for calculus of steps
    int k=0;
    int v=0;
    int a,b;    
    int incremento;
    int nBlocchi,elBlocco;
    // temporary vectors for storing values between steps
    double Xreapp[Ns] = {0};
    double Ximapp[Ns] = {0};
    // sequences 
    double Xre[Ns] = {0};
    double Xim[Ns] = {0};
    float fc[nharms] = {0};
    float index[size/2]={0}; // Ns/4
    float gaps=Fs/(float)size;
    /** In the fft_funct the first thing to do is to calculate the closest power of two to the size of the input vector. 
     * Then the new buffer size is called NC (in case the input vector's dimension is already a power of two, then NC is equal to 
     * the input vector's length) \n*/
    scarto = log2(size)-((int)log2(size)); 
    if (scarto >= 0.5)
        NC = pow(2,(((int)log2(size))+1));
    else
        NC = pow(2,((int)log2(size)));
    
    // RTFI + harmonics frequencies calculation
    /** Then another vector is calculated, 
     * it will be used for the parabolic interpolation and it is called fc[] */
    for (int i=0; i<nharms; i++){
        fc[i]=f0*pow(tet,i);
    }
    
    // bit inversion
    /** The Goertzel algorithm is used to calculate the FFT, this algorithm uses decimation in time dividing the 
     * input sequence in blocks until each block contains only to samples to be combined, please read the document 
     * Tesina di informatica II.pdf for having a clearer understanding of the procedure  */
    numerobit=log2(NC);       
    for (i=0; i<NC; i++)
    {
     appoggio =i;
     posizioni[i] = (appoggio&0x0001)|(posizioni[i]);
     for (j=0; j<(numerobit-1); j++)
        { 
            appoggio = appoggio >> 1;
            posizioni[i] = ((posizioni[i])<<1);
            posizioni[i] = (appoggio&0x0001)|(posizioni[i]);
        }
    }    
    
    // sequences initialization     
    /** Xre is the rewritten input vector with inverted bit position (see the Goertzel algorithm), 
     Xim is not calculated because in fact we don't use the imaginary part */
    i=0;
    if (size>=NC)
    {
       while(i<NC)
        {
            Xre[posizioni[i]] = buffer[i];
            i=i+1;
        }
    }
    else
    {
       while(i<size)
        {
            Xre[posizioni[i]] = buffer[i];
            i=i+1;
        }  
        while(i<NC)
        {     
            Xre[posizioni[i]] =  0.0;
            i=i+1;
        }
    }  
    
    // coefficients calculation
    /** The coefficient calculation Wre and Wim could have been done at the beginning */
    CalcolaW(NC);
  
    for(i=0;i<NC;i++)
    {
        Xreapp[i] = Xre[i]; 
        //Ximapp[i] = Xim[i];         
    }
 // This block is the core of the Goertzel algorithm 
 for(i=0;i<numerobit;i++)
 {    
    nBlocchi = NC /pow(2,i+1);
    incremento = NC /pow(2,i+1);
    elBlocco= NC/nBlocchi;
  
      for (a=0; a<nBlocchi; a++)
      {  
          
          for(b=0; b<(elBlocco/2); b++)
          {
           Xre[k]=Xreapp[k]+ (Wre[v]*Xreapp[k+(int)(pow(2,i))] - Wim[v]*Ximapp[k+(int)(pow(2,i))]);
           Xim[k]=Ximapp[k]+ (Wim[v]*Xreapp[k+(int)(pow(2,i))] + Wre[v]*Ximapp[k+(int)(pow(2,i))]);  
           
           Xre[k+(int)(pow(2,i))]=Xreapp[k]- (Wre[v]*Xreapp[k+(int)(pow(2,i))] - Wim[v]*Ximapp[k+(int)(pow(2,i))]); 
           Xim[k+(int)(pow(2,i))]=Ximapp[k]- (Wim[v]*Xreapp[k+(int)(pow(2,i))] + Wre[v]*Ximapp[k+(int)(pow(2,i))]); 
            
           v = v + incremento;
           if (i != 0)
             k = k+1;  
          }
          k = a*(elBlocco);
          k = k + (elBlocco);
          v=0;
      }
      // k always reaches the value of size
      k=0;
      // writing of next temporary vectors 
      for(j=0;j<NC;j++)
      {
        Xreapp[j] = Xre[j]; 
        Ximapp[j] = Xim[j];         
      }  
                
 } 
    
 // amplitude calculation 
    /** The input buffer is overwritten with the amplitude of the fft points */
 for(i=0;i<NC/2;i++)
 {            
    buffer[i] = pow(((Xre[i]*Xre[i])+(Xim[i]*Xim[i])),0.5)/NC*2.0;
 } 
    
 // RTFI + harmonics components amplitude calculation 
 /** Here the closest peak calculation is performed in order to find the peaks on which the parabolic interpolation should 
  be calculated \n
  For each note (fc[]) we search the Fourier frequency (index[]) closest to the fundamental frequency of that note */
   for (i = 0; i < size/2; i++){
       index[i]=i*gaps;
   }
  float sx;
  float dx;
  int match = 0;
  float A;
  float B;
  float C;
  float amplitude[nharms] = {0};
  
  for (i=0; i<nharms; i++)
  {
      match = 0;
      j = 0;
      
      while (match == 0 && j < size/2)
      {
          if (fc[i]>index[j] && fc[i]<index[j+1])
          {
              
              sx=fc[i]-index[j];
              dx=index[j+1]-fc[i];
              if (sx > dx)
              {
                  match = j+1;
              }
              else
              {
                  match = j;
              }              
          }
          j = j + 1;
      }
      // parabola coefficients calculation
      /** Then we pass to the parabola calculation the 3 points around that RTFI frequency and we calculate the parabola coefficients A, B and C \n
        and use those coefficients to calculate the estimated amplitude of the RTFI frequency */
      parabola(A, B, C, index[match-1], buffer[match-1], index[match], buffer[match], index[match+1], buffer[match+1]);
      amplitude[i] = A*pow(fc[i],2)+B*fc[i]+C;
  } 
  
   //float step=44100/NC;
  /** Finally we overwrite the Fourier output with the values corrected from the parabolic interpolation. \n
   Indeed we don't take full advantage of the parabolic interpolation which could be used to estimate the correct position in frequency of the point. 
   This is a choice we made because we supposed that we don't need to estimate the correct position in frequency of the peak because we already know it, 
   that's why we use the RTFI technique; but in case of the guitar this parabolic interpolation could be also used for estimating the correct frequency 
   during "bendings" even tough we could be precise only on high pitched notes. \n 
   Another thing that should be evaluated is the possibility to analyze a larger buffer, this should be done considering the CPU power we have at our 
   disposal, from this Goertzel implementation documentation we have the complexity of the algorithm which is roughly NlogN*/
   for(i=0; i<(NC/2); i++)
   {
    if (i<nharms){
        buffer[i]=amplitude[i];
       }
   }
}


// CalcolaW() definition
void CalcolaW(int n)
{
     int i;
     for (i=0;i<(n/2);i++)
     {
         Wre[i]=cos(2*PI*i/n);
         Wim[i]=-sin(2*PI*i/n);
   
     }
     
}