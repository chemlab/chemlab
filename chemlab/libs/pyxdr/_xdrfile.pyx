from __future__ import division
cimport _xdrfile
import numpy
cimport numpy
cimport cython

from collections import namedtuple
_xtcframe = namedtuple('_xtcframe', ('step', 'time', 'prec', 'box', 'coords'))

class XDRError(RuntimeError):
    def __init__(self, msg, libxdr_errno):
        self.args = [msg, libxdr_errno, _xdrfile.exdr_message[libxdr_errno]]
        
    def __str__(self):
        return '{} (libxdrfile error {:d}: {})'.format(*self.args[0:3])

cdef class XTCReader:
    cdef _xdrfile.XDRFILE *_xd
    cdef readonly char* name
    cdef readonly int natoms

    def __cinit__(self, path):
        self._xd = NULL
        self.natoms = 0
        self.name = ''

    def __dealloc__(self):
        self.close()
    
    def __init__(self,path):
        cdef int rc
        path = path.encode('utf-8') # Python 3
        
        rc = _xdrfile.read_xtc_natoms(path, &self.natoms)
        if rc != 0:
            raise XDRError('could not open %r' % path, rc)
        self._xd = _xdrfile.xdrfile_open(path, 'r')
        if self._xd is NULL:
            raise XDRError('could not open %r (after successfully reading natoms)'%path)
                
    def close(self):
        cdef int rc
        if self._xd is not NULL:
            try:
                rc = _xdrfile.xdrfile_close(self._xd)
                if rc != 0:
                    raise XDRError('could not close XTC file', rc)
            finally:
                self._xd = NULL
                self.natoms = 0

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def readframe(self):
        cdef float time, prec
        cdef numpy.ndarray[float, ndim=2] box = numpy.empty((3,3), numpy.float32)
        cdef numpy.ndarray[float, ndim=2] x = numpy.empty((self.natoms,3), numpy.float32)
        cdef int rc, step, 
        cdef int natoms = self.natoms
        cdef _xdrfile.XDRFILE *xd = self._xd
    
        with nogil:                
            rc = _xdrfile.read_xtc(xd, natoms, &step, &time, <float*> box.data, <rvec*> x.data, &prec)
        if rc != 0:
            if rc == _xdrfile.exdrENDOFFILE:
                return None
            else:
                raise XDRError('could not read XTC frame', rc)
        
        return _xtcframe(step, time, prec, box, x)
            
    def __iter__(self):
        frame = self.readframe()
        while frame is not None:
            yield frame
            frame = self.readframe()
