'''A set of utilities to interact with gromacs'''

# Need to add a parser to insert this contrib script

# $ chemlab gromacs energy
# it should show a little interface to view the energy

# Let's launch the program and determine what happens
from chemlab.io import datafile
from pylab import *

import difflib
import sys, re
import numpy as np

def setup_commands(subparsers):
    parser = subparsers.add_parser("gromacs")
    
    parser.add_argument('filenames', metavar='filenames', type=str, nargs='+')
    parser.add_argument('-e', metavar='energies', type=str, nargs='+',
                        help='Properties to display in the energy viewer.')
    

    parser.add_argument('-o', help='Do not display GUI and save the plot')
    
    parser.set_defaults(func=lambda args: main(args, args.o))
    

def read_xvg(filename):
    return parse_xvg(open(filename).read())
    
def parse_xvg(text):
    
    def parse_statement(line):
        return 
    
    quantities = []
    curline = 0
    
    lines = text.splitlines()
    for line in lines:
        curline += 1
        if line[0] not in ['#', '@']:
            break

        if 'yaxis' in line:
            m = re.search("\"(.*)\"", line)
            units = m.group(1).split(', ')
        elif re.match('@ s\d+\s+legend', line):
            m = re.search("\"(.*)\"", line)
            quantities.append(m.group(1))
    
    from StringIO import StringIO
    datatxt = '\n'.join(lines[curline:])
    fn = StringIO(datatxt)
    
    fields = np.loadtxt(fn, unpack=True)
    
    return fields
    
    
def main(args, output=None):
    ens = args.e
    fns = args.filenames
    
    datafiles = [datafile(fn) for fn in fns] 
    
    quants = datafiles[0].read('avail quantities')
    for i,e in enumerate(ens):
        if e not in quants:
            match = difflib.get_close_matches(e, quants)
            print 'Quantity %s not present, taking close match: %s' % (e, match[0])
            ens[i] = match[0]
    
    toplot = []
    for df in datafiles:
        for e in ens:
            plotargs = {}
            plotargs['points'] = df.read('quantity', e)
            plotargs['filename'] = df.filename
            plotargs['quantity'] = e
            
            toplot.append(plotargs)
    plots = []
    legends = []
    for arg in toplot:
        p, = plot(arg['points'][0], arg['points'][1])
        plots.append(p)
        legends.append(arg['filename'])
    xlabel('Time(ps)')
    ylabel(ens[0])
    
    ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    grid()
    figlegend(plots, legends, 'upper right')
    show()
    
# from PySide.QtUiTools import QUiLoader
# from PySide.QtCore import QFile
# from PySide.QtGui import QWidget, QApplication

# import matplotlib
# matplotlib.use('Qt4Agg')
# matplotlib.rcParams['backend.qt4'] = 'PySide'
# import pylab

# from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
# from matplotlib.figure import Figure
# import sys

# class App(QApplication):
#     def __init__(self):
#         QApplication.__init__(self, sys.argv)
#         self.loader = loader = QUiLoader()
#         pref = '/home/gabriele/workspace/chemlab/chemlab/contrib/'
#         file = QFile(pref + "energyplot.ui")
#         file.open(QFile.ReadOnly)
#         self.mainwin = mainwin = loader.load(file)
#         file.close()
#         pltcontainer = mainwin.findChild(QWidget, "plotplaceholder")
#         fig = Figure(figsize=(600,600), dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
#         self.ax = ax = fig.add_subplot(111)
#         # generate the canvas to display the plot
#         self.canvas = canvas = FigureCanvas(fig)
#         ly = pltcontainer.layout()
#         ly.addWidget(canvas)
#         #canvas.setParent(self.mainwin)
#         tb = NavigationToolbar(canvas, self.mainwin)
        
#         ly.addWidget(tb)
#         self.mainwin.show()
        
#     def plot(self, *a, **kw):
#         self.ax.plot(*a, **kw)
#         self.canvas.draw()

#     def set_statusbar(self, msg):
#         self.mainwin.statusBar().showMessage(msg)


if __name__ == '__main__':
    main(['pressure'])
