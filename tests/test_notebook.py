from chemlab.notebook.display import Display

from chemlab.core import System


def test_display():
    d = Display('povray')
    s = System.from_arrays(type_array=['O', 'H', 'H'],
                           r_array=[[0.0, 0.0, 0.0], [0.15, 0.0, 0.0], [0.0, 0.15, 0.0]])
    d.system(s)
    
    s.r_array = s.r_array + 0.3
    d.system(s, alpha=0.5)
    
    d.render()
