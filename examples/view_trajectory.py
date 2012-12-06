from pyglet import *

# First Idea
v = Viewer()

tr = Trajectory("whatever.gro")

sr = v.add_renderer(SphereRenderer, tr[0].atoms)
br = v.add_renderer(CubeRenderer, tr[0].boxsize)

def animate(dt):
    sr.load_animation(t.atoms for t in tr)

v.add_animation(animate)

v.show()

# Second Idea

v = Viewer()

tr = Trajectory("whatever.gro")

sr = v.add_renderer(SphereRenderer, tr[0].atoms)
br = v.add_renderer(CubeRenderer, tr[0].boxsize)

slider = v.add_ui(SliderUI, (0, len(tr)))

@slider.update
def animate(newval):
    sr.update_positions(tr[newval])

v.show()
