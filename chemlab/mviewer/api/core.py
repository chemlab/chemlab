'''
Basic functions to interact with what's currently displayed.
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

def frames(skip=1):
    from PySide import QtGui
    
    for i in range(0, viewer.traj_controls.max_index, skip):
        viewer.traj_controls.goto_frame(i)
        yield i
        QtGui.qApp.processEvents()
    
def current_time():
    '''Return the float corresponding to the current time in the
    trajectory (in ns).

    '''
    return viewer.frame_times[current_frame()]
    
def current_representation():
    '''Return the current Representation instance. Representations are
    a way to interact with the displayed chemical data.

    '''
    return viewer.representation
