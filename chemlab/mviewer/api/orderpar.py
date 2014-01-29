from chemlab.utils import distances_within
from chemlab.utils import minimum_image, periodic_distance
from chemlab.molsim.analysis import rdf

from pylab import *
from core import *
from selections import *
from display import *
from appeareance import *

import numpy as np
from PyQt4 import QtGui
import scipy.ndimage

def order_par():
    # Hidden
    visible = visible_atoms()
    
    r_array = current_system().r_array[visible]
    box = current_system().box_vectors
    
    local_dens = []    
    
    # I can try this
    D = periodic_distance(r_array[np.newaxis, :, :],
                         r_array[:, np.newaxis, :],
                         box.diagonal())
    test = (D < 0.60).astype(int)
     
    local_dens = test.sum(axis=-1) - 1
    
    #for r in r_array:
    #    local_dens.append(len(distances_within([r], r_array, 
    #                    0.60, periodic=box.diagonal())))

    local_dens = np.array(local_dens)
    
    return local_dens

def select_crystal():
    ld = order_par()
    select_atoms(visible_atoms()[ld > 11.0])

def center_on_crystal():
    select_crystal()
    center = cluster_center()
    current_system().r_array -= center
    current_system().r_array += 0.5 * current_system().box_vectors.diagonal()
    current_system().r_array[:] = minimum_image(current_system().r_array, current_system().box_vectors.diagonal())
    current_representation().update_positions(current_system().r_array)
    
def radial_density(ion='Cl'):
    s = current_system()    
    
    select_crystal()
    center = cluster_center()

    mask = s.type_array == ion | s.type_array == 'Na'
    r_array = s.r_array.copy()
    
    ions_r = r_array[mask]
    ions_r -= center
    ions_r = minimum_image(ions_r, s.box_vectors.diagonal())
    
    # Density
    mx = s.box_vectors.max()
    
    # distance from center
    distances = np.sqrt((ions_r ** 2).sum(axis=1))
    
    bins = np.linspace(0, mx, 100)
    hist, bins_= np.histogram(distances, bins)

    # Normalize the histogram
    start_shells_r = bins_[:-1]
    end_shells_r = bins_[1:]
    
    start_shells_V = 4.0/3.0 * np.pi * start_shells_r**3
    end_shells_V = 4.0/3.0 * np.pi * end_shells_r**3
    
    V_shell = end_shells_V - start_shells_V
    
    return bins_[:-1], hist/V_shell
    
def find_neutral():
    s = current_system()
    s.charge_array[s.type_array == 'Na'] = 1.0
    s.charge_array[s.type_array == 'Cl'] = -1.0
    
    for i in frame_iter(1):
        select_crystal()
        if s.charge_array[selected_atoms()].sum() == 0:
            break

        
def cluster_center():
    # Center of mass calculation from wikipedia
    atoms = selected_atoms()
    r_array = current_system().r_array[atoms]
    max_vals = current_system().box_vectors.diagonal()
    theta = 2*np.pi*(r_array / max_vals)
    eps = np.cos(theta) * max_vals/(2*np.pi)
    zeta = np.sin(theta) * max_vals/(2*np.pi)
    
    eps_avg = eps.sum(axis=0)
    zeta_avg = zeta.sum(axis=0)
    theta_avg = np.arctan2(-zeta_avg, -eps_avg) + np.pi
    
    return theta_avg * max_vals /(2*np.pi)
    
from chemlab.utils import minimum_image

def periodic_add(a, b):
    return minimum_image(a + b,
                         current_system().box_vectors.diagonal())
import numexpr as ne
def periodic_distance(x0, x1, dimensions):
    # delta = np.abs(x0 - x1)
    delta = ne.evaluate('abs(x0 - x1)')
    
    #delta = np.where(delta > 0.5 * dimensions, dimensions - delta, delta)
    delta = ne.evaluate('where(delta > 0.5 * dimensions, dimensions - delta, delta)')
    
    # return np.sqrt((delta ** 2).sum(axis=-1))
    dsq = ne.evaluate('sum((delta ** 2), %d)' % (len(delta.shape) - 1))
    return ne.evaluate('sqrt(dsq)')
    

