

class Cell:
    key = None
    lines = None

    def __init__(self, key=None, lines=None):
        assert type(key) is str
        assert key.lower() in cellKnown, '{} not a known cell'.format(key)
        self.key = key.lower()

        assert type(lines) is list
        assert all(type(line) == str for line in lines)
        self.lines = lines



cellKnown = ['lattice_cart',

             'external_bfield']


shortcutCells = {}
