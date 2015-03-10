from __future__ import division, print_function
from .base import IOHandler

try:
    import tables as tb
    tables_available = True
except:
    print("HDF backend is not available because pytables is not installed")
    tables_available = False


class HdfIO(IOHandler):
    '''Reader for MDtraj HDF trajectory format.

    **Features**

    .. method:: read("trajectory")

       Read the frames from the file and returns the trajectory as an
       array of times and an array of atomic positions::

           >>> times, positions = datafile('traj.h5').read('trajectory')
           [t1, t2, t3], [pos1, pos2, ...]

    .. method:: read("boxes")

       After reading the "trajectory" feature you can call
       `read("boxes")` that will return a list of 3D array representing box
       dimensions corresponding to each frame.

    '''
    can_read = ['trajectory', 'boxes']
    can_write = []

    def read(self, feature, **kwargs):
        if not tables_available:
            raise Exception("HDF backend is not available because pytables is not installed")

        trjfile = tb.open_file(self.fd.name)

        if feature == 'trajectory':
            skipframes = kwargs.get("skip", None)
            if skipframes is not None:
                print("Skip argument not available for hdf5 backend.")

            return trjfile.root.time, trjfile.root.coordinates

        if feature == 'boxes':
            return trjfile.root.cell_lengths
