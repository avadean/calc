from collections import Counter

# Variables for running calculations.
serialDefault = False
bashAliasesFileDefault = '/home/dean/.bash_aliases'
notificationAliasDefault = 'noti'
queueFileDefault = '/home/dean/tools/files/castep_queue.txt'


def createDirectories(*directoryNames):

    for directory in directoryNames:
        if type(directory) is list:
            assert all(type(name) is str for name in directory)
        else:
            assert type(directory) is str,\
                'Specify only shortcut strings or lists for directories, not {}'.format(type(directory))

    directoryNames = [(getVariableDirectories(directory.strip().lower()) if type(directory) is str else directory)
                      for directory in directoryNames]

    directoryNames = [[string.strip() for string in direc] for direc in directoryNames]

    return directoryNames


class Block:
    pass


class VectorInt:
    def __init__(self, x=None, y=None, z=None, vector=None):
        if vector is None:
            assert type(x) is int
            assert type(y) is int
            assert type(z) is int

            self.x = x
            self.y = y
            self.z = z

        else:
            if type(vector) is VectorInt:
                self.x = vector.x
                self.y = vector.y
                self.z = vector.z

            elif type(vector) is VectorFloat:

                assert vector.x.is_integer() and vector.y.is_integer() and vector.z.is_integer()

                self.x = int(vector.x)
                self.y = int(vector.y)
                self.z = int(vector.z)

            elif type(vector) is str and isVectorInt(vector):
                values = vector.split()

                self.x = int(values[0].strip())
                self.y = int(values[1].strip())
                self.z = int(values[2].strip())

            else:
                raise TypeError('Vector input to VectorInt must be a 3 str-int-vector, VectorInt or int-VectorFloat')

    def __str__(self):
        return '{:>3d}  {:>3d}  {:>3d}'.format(self.x, self.y, self.z)


class VectorFloat:
    def __init__(self, x=None, y=None, z=None, vector=None):
        if vector is None:
            assert type(x) is float
            assert type(y) is float
            assert type(z) is float

            self.x = x
            self.y = y
            self.z = z

        else:
            if type(vector) is VectorInt:
                self.x = float(vector.x)
                self.y = float(vector.y)
                self.z = float(vector.z)

            elif type(vector) is VectorFloat:
                self.x = vector.x
                self.y = vector.y
                self.z = vector.z

            elif type(vector) is str and (isVectorInt(vector) or isVectorFloat(vector)):
                values = vector.split()

                self.x = float(values[0].strip())
                self.y = float(values[1].strip())
                self.z = float(values[2].strip())

            else:
                raise TypeError('Vector input to VectorFloat must be a 3 vector as a str, VectorInt or VectorFloat')

    def __str__(self):
        return '{:>12.4f}  {:>12.4f}  {:>12.4f}'.format(self.x, self.y, self.z)


def stringToValue(value):
    assert type(value) is str

    if value.lower() in ['t', 'true']:
        return True

    elif value.lower() in ['f', 'false']:
        return False

    elif isInt(value):
        return int(float(value))

    elif isFloat(value):
        return float(value)

    elif isVectorInt(value):
        values = value.split()

        x = int(float(values[0].strip()))
        y = int(float(values[1].strip()))
        z = int(float(values[2].strip()))

        return VectorInt(x, y, z)

    elif isVectorFloat(value):
        values = value.split()

        x = float(values[0].strip())
        y = float(values[1].strip())
        z = float(values[2].strip())

        return VectorFloat(x, y, z)

    else:
        return value


def isInt(x):
    assert type(x) is str

    try:
        a = float(x)
        b = int(a)
    except (TypeError, ValueError):
        return False
    else:
        return a == b


def isFloat(x):
    assert type(x) is str

    try:
        float(x)
    except (TypeError, ValueError):
        return False
    else:
        return True


def isVectorInt(vector):
    assert type(vector) is str

    parts = vector.split()

    if len(parts) == 3:
        x = parts[0].strip()
        y = parts[1].strip()
        z = parts[2].strip()

        if isInt(x) and isInt(y) and isInt(z):
            return True

    return False


def isVectorFloat(vector):
    assert type(vector) is str

    parts = vector.split()

    if len(parts) == 3:
        x = parts[0].strip()
        y = parts[1].strip()
        z = parts[2].strip()

        if isFloat(x) and isFloat(y) and isFloat(z):
            return True

    return False


def assertCount(lst=None, count=1):
    assert type(lst) is list
    assert type(count) is int

    counter = Counter(lst)
    assert all(val == count for val in counter.values()), \
        '{} must be specified {} time(s)'.format(counter.most_common(1)[0][0], count)


def assertBetween(value=None, minimum=None, maximum=None, key=None):
    assert type(value) in [int, float]
    assert type(minimum) in [int, float]
    assert type(maximum) in [int, float]

    if key is not None:
        assert type(key) is str

    assert minimum <= value <= maximum,\
        'Value of {}{} outside range of allowed values: {} to {}'.format(value,
                                                                         ' for {}'.format(key) if key is not None else '',
                                                                         minimum,
                                                                         maximum)


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


def getVariableDirectories(string=None):
    """ This function gets a specific shortcut from a string.
        The string will map to a list that contains several
        directory names. """

    assert type(string) is str

    variableDirectories = stringToVariableDirectories.get(string.strip().lower(), None)

    assert variableDirectories is not None, 'Shortcut to variable directories {} not recognised'.format(string)

    return variableDirectories


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

