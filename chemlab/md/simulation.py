
class Simulation(object):
    
    def __init__(self, length, integrator='md', dt=2e-6, dt_io=2e-4, 
                 cutoff=0.9, pme=True, temperature=300, thermostat='v-rescale',
                 pressure=1.0, barostat='berendsen'):
        
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

def to_mdp(simulation):
    
    length = simulation.length * 1000
    dt = simulation.dt * 1000
    dt_io = simulation.dt_io * 1000
    
    r = ''
    r += 'integrator = {}\n'.format(simulation.integrator)
    r += 'dt = {:f}\n'.format(dt)
    r += 'nsteps = {:d}\n'.format(int(length / dt))
    r += 'nstlog = {:d}\n'.format(int(dt_io / dt))
    r += 'nstenergy = {:d}\n'.format(int(dt_io / dt))
    r += 'nstxtcout = {:d}\n'.format(int(dt_io / dt))
    
    r += 'vdwtype = Cut-off\n'
    r += 'rlist = {:f}\n'.format(simulation.cutoff)
    
    r += 'coulombtype = pme\n'
    r += 'rcoulomb = {:f}\n'.format(simulation.cutoff)
    r += 'rvdw = {:f}\n'.format(simulation.cutoff)
    r += 'tcoupl = v-rescale\n'
    r += 'tc-grps = System\n'
    r += 'ref_t = {:f}\n'.format(simulation.temperature)
    r += 'tau_t = {:f}\n'.format(0.1)
    
    r += 'pcoupl = berendsen\n'
    r += 'compressibility = 4.5e-5\n'
    r += 'ref_p = 1.0\n'
    
    r += 'constraints = all-bonds\n'
    
    return r
    
