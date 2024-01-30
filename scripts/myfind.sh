#!/bin/bash

grep $1 *.cpp
grep $1 *.h
grep $1 *.py
grep $1 algo_outputs/*

#grep $1 latex/*

