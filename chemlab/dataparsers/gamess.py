
class GamessDataParser(object):
    def __init__(self, filename):
        self._filename = filename
        self._params = self.parse_params()
        
    def avail_properties(self):
        """Check the data file to see the available properties.
        
        """
        if self._params == 4:
            return 0
        
    def get_property(self, prop):
        if prop == "irc":
            return self._get_irc()

    def _get_irc(self):
        pass

        
