'''Basic functions to retrieve information on what's currently
displayed in the molecular viewer.

'''

def current_system():
    '''The :py:class:`chemlab.core.System` that is currently
    being displayed.

    '''
    return viewer.system


def current_frame():
    '''Return the integer corresponding to the current frame in the
    trajectory.

    '''
    return viewer.traj_controls.current_index


def trajectory(start=None, stop=None, step=None):
    '''Useful command to iterate on the trajectory frames by time (in
    ns). It is meant to be used in a for loop::

        for i in trajectory(0, 10, 0.1):
            coords = current_frame()
            t = current_time()
            # Do something

    The previous snippet will stop at every frame from 0 to 10 ns with
    a step of 0.1 ns.

    '''
    import numpy as np
    from PyQt4 import QtGui

    times = np.array(current_frame_times()) / 1000

    if start is None:
        start = 0

    if stop is None:
        stop = times[-1]

    start = times.searchsorted(start)
    stop = times.searchsorted(stop)

    nsteps = (times[stop] - times[start])/(step)
    step = int((stop - start)/nsteps) or 1

    sl = slice(start, stop, step)
    for i in range(*sl.indices(current_nframes())):
        viewer.traj_controls.goto_frame(i)
        yield i
        QtGui.qApp.processEvents()


def frames(skip=1):
    '''Useful command to iterate on the trajectory frames. It can be
    used in a for loop.

    ::
    
        for i in frames():
            coords = current_trajectory()[i]
            # Do operation on coords

    You can use the option *skip* to take every i :sup:`th` frame.
    
    '''
    from PyQt4 import QtGui
    
    for i in range(0, viewer.traj_controls.max_index, skip):
        viewer.traj_controls.goto_frame(i)
        yield i
        QtGui.qApp.processEvents()


def current_time():
    '''Return the floating point number corresponding to the current
    time in the trajectory (in ns).

    '''
    return viewer.frame_times[current_frame()]


def current_representation():
    '''Return the current Representation instance. Representations are
    a way to interact with the displayed chemical data.

    '''
    return viewer.representation


def current_trajectory():
    '''Return the current trajectory. A trajectory is a set of
    frames.

    '''
    return viewer.current_traj


def current_frame_times():
    '''Return the list of times associated with the current
    trajectory.

    '''
    return viewer.frame_times


def current_nframes():
    '''Return the number of frames in the current trajectory.'''
    return len(current_trajectory())


class _Msg(object):
    def __init__(self):
        self.stack = []
        
    def __call__(self, msg):
        '''Update the message in the status bar'''
        viewer.status_bar.setText('<b>' + msg + '</b>')        
        self.stack.append(msg)
        
    def pop(self):
        self.stack.pop()
        viewer.status_bar.setText('<b>' + self.stack[-1] + '</b>')        

#: Update the message in the status bar
msg = _Msg()
