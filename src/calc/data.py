from collections import Counter


class Block:
    pass


class VectorInt:
    def __init__(self, x=None, y=None, z=None):
        assert type(x) is int
        assert type(y) is int
        assert type(z) is int

        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return '{:>3d}  {:>3d}  {:>3d}'.format(self.x, self.y, self.z)


class VectorFloat:
    def __init__(self, x=None, y=None, z=None):
        assert type(x) is float
        assert type(y) is float
        assert type(z) is float

        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return '{:>12.4f}  {:>12.4f}  {:>12.4f}'.format(self.x, self.y, self.z)


def assertCount(lst=None, count=1):
    assert type(lst) is list
    assert type(count) is int

    countStrings = Counter(lst)
    assert all(val == count for val in countStrings.values()), \
        '{} must be specified {} time(s)'.format(countStrings.most_common(1)[0][0], count)


def getNiceUnit(unit=None, strict=True):
    assert type(unit) is str
    assert type(strict) is bool

    unit = unit.lower()

    niceUnit = unitToNiceUnit.get(unit, None)

    if niceUnit is None and strict:
        raise ValueError('Unit {} does not have any nice units'.format(unit))

    return niceUnit


def getAllowedUnits(unitType=None, strict=True):
    assert type(unitType) is str
    assert type(strict) is bool

    unitList = unitTypeToUnit.get(unitType, None)

    if unitList is None and strict:
        raise ValueError('Unit type {} does not have any allowed units'.format(unitType))

    return unitList


unitToNiceUnit = { 'ev' : 'eV',
                   'ha' : 'Ha',
                   'j' : 'J',
                   'ry' : 'Ry',

                   'ang' : 'Ang',
                   'bohr' : 'Bohr',
                   
                   '1/ang' : '1/Ang'
                   }

unitToUnitType = { 'ev' : 'energy',
                   'ha' : 'energy',
                   'j' : 'energy',
                   'ry' : 'energy',

                   'ang' : 'length',
                   'bohr' : 'length',

                   '1/ang' : 'inverseLength'
                   }

unitTypeToUnit = { 'energy' : ['ev', 'ha', 'j', 'ry'],

                   'length' : ['ang', 'bohr'],

                   'inverseLength' : ['1/ang']
                   }
