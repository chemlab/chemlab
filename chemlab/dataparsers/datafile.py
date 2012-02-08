from gamess import GamessDataParser

parsers = { "gamout": GamessDataParser}

class DataFile(object):
    def __init__(self, filename, format):
        Parser = parsers.get(format, None)
        if not Parser:
            raise ValueError("Format "+format+" not supported.")
        self.parser = Parser(filename)

    def __getitem__(self, item):
        return self.parser.get_property(item)

