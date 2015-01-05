'''A set of utilities to interact with gromacs'''

# Need to add a parser to insert this contrib script

# $ chemlab gromacs energy
# it should show a little interface to view the energy

# Let's launch the program and determine what happens
from chemlab.io import datafile
from pylab import *
from chemlab.molsim.analysis import rdf

import difflib
import sys, re
import numpy as np

def setup_commands(subparsers):
    groparser = subparsers.add_parser("gromacs")
    
    subparsers2 = groparser.add_subparsers()
    eparser = subparsers2.add_parser("energy")
    
    eparser.add_argument('filenames', metavar='filenames', type=str, nargs='+')
    eparser.add_argument('-e', metavar='energies', type=str, nargs='+',
                        help='Properties to display in the energy viewer.')
    

    eparser.add_argument('-o', help='Do not display GUI and save the plot')
    
    eparser.set_defaults(func=lambda args: energy(args, args.o))

    rdfparser = subparsers2.add_parser("rdf")
    rdfparser.add_argument('selection', metavar='selection', type=str)
    rdfparser.add_argument('filename', metavar='filename', type=str)
    rdfparser.add_argument('trajectory', metavar='trajectory', type=str)
    rdfparser.add_argument('-t', metavar='t', type=str) 
    rdfparser.set_defaults(func=rdffunc)
    
def energy(args, output=None):
    ens = args.e
    fns = args.filenames
    
    datafiles = [datafile(fn) for fn in fns] 
    
    quants = datafiles[0].read('avail quantities')
    for i,e in enumerate(ens):
        if e not in quants:
            match = difflib.get_close_matches(e, quants)
            print('Quantity %s not present, taking close match: %s'
                  % (e, match[0]))
            ens[i] = match[0]
    
    toplot = []
    for df in datafiles:
        for e in ens:
            plotargs = {}
            plotargs['points'] = df.read('quantity', e)
            plotargs['filename'] = df.fd.name
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

def get_rdf(arguments):
    return rdf(arguments[0], arguments[1], periodic=arguments[2])

def rdffunc(args):

    import multiprocessing
    type_a, type_b = args.selection.split('-')
    syst = datafile(args.filename).read("system")
    sel_a = syst.type_array == type_a
    sel_b = syst.type_array == type_b
    
    df = datafile(args.trajectory)
    t, coords = df.read("trajectory")
    boxes = df.read("boxes")
    
    times = [int(tim) for tim in args.t.split(',')]
    ind = np.searchsorted(t, times)
    arguments = ((coords[i][sel_a], coords[i][sel_b], boxes[i]) for i in ind) 
    
    rds = map(get_rdf, arguments)
    
    for rd in rds:
        plot(rd[0], rd[1])
    
    ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    
    xlabel('Time(ps)')
    ylabel(args.selection)

    grid()
    show()
    

if __name__ == '__main__':
    main(['pressure'])
