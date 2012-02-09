import re
from .textutils import greplines, grep_split, sections

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
        avail_props.add(runtyp)

        return avail_props
    
    def get_property(self, prop):
        if prop == "irc":
            return self._parse_irc()
        
    def _parse_irc(self):
        """Parse intrinsic reaction coordinate calculation.
        
        """
        irc_geoms = sections("***** NEXT POINT ON IRC FOUND *****",
                             "INTERNUCLEAR DISTANCES (ANGS.)",
                             self.text)
        print irc_geoms
        # then parse the geom in between
        
        
        
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
        

    def parse_energy(self, text):
        """Parse the output resulted from a single point calculation.
        
        """
        if self.tddft == "excite":
            energies = sections("SUMMARY OF TDDFT RESULTS",
                                "DONE WITH TD-DFT EXCITATION ENERGIES",
                                text)
            
            lines = energies[0].splitlines()
            regex = re.compile("""
                               \s+(\d+)   # State Number
                               \s+([^ ])  # State sym
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
                    osc_strength = float(match.group(9)) if match.group(9) else 0.000
                    states.append(
                        State(int(match.group(1)), match.group(2),
                              float(match.group(3)), float(match.group(4)), osc_strength)
                    )
            # if all is parsed status is OK for this energy
            self.errcode = OK
            return Energy(states=states)
    


def parse_card(card, text, default=None):
    """Parse a card from an input string
    
    """
    match = re.search(card.lower() + r"\s*=\s*(\w+)", text.lower())
    return match.group(1) if match else default

def parse_inpsec(sec, text):
    """Parse a section in the input file denoted by parse_inpspec.

    """
    return  sections(" \$"+sec, "\$end", text.lower(), line=False)[0]


        
