

class Cell:
    key = None
    lines = None

    def __init__(self, key=None, lines=None):
        assert type(key) is str
        key = key.lower()
        assert key in cellKnown, '{} not a known cell'.format(key)
        self.key = key

        assert type(lines) is list
        assert all(type(line) == str for line in lines)
        self.lines = lines



cellKnown = ['lattice_cart']

