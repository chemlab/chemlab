'''Trajectory analysis utils

'''
from chemlab.core.spacegroup.crystal import crystal
from chemlab.molsim.analysis import radial_distribution_function
from chemlab.data import moldb
from chemlab.io.gro import write_gro

from pylab import *


def test_rdf():
    # Take a system, say a LiCl salt and calculate g+- 
    system = crystal([[0.00000, 0.00000, 0.00000], [0.50000, 0.5000, 0.5000]],
              [moldb.li, moldb.cl], group=225,
              cellpar=[0.513, 0.513, 0.513, 90, 90, 90],
                     repetitions=[6,6,6])

    rdf = radial_distribution_function(system,
                                       system.type_array == 'Li',
                                       system.type_array == 'Cl', 4618, 9.232)
    

    
    #gro_rdf = np.loadtxt("rdf.xvg", skiprows=13,unpack=True)
    #print rdf[0][:10]
    #print gro_rdf[0][:10]
    #print np.allclose(rdf[0], gro_rdf[0])
    
    plot(rdf[0], rdf[1], 'blue')
    #plot(gro_rdf[0], gro_rdf[1], color='red')
    #write_gro(system, 'cry.gro')
    show()