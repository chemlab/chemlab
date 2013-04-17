'''Module to easily handle units'''

baseunits = ['kg', 'm', 'm^2', 'm^3']

# on the left there are the standard units
convtable = '''
amu = 1.660538921e-27 kg
g   = 1.0e-3 kg
nm  = 1.0e-9 m
cm  = 1.0e-2 m
cm^3 = 1.0e-6 m^3
nm^3 = 1.0e-27 m^3
'''.strip()

convmap = {}
for line in convtable.splitlines():
    deriv, eq, fac, base = line.split()
    convmap[deriv] = (float(fac), base)

def convert(value, origin, dest):
    # Base case
    if origin == dest:
        return value
        
    if origin not in convmap:
        raise Exception('convert: %s unit not supported.' % origin)
    if dest not in convmap:
        raise Exception('convert: %s unit not supported.' % dest)

    bval, bunit = convmap[origin]
    if dest in baseunits:
        return bval*value
    else:
        dval, dunit = convmap[dest]
        return bval*value / dval
    
    
    