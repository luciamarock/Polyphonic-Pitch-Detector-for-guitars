#!/bin/bash

# HOW TO USE 
# $1 = guitar [Prs, Ibanez, poly or piano]
# $2 = note name [Gmin, etc ...]

#mv /home/luciamarock/Documents/AudioAnalyzer/audioFiles/piano/stereo/monophonic/$2.wav /home/luciamarock/Documents/AudioAnalyzer/audioFiles/piano/stereo/monophonic/converted

mv filefft.out ./scores/$1/$2_filefft.out
mv filefilter.out ./scores/$1/$2_filefilter.out
mv monodet.out ./scores/$1/$2_monodet.out
mv integer.out ./scores/$1/$2_integer.out

#mv sine.txt algo_outputs/
#mv mapping.txt algo_outputs/
#mv coeffs.txt algo_outputs/
#mv notes.txt algo_outputs/

