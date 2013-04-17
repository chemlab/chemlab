from chemlab.db import masses
from chemlab.molsim import cforces2 as cforces

def euler(r0, v0, a0, dt):
    dv = a0*dt
    v_n = v0 + dv
    dr = dt*v_n
    r_n = r0 + dr
    return r_n, v_n
    
def velocity_verlet(r0, v0, a0, dt, afunc):
    v_half = v0 + 0.5*a0*dt
    r_t = r0 + v_half*dt
    a_t = afunc(r_t)
    v_t = v_half + 0.5*a_t*dt
    
    return r_t, v_t, a_t

def evolve_generator(sys, t, tstep, periodic=True, method="velocity_verlet"):
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
    
    first_step = True
    
    yield sys, 0.0
    for i in range(steps):
        yield sys, tstep*i*1e12
        
        rarray = sys.rarray * 1e-9
        varray = sys.varray * 1e3 # nm/ps to m/s
        
        if method == "euler":
            farray = cforces.lennard_jones(rarray, sys.type, periodic=periodic)        
            rarray, varray = euler(rarray, varray, farray/m, tstep)
            
        elif method == "velocity_verlet":
            if first_step:
                farray = cforces.lennard_jones(rarray, sys.type, periodic=periodic)        
                aarray = farray/m
            
            rarray, varray, aarray = velocity_verlet(rarray, varray, aarray, tstep,
                                                     lambda rarray: cforces.lennard_jones(rarray, sys.type, periodic=periodic)/m)
        
        # Add periodic conditions
        if periodic:
            i_toopositive = rarray > boxsize * 0.5
            rarray[i_toopositive] -= boxsize  
            i_toonegative = rarray < - boxsize * 0.5
            rarray[i_toonegative] += boxsize
        
        # Converting back
        sys.rarray = rarray * 1e9 
        sys.varray = varray * 1e-3

        first_step = False
