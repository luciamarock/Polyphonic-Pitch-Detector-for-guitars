/* 
 * File:   pdct_main.cpp
 * Author: luciamarock
 *
 * Created on 5 novembre 2016, 14.00
 */

#include <cstdlib>
#include <cstdio>
#include <cstdarg>
#include "cPdctOptions.h"
#include "cPdctMain.h"

/*
 * 
 */
int main(int argc, char** argv)
{
    fprintf(stdout, "Start Of Program \n");
    
    /* get command line options, and run rpogram */
    cPdctOptions aMainOptions;
    if(aMainOptions.parseCommandLine(argc, argv)){
        cPdctMain aMainProagram;
        aMainProagram.run(aMainOptions);
    }
    
    fprintf(stdout, "End Of Program \n");
   
    return 0;
}

