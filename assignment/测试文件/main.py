#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This program reads in an input argument (which is expected to be
a positive integer) and write some text to a file with name
dummy_*.txt where * is the input argument 


"""

import sys 
import os
# import numpy as np 

def main(s):
          
    # As a demonstration, write to a file called dummy_*.txt
    # in the output directory 
    out_folder = 'output'
    dummy_file = os.path.join(out_folder,'dummy_'+s+'.txt')
    
    with open(dummy_file,'w') as file:
        file.writelines(f'The input argument is {s}\n') 
  
if __name__ == "__main__":
   main(sys.argv[1])
