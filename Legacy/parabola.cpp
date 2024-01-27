/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "parabola.h"
/** Given three points, it calculates the coefficients of the parabola passing through those points */
void parabola(float &A, float &B, float &C, float x0, float y0, float x1, float y1, float x2, float y2){

    A = (x2*(y1-y0)+x1*(y0-y2)+x0*(y2-y1))/((x0-x1)*(x0-x2)*(x1-x2));
    B = (pow(x0,2)*(y1-y2)+pow(x2,2)*(y0-y1)+pow(x1,2)*(y2-y0))/((x0-x1)*(x0-x2)*(x1-x2));
    C = (pow(x1,2)*(x2*y0-x0*y2)+x1*(pow(x0,2)*y2-pow(x2,2)*y0)+x0*x2*(x2-x0)*y1)/((x0-x1)*(x0-x2)*(x1-x2));

}