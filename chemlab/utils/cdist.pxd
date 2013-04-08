cdef extern from "math.h":
    double sqrt(double)
    double rint(double)

cdef inline double minimum_image_distance(double[:] a,double[:] b, double[:] periodic)
