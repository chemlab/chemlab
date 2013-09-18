from chemlab.utils import distances_within
from core import *
from select_ import *
from display import *
import numpy as np


def order_par():
    # Hidden
    visible = visible_atoms()
    
    r_array = current_system().r_array[visible]
    box = current_system().box_vectors
    
    local_dens = []    
    for r in r_array:
        local_dens.append(len(distances_within([r], r_array, 
                        0.60, periodic=box.diagonal())))
    
    local_dens = np.array(local_dens)
    
    return local_dens

def select_crystal():
    ld = order_par()
    current_selection().select_atoms(visible_atoms()[ld > 11.0])

def center_on_crystal():
    select_crystal()
    center = cluster_center()
    current_system().r_array -= center
    current_system().r_array += 0.5 * current_system().box_vectors.diagonal()
    current_system().r_array = minimum_image(current_system().r_array, current_system().box_vectors.diagonal())
    current_representation().update_positions(current_system().r_array)
    
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
def periodic_distance(x0, x1, dimensions):
    delta = np.abs(x0 - x1)
    delta = np.where(delta > 0.5 * dimensions, dimensions - delta, delta)
    return np.sqrt((delta ** 2).sum(axis=-1))

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
    
from chemlab.molsim.analysis import rdf
from pylab import *

def plot_rdf(type_a, type_b):
    s = current_system()
    rd = rdf(s.r_array[s.type_array == type_a],
             s.r_array[s.type_array == type_b], periodic=s.box_vectors)
    plot(rd[0], rd[1])

from PyQt4 import QtGui

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
        t.append(current_traj_time())
        
    return t, lds

import numpy as np
import scipy.ndimage

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
    hist_a, bin_edges = np.histogram(attachments, bins=100, range=(min(t), max(t)))
    hist_d, bin_edges = np.histogram(detachments, bins=100, range=(min(t), max(t)))
    
    return bin_edges[1:], hist_a, hist_d
    
def dissolution_profile(directory=None, iframes=100):

    if directory is not None:
        load_system(directory + 'start.gro')
        load_trajectory(directory + 'traj.xtc')
    
    goto_time(0)
    select_molecules('H2O')
    hide()
    
    t = []
    sizes = []
    for i in frame_iter(iframes):
        sizes.append(crystal_size())
        t.append(current_traj_time())
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
    hide()
    
    t = []
    sizes = []
    for i in frame_iter(iframes):
        sizes.append(crystal_radius())
        t.append(current_traj_time())
        if sizes[-1] == 0:
            break
    
    return t, sizes

def pub_style():
    background_color('white')
    add_post_processing(SSAOEffect, kernel_size=128)
    add_post_processing(FXAAEffect)
    add_post_processing(GammaCorrectionEffect)

