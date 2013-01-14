'''A set of utilities to interact with gromacs'''

# Need to add a parser to insert this contrib script

# $ chemlab gromacs energy
# it should show a little interface to view the energy

# Let's launch the program and determine what happens

import pexpect
import difflib
import sys

def setup_commands(subparsers):
    parser = subparsers.add_parser("gromacs")
    
    parser.add_argument('properties', metavar='property', type=str, nargs='+',
                        help='Properties to display in the energy viewer.')
    parser.set_defaults(func=lambda args: main(args.properties))

def main(args):
    child = pexpect.spawn('g_energy')
    
    # Let's read the properties
    child.expect('Select the terms you want')
    for i in range(4):
        child.readline()

    datatab = ''
    while True:
        line = child.readline()
        datatab += line.lower()

        if line == '\r\n':
            #print 'done!'
            break
    
    data_avail = datatab.split()[1::2]
    
    # Selecting user input
    input_ = ''
    for arg in args[:]:
        match = difflib.get_close_matches(arg, data_avail)
        print 'Close Matches', match

        if match == []:
            print arg, ': No such property'
            sys.exit(0)

        prop = match[0]
        ind = data_avail.index(prop) + 1
        input_ += '%d ' % ind
    child.sendline(input_+'\n\n')

    # Now parse the average and other quantities
    child.expect('Energy           ')
    child.readline() # Skip two lines
    child.readline()
    # print child.readline().split()
    child.expect('\r\n\r\n')
    averages = child.before.split('\n')
    
    child.expect(pexpect.EOF)

    import re

    quantities = []
    for line in open('energy.xvg'):
        if line[0] not in ['#', '@']:
            break

        if 'yaxis' in line:
            m = re.search("\"(.*)\"", line)
            units = m.group(1).split(', ')
        elif re.match('@ s\d+\s+legend', line):
            m = re.search("\"(.*)\"", line)
            quantities.append(m.group(1))
            
    import numpy as np
    # Finally display this with matplotlib
    datamat = np.loadtxt('energy.xvg', comments='@', skiprows=8, unpack=True)

    
    app = App()
    app.plot(datamat[0], datamat[1])
    msg = '{}   Avg: {}     Err.Est.: {}   RMSD: {}    Drift: {}'.format(*averages[0].split())
    app.set_statusbar(msg)
    app.exec_()
    
from PySide.QtUiTools import QUiLoader
from PySide.QtCore import QFile
from PySide.QtGui import QWidget, QApplication

import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'
import pylab

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys

class App(QApplication):
    def __init__(self):
        QApplication.__init__(self, sys.argv)
        self.loader = loader = QUiLoader()
        pref = '/home/gabriele/workspace/chemlab/chemlab/contrib/'
        file = QFile(pref + "energyplot.ui")
        file.open(QFile.ReadOnly)
        self.mainwin = mainwin = loader.load(file)
        file.close()
        pltcontainer = mainwin.findChild(QWidget, "plotplaceholder")
        fig = Figure(figsize=(600,600), dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
        self.ax = ax = fig.add_subplot(111)
        # generate the canvas to display the plot
        self.canvas = canvas = FigureCanvas(fig)
        ly = pltcontainer.layout()
        ly.addWidget(canvas)
        #canvas.setParent(self.mainwin)
    
        self.mainwin.show()
        
    def plot(self, *a, **kw):
        self.ax.plot(*a, **kw)
        self.canvas.draw()

    def set_statusbar(self, msg):
        self.mainwin.statusBar().showMessage(msg)
if __name__ == '__main__':
    main(['pressure'])
