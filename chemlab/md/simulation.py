import warnings
import itertools
class Simulation(object):
    
    def __init__(self, system, potential, length=1.0, integrator='md', dt=2e-6, dt_io=2e-4, 
                 cutoff=0.9, pme=True, temperature=300, thermostat='v-rescale',
                 pressure=1.0, barostat='berendsen', constraints='none',
                 annealing=[]):
        
        self.system = system
        self.potential = potential
        
        self.integrator = integrator
        self.dt = dt
        self.dt_io = dt_io
        self.length = length
        
        self.pme = pme
        self.cutoff = cutoff
        
        self.temperature = temperature
        self.thermostat = thermostat
        
        self.pressure = pressure
        self.barostat = barostat
        self.constraints = constraints
        
        self.annealing = annealing

def to_mdp(simulation):
    
    length = simulation.length * 1000
    dt = simulation.dt * 1000
    dt_io = simulation.dt_io * 1000
    annealing = simulation.annealing
    
    r = ''
    r += 'integrator = {}\n'.format(simulation.integrator)
    r += 'dt = {:f}\n'.format(dt)
    r += 'nsteps = {:d}\n'.format(int(length / dt))
    r += 'nstlog = {:d}\n'.format(int(dt_io / dt))
    r += 'nstenergy = {:d}\n'.format(int(dt_io / dt))
    r += 'nstxtcout = {:d}\n'.format(int(dt_io / dt))
    
    if simulation.potential.intermolecular.type == 'custom':
            
        vdwtype = coulombtype = 'user'
        if simulation.pme:
            coulombtype = 'pme-user'
        
        r += 'energygrps = {}\n'.format(" ".join(simulation.potential.intermolecular.particles))
        r += 'energygrp-table = {}\n'.format(" ".join(itertools.chain(*simulation.potential.intermolecular.special_pairs)))
    else:
        vdwtype = 'Cut-off'
        coulombtype = "pme" if simulation.pme else "Cut-off"
    
    r += 'vdwtype = {}\n'.format(vdwtype)
    
    r += 'rlist = {:f}\n'.format(simulation.cutoff)
    
    r += 'coulombtype = {}\n'.format(coulombtype)
    r += 'rcoulomb = {:f}\n'.format(simulation.cutoff)
    r += 'rvdw = {:f}\n'.format(simulation.cutoff)
    r += 'tcoupl = v-rescale\n'
    r += 'tc-grps = System\n'
    r += 'ref_t = {:f}\n'.format(simulation.temperature)
    r += 'tau_t = {:f}\n'.format(0.1)
    
    if annealing:
        
        r += "annealing = single\n"
        r += "annealing-npoints = {}\n".format(len(annealing))
        # Time from ns to ps
        r += "annealing-time = {}\n".format(" ".join(str(a[0] * 1000) for a in annealing))
        r += "annealing-temp = {}\n".format(" ".join(str(a[1]) for a in annealing)) 
    
    if simulation.pressure is None:
        r += 'pcoupl = {}\n'.format('no')
    else:
        r += 'pcoupl = {}\n'.format(simulation.barostat)
        r += 'compressibility = 4.5e-5\n'
        r += 'ref_p = {}\n'.format(simulation.pressure)
    
    r += 'constraints = {}\n'.format(simulation.constraints)
    
    return r
    
