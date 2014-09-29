cdef extern from "math.h":
    double sqrt(double) nogil
    double rint(double) nogil

cdef double minimum_image_distance(double[:] a,double[:] b, double[:] periodic) nogil
