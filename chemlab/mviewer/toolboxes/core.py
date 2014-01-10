'''
Basic functions to interact with what's currently displayed.
'''

def hide():
    return viewer.representation.hide()
    
def current_system():
    '''The :py:class:`chemlab.core.System` that is currently
    displayed.

    '''
    return viewer.system
    
def current_traj_frame():
    return viewer.traj_controls.current_index

def current_traj_time():
    return viewer.frame_times[current_traj_frame()]
    
def current_selection():
    return viewer.representation.selection_state
    
def current_representation():
    return viewer.representation
