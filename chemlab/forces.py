from .mathutils import direction, distance

# Eps in meV
# sigma in nm
lj_params = {
    "Ne" : { "eps"  : 3.0840,
             "sigma": 0.2782}
    
}

def lennard_jones(a, b):
    d = direction(a.coords, b.coords)
    r = distance(a.coords, b.coords)
    eps = lj_params[a.type]["eps"]
    sigma = lj_params[a.type]["sigma"]
    
    return -d*24*eps*(2*(sigma**12 / r**13) - (sigma**6 / r**7))
