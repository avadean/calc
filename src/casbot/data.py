from collections import Counter
from numpy import array, empty


# Variables for running calculations.
serialDefault = False
bashAliasesFileDefault = '/home/dean/.bash_aliases'
notificationAliasDefault = 'noti'
queueFileDefault = '/home/dean/tools/files/castep_queue.txt'


# Periodic table of elements.
elements = ['h' ,                                                                                                 'he',
            'li', 'be',                                                             'b' , 'c' , 'n' , 'o' , 'f' , 'ne',
            'na', 'mg',                                                             'al', 'si', 'p' , 's' , 'cl', 'ar',
            'k' , 'ca', 'sc', 'ti', 'v' , 'cr', 'mn', 'fe', 'co', 'ni', 'cu', 'zn', 'ga', 'ge', 'as', 'se', 'br', 'kr',
            'rb', 'sr', 'y' , 'zr', 'nb', 'mo', 'tc', 'ru', 'rh', 'pd', 'ag', 'cd', 'in', 'sn', 'sb', 'te', 'i' , 'xe',
            'cs', 'ba',
            'la', 'ce', 'pr', 'nd', 'pm', 'sm', 'eu', 'gd', 'tb', 'dy', 'ho', 'er', 'tm', 'yb', 'lu',
            'hf', 'ta', 'w' , 're', 'os', 'ir', 'pt', 'au', 'hg', 'tl', 'pb', 'bi', 'po', 'at', 'rn',
            'fr', 'ra',
            'ac', 'th', 'pa', 'u' , 'np', 'pu', 'am', 'cm', 'bk', 'cf', 'es', 'fm', 'md', 'no', 'lr',
            'rf', 'db', 'sg', 'bh', 'hs', 'mt', 'ds', 'rg', 'cn', 'nh', 'fl', 'mc', 'lv', 'ts', 'og' ]


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
    def __init__(self, *values, vector=None):
        if vector is None:
            assert all(type(val) is int for val in values)

            self.values = values

        else:
            if type(vector) is VectorInt:
                self.values = vector.values

            elif type(vector) is VectorFloat:
                assert all(val.is_integer() for val in vector.values)

                self.values = [int(val) for val in vector.values]

            elif type(vector) is str:
                values = [val.strip() for val in vector.split()]

                assert isInt(*values)

                self.values = [int(float(val)) for val in values]

            else:
                raise TypeError('Vector input to VectorInt must be a 3 str-int-vector, VectorInt or int-VectorFloat')

        self.type_ = len(self.values)

    def __str__(self):
        intSetting = '{:>3d}'

        return '  '.join(intSetting for _ in range(self.type_)).format(*self.values)
        #return '{:>3d}  {:>3d}  {:>3d}'.format(self.x, self.y, self.z)

    def getMagnitude(self):
        return sum(val ** 2.0 for val in self.values) ** 0.5


class VectorFloat:
    def __init__(self, *values, vector=None):
        if vector is None:
            assert all(type(val) is float for val in values)

            self.values = values

        else:
            if type(vector) is VectorInt:
                self.values = [float(val) for val in vector.values]

            elif type(vector) is VectorFloat:
                self.values = vector.values

            elif type(vector) is str:
                values = [val.strip() for val in vector.split()]

                assert isInt(*values) or isFloat(*values)

                self.values = [float(val) for val in values]

            else:
                raise TypeError('Vector input to VectorFloat must be a vector as a str, VectorInt or VectorFloat')

        self.type_ = len(self.values)

    def __str__(self):
        floatSetting = '{:>12.4f}'

        return '  '.join(floatSetting for _ in range(self.type_)).format(*self.values)
        #return '{:>12.4f}  {:>12.4f}  {:>12.4f}'.format(self.x, self.y, self.z)

    def getMagnitude(self):
        return sum(val ** 2.0 for val in self.values) ** 0.5



def strListToArray(lst=None):
    assert type(lst) is list
    assert all(type(line) is str for line in lst)

    if len(lst) == 0:
        return empty(0, dtype=float)

    assert all(len(line.split()) == len(lst[0].split()) for line in lst), 'Shape mismatch when converting to array'

    try:
        arr = array([line.split() for line in lst], dtype=float)
    except ValueError:
        raise ValueError('Error in tensor format {}'.format('  '.join(lst)))

    return arr


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
        return VectorInt(vector=value)

    elif isVectorFloat(value):
        return VectorFloat(vector=value)

    else:
        return value


