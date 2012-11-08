from chemlab.data import masses
from chemlab.molsim import cforces

def euler(r0, v0, a0, dt):
    dv = a0*dt
    v_n = v0 + dv
    dr = dt*v_n
    r_n = r0 + dr
    return r_n, v_n

def evolve_generator(sys, t, tstep, periodic=True):
    # First let's convert all in si units
    t *= 1e-12
    tstep *= 1e-12
    
    steps = int(t/tstep)
    m = masses.typetomass[sys.type] * 1.660538921e-27 # Mass in Kg
    boxsize = sys.boxsize*1e-9
    
    if periodic == True:
        periodic = boxsize
    else:
        periodic = False
    
    for i in range(steps):
        yield sys, tstep*i*1e12
        
        rarray = sys.rarray * 1e-9
        varray = sys.varray * 1e3 # nm/ps to m/s
        
        farray = cforces.lennard_jones(rarray, sys.type, periodic=periodic)        
        rarray, varray = euler(rarray, varray, farray/m, tstep)
        
        # Add periodic conditions
        if periodic:
            i_toopositive = rarray > boxsize * 0.5
            rarray[i_toopositive] -= boxsize  
            i_toonegative = rarray < - boxsize * 0.5
            rarray[i_toonegative] += boxsize
        
        # Converting back
        sys.rarray = rarray * 1e9 
        sys.varray = varray * 1e-3