/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

#include <iostream>
#include "streamer.h"

int chunker(int buffdim, int elemcount){
 /** This function basically divides the total length (in number of samples) of the audio file in input 
  by the length of the chosen samples buffer, in this case 256, this way we obtain the number of buffers 
  contained in the audio file. \n 
  There is of course a bunch of remaining samples this can be ignored, in fact they are not returned, the calculation 
  was made just for educational purposes because it is done calling another function */
 int buffcount;
 
 buffcount = (int)elemcount/buffdim; 
 return buffcount;
}