def isInt(*xList):
    assert all(type(x_i) is str for x_i in xList)

    for x_i in xList:
        try:
            a = float(x_i)
            b = int(a)
        except (TypeError, ValueError):
            return False
        else:
            if a != b:
                return False

    return True


def isFloat(*xList):
    assert all(type(x_i) is str for x_i in xList)

    for x_i in xList:
        try:
            float(x_i)
        except (TypeError, ValueError):
            return False

    return True


def isVectorInt(vector):
    assert type(vector) is str

    return True if all(isInt(part) for part in vector.split()) else False


def isVectorFloat(vector):
    assert type(vector) is str

    return True if all(isFloat(part) for part in vector.split()) else False


def assertCount(lst=None, count=1):
    assert type(lst) is list
    assert type(count) is int

    counter = Counter(lst)
    assert all(val == count for val in counter.values()), \
        '{} must be specified {} time(s)'.format(counter.most_common(1)[0][0], count)


def assertBetween(*values, minimum=None, maximum=None, key=None):
    assert all(type(value) in [int, float] for value in values)
    assert type(minimum) in [int, float]
    assert type(maximum) in [int, float]

    if key is not None:
        assert type(key) is str

    for value in values:
        assert minimum <= value <= maximum,\
            'Value of {}{} outside range of allowed values: {} to {}'.format(value,
                                                                             ' for {}'.format(key) if key is not None else '',
                                                                             minimum,
                                                                             maximum)


def getFromDict(key=None, dct=None, strict=True, default=None):
    assert type(key) is str
    assert type(dct) is dict
    assert type(strict) is bool

    if default is not None:
        assert type(default) in [str, float, int],\
            'getFromDict default does not work for type {} yet'.format(type(default))

    key = key.strip().lower()

    value = dct.get(key, default)

    if value == default and strict:
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



class PrintColors:
    default = '\033[39m'
    black = '\033[30m'
    red = '\033[31m'
    green = '\033[32m'
    yellow = '\033[33m'
    blue = '\033[34m'
    magenta = '\033[35m'
    cyan = '\033[36m'
    gray = '\033[37m'
    orange = '\033[38;5;166m'
    pink = '\033[38;5;13m'

    lightRed = '\033[91m'
    lightGreen = '\033[92m'
    lightYellow = '\033[93m'
    lightBlue = '\033[94m'
    lightMagenta = '\033[95m'
    lightCyan = '\033[96m'

    reset = '\033[0m'
    bold = '\033[1m'
    italicized = '\033[3m'
    underline = '\033[4m'
    blink = '\033[5m'

    errored = red
    notYetCreated = orange
    created = pink
    submitted = yellow
    running = blue
    completed = green



unitToNiceUnit = { 'ev' : 'eV',
                   'ha' : 'Ha',
                   'j' : 'J',
                   'ry' : 'Ry',
                   'mhz' : 'MHz',

                   'ang' : 'Ang',
                   'bohr' : 'Bohr',

                   '1/ang' : '1/Ang'
                   }

unitToUnitType = { 'ev' : 'energy',
                   'ha' : 'energy',
                   'j' : 'energy',
                   'ry' : 'energy',
                   'mhz' : 'energy',

                   'ang' : 'length',
                   'bohr' : 'length',

                   '1/ang' : 'inverseLength'
                   }

unitTypeToUnit = { 'energy' : ['ev', 'ha', 'j', 'ry', 'mhz'],

                   'length' : ['ang', 'bohr'],

                   'inverseLength' : ['1/ang']
                   }

stringToVariableDirectories = {'halides': ['001_HF', '002_HCl', '003_HBr', '004_HI'],

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

                               'bfield': ['00T', '01T', '02T', '03T', '04T', '05T', '06T', '07T', '08T', '09T', '10T'],
                               'tensbfield': ['000T', '010T', '020T', '030T', '040T', '050T', '060T', '070T', '080T', '090T', '100T'],
                               'hundredsbfield': ['0000T', '0100T', '0200T', '0300T', '0400T', '0500T', '0600T', '0700T', '0800T', '0900T', '1000T'],
                               'kilosbfield': ['00kT', '01kT', '02kT', '03kT', '04kT', '05kT', '06kT', '07kT', '08kT', '09kT', '10kT']
                               }

stringToVariableDirectoriesAliases = {'xbfield': stringToVariableDirectories.get('bfield'),
                                      'ybfield': stringToVariableDirectories.get('bfield'),
                                      'zbfield': stringToVariableDirectories.get('bfield')
                                      }

stringToVariableDirectories = stringToVariableDirectories | stringToVariableDirectoriesAliases
