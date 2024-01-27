/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   resonators.h
 * Author: luciamarock
 *
 * Created on May 20, 2019, 11:14 PM
 */

#ifndef RESONATORS_H
#define RESONATORS_H
struct Tuple{
        float a[100];
        float b[100];
        float c[100];
        float d[100];
    };
struct Tuple init(int Fs, float f0, int nnotes, float tet);

#endif /* RESONATORS_H */