stringToVariableDirectories = {'halides':['001_HF', '002_HCl', '003_HBr', '004_HI'],

                               'soc': ['001_scalar_soc_false',
                                       '002_spinor_soc_false',
                                       '003_spinor_soc_true'],

                               'density': ['density_in_x',
                                           'density_in_y',
                                           'density_in_z'],

                               'socdensity': ['001_scalar_soc_false',
                                              '002_spinor_soc_false',
                                              '003_spinor_soc_true_x',
                                              '003_spinor_soc_true_y',
                                              '003_spinor_soc_true_z'],

                               'hyperfinebfield': ['00T/density_in_x', '00T/density_in_y', '00T/density_in_z',
                                                   '01T/density_in_x', '01T/density_in_y', '01T/density_in_z',
                                                   '02T/density_in_x', '02T/density_in_y', '02T/density_in_z',
                                                   '03T/density_in_x', '03T/density_in_y', '03T/density_in_z',
                                                   '04T/density_in_x', '04T/density_in_y', '04T/density_in_z',
                                                   '05T/density_in_x', '05T/density_in_y', '05T/density_in_z',
                                                   '06T/density_in_x', '06T/density_in_y', '06T/density_in_z',
                                                   '07T/density_in_x', '07T/density_in_y', '07T/density_in_z',
                                                   '08T/density_in_x', '08T/density_in_y', '08T/density_in_z',
                                                   '09T/density_in_x', '09T/density_in_y', '09T/density_in_z',
                                                   '10T/density_in_x', '10T/density_in_y', '10T/density_in_z'],

                               'hyperfinetensbfield': ['000T/density_in_x', '000T/density_in_y', '000T/density_in_z',
                                                       '010T/density_in_x', '010T/density_in_y', '010T/density_in_z',
                                                       '020T/density_in_x', '020T/density_in_y', '020T/density_in_z',
                                                       '030T/density_in_x', '030T/density_in_y', '030T/density_in_z',
                                                       '040T/density_in_x', '040T/density_in_y', '040T/density_in_z',
                                                       '050T/density_in_x', '050T/density_in_y', '050T/density_in_z',
                                                       '060T/density_in_x', '060T/density_in_y', '060T/density_in_z',
                                                       '070T/density_in_x', '070T/density_in_y', '070T/density_in_z',
                                                       '080T/density_in_x', '080T/density_in_y', '080T/density_in_z',
                                                       '090T/density_in_x', '090T/density_in_y', '090T/density_in_z',
                                                       '100T/density_in_x', '100T/density_in_y', '100T/density_in_z'],

                               'hyperfinehundredsbfield': ['0000T/density_in_x', '0000T/density_in_y', '0000T/density_in_z',
                                                           '0100T/density_in_x', '0100T/density_in_y', '0100T/density_in_z',
                                                           '0200T/density_in_x', '0200T/density_in_y', '0200T/density_in_z',
                                                           '0300T/density_in_x', '0300T/density_in_y', '0300T/density_in_z',
                                                           '0400T/density_in_x', '0400T/density_in_y', '0400T/density_in_z',
                                                           '0500T/density_in_x', '0500T/density_in_y', '0500T/density_in_z',
                                                           '0600T/density_in_x', '0600T/density_in_y', '0600T/density_in_z',
                                                           '0700T/density_in_x', '0700T/density_in_y', '0700T/density_in_z',
                                                           '0800T/density_in_x', '0800T/density_in_y', '0800T/density_in_z',
                                                           '0900T/density_in_x', '0900T/density_in_y', '0900T/density_in_z',
                                                           '1000T/density_in_x', '1000T/density_in_y', '1000T/density_in_z'],

                               'hyperfinekilosbfield': ['00kT/density_in_x', '00kT/density_in_y', '00kT/density_in_z',
                                                       '01kT/density_in_x', '01kT/density_in_y', '01kT/density_in_z',
                                                       '02kT/density_in_x', '02kT/density_in_y', '02kT/density_in_z',
                                                       '03kT/density_in_x', '03kT/density_in_y', '03kT/density_in_z',
                                                       '04kT/density_in_x', '04kT/density_in_y', '04kT/density_in_z',
                                                       '05kT/density_in_x', '05kT/density_in_y', '05kT/density_in_z',
                                                       '06kT/density_in_x', '06kT/density_in_y', '06kT/density_in_z',
                                                       '07kT/density_in_x', '07kT/density_in_y', '07kT/density_in_z',
                                                       '08kT/density_in_x', '08kT/density_in_y', '08kT/density_in_z',
                                                       '09kT/density_in_x', '09kT/density_in_y', '09kT/density_in_z',
                                                       '10kT/density_in_x', '10kT/density_in_y', '10kT/density_in_z'],

                               'bfield': ['00T', '01T', '02T', '03T', '04T', '05T', '06T', '07T', '08T', '09T', '10T']
                               }

stringToVariableDirectoriesAliases = {'xbfield': stringToVariableDirectories.get('bfield'),
                                      'ybfield': stringToVariableDirectories.get('bfield'),
                                      'zbfield': stringToVariableDirectories.get('bfield')
                                      }

stringToVariableDirectories = stringToVariableDirectories | stringToVariableDirectoriesAliases
