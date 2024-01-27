/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
#include <cstdlib>
#include <stdio.h>
#include <iostream>
#include <math.h>
#include <vector>
#include <fstream>
#include <iomanip>
#include "resonators.h"
#include <fftw3.h>
//#define N 512

using namespace std;


    
struct Tuple init(int Fs, float f0, int nnotes, float tet){

    struct Tuple tuple;
    // vectors
    
    float *reas=tuple.a;
    float *imas=tuple.b;
    float *bees=tuple.c;
    float *notes=tuple.d;
    // end vectors
    float d=pow(2,(1/24.));
    float c=4*(d-1)/(d+1);
    float omega;
    float romega;
    float r;
    float phi;
    float rea;
    float ima;
    float b;
    //FILE *notes_piano;
    //notes_piano = fopen("notes_piano.out","w");
      
    /** This init function is called directly from the main() program
     * at the beginning it loops until nharms (which in this case is 70) in order to calculate the 
     * center frequencies for the RTFI resonators, the f0 is also hard coded and it's set to 77.782 Hz
     * for the Guitar. The notes vector is returned as coefficent d 
     * All of these parameters should be read from a configuration file 
     * instead of being hard-coded */
        for (int i=0; i<nnotes; i++){
            float fc=f0*pow(tet,i);  
            notes[i]=fc;
            //fprintf(notes_piano,"%f ",fc);
            //fprintf(notes_piano,"\n");
        }
    //fclose(notes_piano);

  /** Finally the coefficients for the RTFI resonators are calculated, no mistery in this block 
   * just a bit of math.  */
        for (int i=0; i<nnotes; i++){            
            omega = 2*M_PI*notes[i];
            romega = c * notes[i];
            r = exp(-romega/Fs);
            phi = omega/Fs;
            rea = r*cos(phi);
            reas[i]=rea;
            ima = r*sin(phi);
            imas[i]=ima;
            b = (1-pow(r,2))/(r*sqrt(2));
            bees[i]=b;
        }
    return tuple;
}