def next_frame(skip=False):
    viewer.traj_controls.next(skip)
    
def plot_crystal_radii():
    radii = []
    for i in next_frame(skip=10):
        radii.append(crystal_radius())
    
    plot(range(len(radii)), radii)
    
def crystal_radius():
    # unselect()
    select_crystal()
    geom_center = cluster_center()
    atoms = selected_atoms()
    r_array = current_system().r_array[atoms]
    
    # Periodic distance
    return periodic_distance(r_array, geom_center, current_system().box_vectors.diagonal()).max()

def crystal_size():
    select_crystal()
    return len(selected_atoms())
    
def plot_rdf(type_a, type_b):
    s = current_system()
    rd = rdf(s.r_array[s.type_array == type_a],
             s.r_array[s.type_array == type_b], periodic=s.box_vectors)
    plot(rd[0], rd[1])

def frame_iter(iframes):
    while True:
        try:
            yield viewer.traj_controls.next(iframes)
            QtGui.qApp.processEvents()
        except StopIteration:
            break


def local_densities():
    lds = []
    t = []
    
    goto_time(0)
    for i in frame_iter(1):
        QtGui.qApp.processEvents()
        lds.append(order_par())
        t.append(current_time())
        
    return t, lds



def event_rate(t=None, ld=None, sigma=4, threshold=14):
    if t is None or ld is None:
        t, ld = local_densities()
    
    ld = np.array(ld)
    t = np.array(t)
    
    attachments = []
    detachments = []

    
    # First of all, filter this guy
    for i in range(ld.shape[1]):
        signal = ld[:, i]
        signal = scipy.ndimage.gaussian_filter1d(signal, sigma)
        signal_copy = signal.copy()
        signal = np.empty_like(signal)
        signal[signal_copy >= threshold] = 1.0
        signal[signal_copy < threshold] = 0.0

        # Determine the fucking events
        difference = np.diff(signal)
        df = difference.nonzero()[0]

        attachments.extend(t[df[difference[df] > 0.0]])
        detachments.extend(t[df[difference[df] < 0.0]])

    # Rate of attachments/detachments?
    hist_a, bin_edges = np.histogram(attachments, bins=100,
                                     range=(min(t), max(t)))
    hist_d, bin_edges = np.histogram(detachments, bins=100,
                                     range=(min(t), max(t)))
    
    # We basically histogrammed with certain bins, it means tot events
    # per bin, to get a time rate, I should divide by the bin size
    
    ps_per_bin = (max(t) - min(t))/100.0
    ns_per_bin = ps_per_bin/1000
    
    return bin_edges[1:], hist_a/ns_per_bin, hist_d/ns_per_bin


def dissolution_profile(directory=None, iframes=1):

    if directory is not None:
        load_system(directory + 'start.gro')
        load_trajectory(directory + 'traj.xtc')
    
    goto_time(0)
    select_molecules('H2O')
    hide_selected()
    
    t = []
    sizes = []
    for i in frame_iter(iframes):
        sizes.append(crystal_size())
        t.append(current_time())
        print t[-1], sizes[-1]
        if sizes[-1] == 0:
            break
    
    return t, sizes


def radius_profile(directory=None, iframes=100):

    if directory is not None:
        load_system(directory + 'start.gro')
        load_trajectory(directory + 'traj.xtc')
    
    goto_time(0)
    select_molecules('H2O')
    hide_selected()
    
    t = []
    sizes = []
    for i in frame_iter(iframes):
        sizes.append(crystal_radius())
        t.append(current_time())
        if sizes[-1] == 0:
            break
    
    return t, sizes


def pub_style():
    background_color('white')
    add_post_processing(SSAOEffect, kernel_size=128)
    add_post_processing(FXAAEffect)
    add_post_processing(GammaCorrectionEffect)

def potential_on_atoms():
    select_crystal()
    s = current_system()
    s.charge_array[s.type_array == 'Na'] = 1.0
    s.charge_array[s.type_array == 'Cl'] = -1.0
    
    # Let's do it arraywise
    ri = s.r_array[selected_atoms()][np.newaxis, :, :]
    rj = s.r_array[selected_atoms()][:, np.newaxis, :]
    
    rij = periodic_distance(ri, rj, s.box_vectors.diagonal())
    
    qi = s.charge_array[selected_atoms()][np.newaxis, :]
    qj = s.charge_array[selected_atoms()][:, np.newaxis]

    qiqj = qi * qj
    
    potentials = qiqj/rij
    potentials[np.diag_indices_from(potentials)] = 0.0
    return potentials.sum(axis=0)
    
