#!/bin/bash

cython -a $1
fname="${1%.*}"

gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -lm -fno-strict-aliasing \
      -I/usr/include/python2.7 -o $fname.so $fname.c


