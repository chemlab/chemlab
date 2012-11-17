
cforces.so:
	cython -a chemlab/molsim/cforces.pyx
	gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -lm -fopenmp -fno-strict-aliasing \
            -I/usr/include/python2.7 -o chemlab/molsim/cforces.so chemlab/molsim/cforces.c

cenergy.so:
	cython -a chemlab/molsim/cenergy.pyx
	gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -lm -fopenmp -fno-strict-aliasing \
            -I/usr/include/python2.7 -o chemlab/molsim/cenergy.so chemlab/molsim/cenergy.c

cforces2.so:
	cython -a chemlab/molsim/cforces2.pyx
	gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -lm -fopenmp -fno-strict-aliasing \
            -I/usr/include/python2.7 -o chemlab/molsim/cforces2.so chemlab/molsim/cforces2.c chemlab/molsim/cmpforces.c

