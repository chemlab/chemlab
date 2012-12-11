from chemlab.graphics import Viewer
from chemlab.graphics.renderers import SphereRenderer, CubeRenderer
from chemlab.io.gro import read_gro_traj
import sys

filename = sys.argv[1]

v = Viewer()

tr = read_gro_traj(filename)

sr = v.add_renderer(SphereRenderer, tr[0].atoms)
br = v.add_renderer(CubeRenderer, tr[0].boxsize)

i = 0
def animate():
    try:
        sys = tr[i]
    except IndexError:
        return
    global i 
    i += 1
    
    if i == 2:
        return
    sr.update(sys.rarray)


v.schedule(animate)
v.run()