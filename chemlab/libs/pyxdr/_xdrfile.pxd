cdef extern from "xdrfile.h":

    ctypedef struct XDRFILE:
        pass
    
    ctypedef enum xdrstat_t:
        exdrOK
        exdrHEADER
        exdrSTRING
        exdrDOUBLE
        exdrINT
        exdrFLOAT
        exdrUINT
        exdr3DX
        exdrCLOSE
        exdrMAGIC
        exdrNOMEM
        exdrENDOFFILE
        exdrFILENOTFOUND
        exdrNR
        
    #ctypedef float matrix[3][3]
    #ctypedef float rvec[3]
    ctypedef float *matrix
    ctypedef float *rvec
    
    XDRFILE* xdrfile_open(char* path, char* mode)
    int xdrfile_close(XDRFILE* xfp)
    
    char* exdr_message[14]
    
cdef extern from "xdrfile_xtc.h":
    int read_xtc_natoms(char* fn, int* natoms)
    int read_xtc(XDRFILE *xd, int natoms, int *step, float* time, matrix box, rvec *x, float *prec) nogil 
    int write_xtc(XDRFILE *xd, int natoms, int step, float  time, matrix box, rvec *x, float prec)
