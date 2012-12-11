# Plotting utility

import matplotlib
matplotlib.use('TkAgg')
import numpy as np

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk

def destroy(e): sys.exit()

root = Tk.Tk()
root.wm_title("Embedding in TK")
#root.bind("<Destroy>", destroy)


f = Figure(figsize=(5,4), dpi=100)
a = f.add_subplot(111)
t = np.arange(0.0,3.0,0.01)
s = np.sin(2*np.pi*t)

a.plot(t,s)
a.set_title('Tk embedding')
a.set_xlabel('X axis label')
a.set_ylabel('Y label')

def display_potential():
    filename = sys.argv[1]
    import os
    directory, basename = os.path.split(filename)
    os.chdir(directory)
    
    os.system('g_energy')
    
    with open(basename) as fd:
        lines = fd.readlines()

    lines = [ l for l in lines if not l.startswith('#')]
    import re
    regex = re.compile('@ s(\d+) legend "(.*)"')
    
    labels = []
    nums = []
    for l in lines:
        match = regex.match(l)
        if match:
            num, label = match.groups()
            nums.append(int(num))
            labels.append(label)
    
    # All the data numbers
    lines = [ l for l in lines if not l.startswith('@')]            
    datamat = []
    
    for l in lines:
        datamat.append([float(n) for n in l.split()])
    
    datamat = np.array(datamat)
    x = datamat[:, 0]
    
    def plot(n, l):
        a.clear()
        a.set_title(l)
        a.plot(x, datamat[:, n+1])
        f.canvas.draw()

    # Let's make the various buttons
    for i, lab in enumerate(labels):
        button = Tk.Button(master=root, text=lab,
                           command=lambda n=i, l=lab: plot(n, l))
        button.pack(side=Tk.RIGHT)
        
# a tk.DrawingArea
canvas = FigureCanvasTkAgg(f, master=root)
canvas.show()
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

toolbar = NavigationToolbar2TkAgg( canvas, root )
toolbar.update()
canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

button = Tk.Button(master=root, text='Quit', command=sys.exit)
button.pack(side=Tk.RIGHT)

display_potential()
Tk.mainloop()