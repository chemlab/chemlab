"""Create rendered pictures"""
from chemlab.graphics import Scene
from chemview.render import render_povray



def test_render():
    scene = Scene()
    scene.add_representation('points', {'coordinates' : [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
                                        'colors' : [0xffffff, 0xffffff],
                                        'sizes' : [1, 1]})
    scene.camera.autozoom([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    render_povray(scene.to_dict(), filename='/tmp/hello.png')
