#!/bin/bash

zip -ry GAP_src.zip *.h *.cpp *.py Makefile script.sh algo_outputs/ ./appunti
mv GAP_src.zip /home/luciamarock/GAP/Bcks

zip -ry scores.zip scores/ 
mv scores.zip /home/luciamarock/GAP/Bcks

cd ..
zip -ry AudioAnalyzer.zip AudioAnalyzer/ -x '*scores*' -x '*audioFiles*'
mv AudioAnalyzer.zip /home/luciamarock/GAP/Bcks


#cd /home/luciamarock/Dropbox/cppEsercizi
#zip -ry AudioAnalyzer_drop.zip AudioAnalyzer/
#mv AudioAnalyzer_drop.zip /home/luciamarock/GAP/Bcks
#rm -rf AudioAnalyzer/

#unzip AudioAnalyzer.zip
#rm -f AudioAnalyzer.zip