def color_potentials():
    potentials = potential_on_atoms()
    print 'Total potential', 0.5 * potentials.sum()
    
    # Normalize and all positive
    potentials -=  potentials.min()
    potentials /= potentials.max() - potentials.min()
    
    from chemlab.graphics import colors
    colarray = np.array([colors.mix('cyan', 'red', pt) for pt in potentials])
    change_color(colarray)

from chemlab.graphics.pickers import ray_spheres_intersection

def select_surface():
    center_on_crystal()
    center = cluster_center()
    
    lasts = []
    for theta in np.arange(0, np.pi, 0.05):
        for phi in np.arange(0, 2.0 * np.pi, 0.1):
            
            r = 1.0
            
            sample_dir = np.zeros(3)
            sample_dir[0] = np.sin(theta) * np.cos(phi)
            sample_dir[1] = np.sin(theta) * np.sin(phi)
            sample_dir[2] = np.cos(theta)
        
            intersections, dist = ray_spheres_intersection(center,
                                                           sample_dir,
                                                           current_system().r_array[selected_atoms()],
                                                           np.array([0.3]
                                                                *
                                                                len(selected_atoms())))
        
            if intersections:
                lasts.append(selected_atoms()[intersections[-1]])
            
    clear_selection()
    select_indices(list(set(lasts)))
    
def surface_dissolution_rate(iframes=1):
    goto_time(0)
    
    surf = []
    t = []
    for i in frame_iter(iframes):
        select_surface()
        natoms = len(selected_atoms())
        surf.append(natoms)
        t.append(current_time())
        if natoms == 0:
            break
    
    return np.array(t), np.array(surf)

from chemlab.core import *
from chemlab.db import *
from chemlab.io import *

def makebox(nwater):
    db = ChemlabDB()
    spce = db.get('molecule', 'gromacs.spce')
    n = nwater**(1.0/3.0)
    l = np.ceil(n + 1) * 0.3
    wbox = random_lattice_box([spce], [nwater], [l, l, l], spacing=[0.3, 0.3, 0.3])
    
    display(wbox)

def makewall():
    db = ChemlabDB()
    na = db.get('molecule', 'gromacs.na+')
    cl = db.get('molecule', 'gromacs.cl-')
    spce = db.get('molecule', 'gromacs.spce')
     
    s = crystal([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]], # Fractional Positions
                [na, cl], # Molecules
                225, # Space Group
                cellpar = [.54, .54, .54, 90, 90, 90], # unit cell parameters
                repetitions = [4, 7, 7]) # unit cell repetitions in each direction

    # Fill the rest with water
    wbox = random_lattice_box([spce], [4000], [0.54 * 16, 0.54 * 7,
                                               0.54 * 7],
                              spacing=[0.3, 0.3,
                                       0.3])

    wbox.bonds = np.array([])
    wbox.r_array[:, 0] += 0.54 * 4
    
    s2 = merge_systems(wbox, s, 0.5)
    
    display(s2)
    
    
def makesphere(size):
    db = ChemlabDB()
    na = db.get('molecule', 'gromacs.na+')
    cl = db.get('molecule', 'gromacs.cl-')

    spce = db.get('molecule', 'gromacs.spce')

    s = crystal([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]], # Fractional Positions
                [na, cl], # Molecules
                225, # Space Group
                cellpar = [.54, .54, .54, 90, 90, 90], # unit cell parameters
                repetitions = [13, 13, 13]) # unit cell repetitions in each directio

    # let's cut this crap
    center = s.r_array.sum(0) / len(s.r_array)
    s.r_array -= center
    # for 1000 0.22 * 13
    # for 500
    toremove = ((s.r_array) ** 2).sum(axis=1) < size
    toremove = toremove.nonzero()[0]

    s = subsystem_from_atoms(s, toremove)
    display(s)