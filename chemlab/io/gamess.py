import re
from .textutils import greplines, grep_split, sections
from .. import Molecule, Atom

# Error codes
OK = 0
GEOM_NOT_LOCATED = 1
UNKNOWN = 2

class GamessDataParser(object):
    
    def __init__(self, filename):
        
        self.text = open(filename).read()
        self.lines = self.text.splitlines()

    def get_avail_properties(self):
        avail_props = set()
        # Get the input
        inputc = greplines("INPUT CARD>", self.lines)
        # get rid of INPUT CARD> string and join the lines in a single
        # string
        inputc = '\n'.join(l[12:] for l in inputc)
        runtyp = parse_card("runtyp", inputc, "energy")

        supported_modes = ("energy", "irc")
        
        if runtyp in supported_modes:
            avail_props.add(runtyp)

        return avail_props
    
    def get_property(self, prop):
        if prop == "irc":
            return self._parse_irc()
        if prop == "energy":
            return self._parse_tddft()
        
    def _parse_irc(self):
        """Parse intrinsic reaction coordinate calculation.
        returns a dictionary containing:

        geometries : a list of Molecule instances representing each point in the IRC
        energies   : a list of total energies (Hartree)
        distances   : distance from the starting point in mass-weighted coords (bohr \sqrt(amu))
        """
        irc_geoms = sections(re.escape("***** NEXT POINT ON IRC FOUND *****"),
                             re.escape("INTERNUCLEAR DISTANCES (ANGS.)"),
                             self.text)
        
        # get and store the energy
        energies = [entry.splitlines()[5] for entry in irc_geoms] # The total energy line
        energies = [float(entry.split()[3]) for entry in energies]

        # get and store the distance
        distances = [entry.splitlines()[4] for entry in irc_geoms] # The path distance line
        distances = [float(entry.split()[5]) for entry in distances]
        
        # strip the garbage
        irc_geoms = ['\n'.join(i.splitlines()[11:-1]) for i in irc_geoms]
        irc_geoms = [self._parse_geometry(i) for i in irc_geoms]
        
        return {"geometries": irc_geoms,
                "energies": energies,
                "distances": distances}
        
    def _parse_geometry(self, geom):
        """Parse a geometry string and return Molecule object from
        it.

        """
        atoms = []
        for i, line in enumerate(geom.splitlines()):
           sym, atno, x, y, z = line.split()
           atoms.append(Atom(sym, [float(x), float(y), float(z)], id=i))
        
        return Molecule(atoms)
        
    def parse_optimize(self):
        """Parse the ouput resulted of a geometry optimization. Or a
        saddle point.

        """
        match = re.search("EQUILIBRIUM GEOMETRY LOCATED", self.text)
        spmatch = "SADDLE POINT LOCATED" in self.text
        located = True if match or spmatch else False

        points = grep_split(" BEGINNING GEOMETRY SEARCH POINT NSERCH=",
                            self.text)
        if self.tddft == "excite":
            points = [self.parse_energy(point) for point in points[1:]]
        else:
            regex = re.compile(r'NSERCH:\s+\d+\s+E=\s+([+-]?\d+\.\d+)')
            points = [Energy(states=[State(0,None,float(m.group(1)), 0.0, 0.0)]) for m in regex.finditer(self.text)]
        
        # Error handling
        if "FAILURE TO LOCATE STATIONARY POINT, TOO MANY STEPS TAKEN" in self.text:
            self.errcode = GEOM_NOT_LOCATED
            self.errmsg = "too many steps taken: %i"%len(points)
        
        if located:
            self.errcode = OK
        
        return Optimize(points=points)
        

    def _parse_tddft(self):
        """Parse the output resulted from a tddft calculation.
        
        """
        text = self.text
        energies = sections("SUMMARY OF TDDFT RESULTS",
                            "DONE WITH TD-DFT EXCITATION ENERGIES",
                            text)

        lines = energies[0].splitlines()
        regex = re.compile("""
                           \s+(\d+)   # State Number
                           \s+([ ^]+)  # State sym
                           \s+([+-]?\d+\.\d+) # Tot Energy  
                           \s+([+-]?\d+\.\d+) # Exc Energy
                               (\s+([+-]?\d+\.\d+) # 
                                \s+([+-]?\d+\.\d+) # Dipole moment
                                \s+([+-]?\d+\.\d+) # 
                                \s+([+-]?\d+\.\d+))? # Oscillator strength
                           """, flags=re.VERBOSE)

        states = []
        for line in lines:
            match = regex.match(line)
            if match:
                # Check for strange behaviour of symmetry
                if not re.match("\w+",match.group(4)):
                    raise ValueError("Strange symmetry string: %s"%match.group(4))
                 
                osc_strength = float(match.group(9)) if match.group(9) else 0.000
                states.append({"num": int(match.group(1)), "sym": match.group(4),
                               "strength": osc_strength})
        return {"states": states}
    


def parse_card(card, text, default=None):
    """Parse a card from an input string
    
    """
    match = re.search(card.lower() + r"\s*=\s*(\w+)", text.lower())
    return match.group(1) if match else default

def parse_inpsec(sec, text):
    """Parse a section in the input file denoted by parse_inpspec.

    """
    return  sections(" \$"+sec, "\$end", text.lower(), line=False)[0]


        
