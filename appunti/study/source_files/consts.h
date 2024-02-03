/*
 * File:   consts.h
 * Author: Gil Hadas
 *
 * Created on July 5, 2023
 */

#ifndef CONSTS_H
#define CONSTS_H


#include <math.h>
// set buffer size
#define sampvect 256
//#define Sf 44100.0

#define PI 3.14159265358979323

#define  NNOTES 51   // normal 89, reduced 51
#define NHARMS 70   // normal 108, reduced 70
#define MIDI_START 40 // starting MIDI note number for Database files, normal 36, reduced 40
#define SCALING 2147483648.0

#define MAX_EXPECTED 10

#define TEMPO_CONST 60000000
#define SECONDS 60
#define BILLION  1000000000L;

#define REALTIME 1
#define WRITE_TO_FILE 1
#define SAVE_INPUT_TO_FILE 0

const float sens = 5.0;  // between 1 and 10
const float rtfithreshold = 4.601162791/sens;
const float firstharmth = 4.3/sens;
const float scndharmth = 3.999/sens;
const float stability_threshold = 3.5 / sens;
const int using_score = 1;
const int op_wait = 9;
const int index_to_MIDI = 39; // normal 20, reduced 39
const float noise_threshold = 3.0; // between 1 and 10
const float attack_threshold = 0.2;
const float integer_threshold = noise_threshold / 100.0;
const float tet  = pow(2.0, 1.0/(1.0*12.0));
const float f0 = 77.782;   // when normal 25.9565436, when reduced 77.782

#endif /* CONSTS_H */

