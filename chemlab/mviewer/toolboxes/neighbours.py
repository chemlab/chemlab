from scipy.spatial import cKDTree

def neighbours(dist):
    sel = current_selection().atom_selection
    kd = cKDTree(s.r_array)
    
    return kd.query_ball_point(s.r_array[sel.atom_selection], dist)
    
def select_neighbours(dist):
    tohigh = neighbours(dist)
    sel.highlight()
    
    
