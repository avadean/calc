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


def assertBetween(value=None, minimum=None, maximum=None, key=None):
    assert type(value) in [int, float]
    assert type(minimum) in [int, float]
    assert type(maximum) in [int, float]

    if minimum <= value <= maximum:
        return

    if key is None:
        raise ValueError('Value of {} outside range of allowed values: {} to {}'.format(value,
                                                                                        minimum,
                                                                                        maximum))
    else:
        assert type(key) is str

        raise ValueError('Value of {} for {} outside range of allowed values: {} to {}'.format(value,
                                                                                               key,
                                                                                               minimum,
                                                                                               maximum))


def getFromDict(key=None, dct=None, strict=True):
    assert type(key) is str
    assert type(dct) is dict
    assert type(strict) is bool

    key = key.lower()

    value = dct.get(key, None)

    if value is None and strict:
        raise ValueError('Key {} does not have a value'.format(key))

    return value


def getNiceUnit(unit=None, strict=True):
    return getFromDict(key=unit, dct=unitToNiceUnit, strict=strict)


def getAllowedUnits(unitType=None, strict=True):
    return getFromDict(key=unitType, dct=unitTypeToUnit, strict=strict)


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

stringToVariableDirectories = {'soc': ['scalar_soc_false',
                                       'spinor_soc_false',
                                       'spinor_soc_true'],

                               'density': ['density_in_x',
                                           'density_in_y',
                                           'density_in_z'],

                               'socdensity': ['scalar_soc_false',
                                              'spinor_soc_false',
                                              'spinor_soc_true_x',
                                              'spinor_soc_true_y',
                                              'spinor_soc_true_z'],

                               'zbfield': ['00T', '01T', '02T', '03T', '04T', '05T', '06T', '07T', '08T', '09T', '10T']
                               }
