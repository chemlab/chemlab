from gamess import GamessDataParser
from tinker import TinkerXyzDataParser
import os

parsers = { "gamout": GamessDataParser,
            "tinkerxyz": TinkerXyzDataParser}

class DataFile(object):
    def __init__(self, filename, format):
        Parser = parsers.get(format, None)
        self.filename = filename
        
        if not os.path.exists(filename):
            raise ValueError("File %s does not exists."%filename)
            
        if not Parser:
            raise ValueError("Format "+format+" not supported.")
            
        self.parser = Parser(filename)
        self.properties = self.parser.get_avail_properties()

    def __getitem__(self, item):
        if item in self.properties:
            return self.parser.get_property(item)
        else:
            raise ValueError("Property %s not present or not parsable in %s"%
                             (item, self.filename))
