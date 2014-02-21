import re

def guess_type(typ):
    '''Guess the atom type from purely heuristic considerations.'''
    # Strip useless numbers
    match = re.match("([a-zA-Z]+)\d*", typ)
    if match:
        typ = match.groups()[0]
        return typ
