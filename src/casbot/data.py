from collections import Counter
from numpy import array, empty
from pathlib import Path


# Variables for running calculations.
serialDefault = False
bashAliasesFileDefault = '/home/dean/.bash_aliases'
notificationAliasDefault = 'noti'
queueFileDefault = '/home/dean/tools/files/castep_queue.txt'


# Mathematical constants.
pi = 3.141_592_653_589_793_238_462_643_383_279_502_884_197_169
e  = 2.718_281_828_459_045_235_360_287_471_352_662_497_757_247

# Fundamental constants. CODATA 2014.
planckSI     = 6.626_070_040e-34                                              # Planck's constant SI.
hbarSI       = planckSI / (2.0 * pi)                                          # Planck's reduced constant SI.
speedLightSI = 299_792_458.0                                                  # Speed of light SI.
mu0SI        = pi * 4.0e-7                                                    # Magnetic permeability SI.
ep0SI        = 1.0 / (mu0SI * speedLightSI ** 2.0)                            # Electric permeability SI.
eChargeSI    = 1.602_176_620_8e-19                                            # Electric charge SI.
eMassSI      = 9.109_383_56e-31                                               # Electron mass SI.
pMassSI      = 1.672_621_898e-27                                              # Proton mass SI.
eGyroSI      = 1.760_859_644e+11                                              # Electron gyromagnetic ratio SI.
avogadroSI   = 6.022_140_857e+23                                              # Avogadro's constant SI.
molarGasSI   = 8.314_459_8                                                    # Molar gas constant SI.
eSpinG       = -2.002_319_304_361_82                                          # Electron spin g-factor (unitless).
fs           = eChargeSI ** 2.0 / (4.0 * pi * ep0SI * hbarSI * speedLightSI)  # Fine structure constant (unitless).
boltzmannSI  = molarGasSI / avogadroSI                                        # Boltzmann's constant SI.
amuSI        = 1.0e-3 / avogadroSI                                            # Atomic mass unit SI.


# Dervied constants.
# ! Lengths.
bohr       = 1.0
metre      = eMassSI * speedLightSI * fs / hbarSI
centimetre = metre * 1.0e-2
nanometre  = metre * 1.0e-9
angstrom   = metre * 1.0e-10
picometre  = metre * 1.0e-12

# ! Masses.
eMass = 1.0
amu   = 1.0e-3 / avogadroSI / eMassSI
kg    = 1.0 / eMassSI
gram  = kg * 1.0e-3

# ! Times.
aut         = 1.0
second      = speedLightSI ** 2.0 * fs ** 2.0 * eMassSI / hbarSI
millisecond = 1.0e-3 * second
microsecond = 1.0e-6 * second
nanosecond  = 1.0e-9 * second
picosecond  = 1.0e-12 * second
femtosecond = 1.0e-15 * second

# ! Charges.
eCharge = 1.0
coulomb  = 1.0 / eChargeSI

# ! Electric dipole moments.
debyeSI = 1.0e-21 / speedLightSI
debye   = debyeSI * coulomb * metre

# ! Spins.
eSpin = 1.0
hbar   = 2.0

# ! Magnetic dipole moments.
magnetonSI = eChargeSI * hbarSI / (2.0 * eMassSI)
magneton   = hbar / eSpinG

# ! Energies.
hartree            = 1.0
millihartree       = 1.0e-3
electronvolt      = eChargeSI / (fs ** 2.0 * eMassSI * speedLightSI ** 2.0)
millielectronvolt = electronvolt * 1.0e-3
rydberg            = 0.5
millirydberg       = rydberg * 1.0e-3
joule              = 1.0 / (fs ** 2.0 * eMassSI * speedLightSI ** 2.0)
erg                = joule * 1.0e-7
kilojoulepermole   = joule / avogadroSI * 1.0e3
kilocalpermole     = kilojoulepermole * 4.184  # 4.184 is specific heat of water.
hertz              = planckSI * joule
megahertz          = hertz * 1.0e6
gigahertz          = hertz * 1.0e9
terahertz          = hertz * 1.0e12
wavenumber         = hertz * speedLightSI * 1.0e2
kelvin             = boltzmannSI * joule

# ! Entropy.
joulebymolebykelvin   = 1.0 / molarGasSI
caloriebymolebykelvin = 4.184 * joulebymolebykelvin

# ! Forces.
hartreebybohr = 1.0
eVbyang       = electronvolt / angstrom
newton        = joule / metre
dyne          = newton * 1.0e-5

# ! Velocities.
auv            = 1.0
angperps       = angstrom / picosecond
angperfs       = angstrom / femtosecond
bohrperps      = bohr / picosecond
bohrperfs      = bohr / femtosecond
metrepersecond = metre / second

# ! Pressures.
hartreebybohr3 = 1.0
evbyang3       = electronvolt / angstrom ** 3.0
pascal         = newton / metre ** 2.0
megapascal     = pascal * 1.0e6
gigapascal     = pascal * 1.0e9
terapascal     = pascal * 1.0e12
petapascal     = pascal * 1.0e15
atmosphere     = pascal * 101325.027  # 101325.027 is conversion to atmospheres.
bar            = pascal * 1.0e5
megabar        = bar * 1.0e6

# ! Reciprocal length.
invbohr      = 1.0
invmetre     = 1.0 / metre
invnanometre = 1.0 / nanometre
invangstrom  = 1.0 / angstrom
invpicometre = 1.0 / picometre

# ! Force constants.
hartreebybohr2   = 1.0
evbyang2         = electronvolt / angstrom ** 2.0
newtonbymetre    = newton / metre
dynebycentimetre = dyne / centimetre

# ! Volumes.
bohr3       = 1.0
metre3      = metre ** 3.0
centimetre3 = (metre * 1.0e-2) ** 3.0
nanometre3  = (metre * 1.0e-9) ** 3.0
angstrom3   = (metre * 1.0e-10) ** 3.0
picometre3  = (metre * 1.0e-12) ** 3.0

# ! Magnetic resonance.
acu          = 1.0
ampere       = (fs ** 2.0 * eMassSI * speedLightSI ** 2.0 * planckSI) / eChargeSI
acd          = 1.0
amperemetre2 = ampere / metre ** 2.0
amfd         = 1.0
tesla        = eChargeSI * invmetre ** 2.0 * 2.0 * pi / planckSI
gauss        = 1.0e-4 * eChargeSI * invmetre ** 2.0 * 2.0 * pi / planckSI
agr          = 1.0
radsectesla  = eMassSI / eChargeSI
mhztesla     = 2.0 * pi * radsectesla * 1.0e-6
bohr2        = 1.0
fm2          = metre ** 2.0 * 1.0e-30
barn         = metre ** 2.0 * 1.0e-28

# ! IR intensities.
e2byamu     = 1.0 / amu
d2byamuang2 = (debye / angstrom) ** 2.0 / amu
kmbymol     = d2byamuang2 / 42.2561  # 42.2561 is strange unit favoured by spectroscopists from Gaussian03 docs.

# ! Electric field.
hartreebybohrbye = 1.0
eVbyangbye       = electronvolt / angstrom
newtonbycoulomb  = joule / metre / eChargeSI

# ! NLO Susceptibility  (1 / Efield).
bohrebyhartree = 1.0
pmbyvolt       = picometre / electronvolt


'''
unitConversions = {'ang': {'ang': 1.0, 'bohr': bohr / angstrom},
                   'bohr': {'ang': angstrom / bohr, 'bohr': 1.0},

                   'amfd': {'amfd': 1.0, 'tesla': tesla / amfd},
                   'tesla': {'amfd': amfd / tesla, 'tesla': 1.0}
                   }
'''


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
                f'Specify only shortcut strings or lists for directories, not {type(directory)}'

    directoryNames = [(getVariableDirectories(directory.strip().lower()) if type(directory) is str else directory)
                      for directory in directoryNames]

    directoryNames = [[string.strip() for string in direc] for direc in directoryNames]

    return directoryNames


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

    value = value.strip()

    if value.lower() in ['t', 'true']:
        return True

    elif value.lower() in ['f', 'false']:
        return False

    elif isInt(value):
        return int(float(value))

    elif isFloat(value):
        return float(value)

    elif isVectorInt(value):
        return array(value.split(), dtype=int)

    elif isVectorFloat(value):
        return array(value.split(), dtype=float)

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
        f'{counter.most_common(1)[0][0]} must be specified {count} time(s)'


def assertBetween(*values, minimum=None, maximum=None, key=None):
    for value in values:
        try:
            float(value)
        except ValueError:
            raise ValueError('Non-int or float type present')
    #assert all(type(value) in [int, float] for value in values)
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
        assert type(default) in [str, float, int], f'getFromDict default does not work for type {type(default)} yet'

    key = key.strip().lower()

    value = dct.get(key, default)

    if value == default and strict:
        print(value, default, dct)
        raise ValueError(f'Key {key} does not have a value')

    return value


def getUnit(key=None, unit=None, unitTypes=None, strict=True):
    assert type(key) is str
    assert type(unit) is str
    assert type(unitTypes) is dict
    assert type(strict) is bool

    unitType = getFromDict(key=key, dct=unitTypes, strict=strict)

    unit = unit.strip().lower()

    assert unit in getAllowedUnits(unitType)

    unit = getNiceUnit(unit)

    return unit


def getNiceUnit(unit=None):
    return getFromDict(key=unit, dct=unitToNiceUnit, strict=False, default=unit)


def getAllowedUnits(unitType=None, strict=True):
    return getFromDict(key=unitType, dct=unitTypeToUnit, strict=strict)


def getVariableDirectories(string=None):
    """ This function gets a specific shortcut from a string.
        The string will map to a list that contains several
        directory names. """

    assert type(string) is str

    variableDirectories = stringToVariableDirectories.get(string.strip().lower(), None)

    assert variableDirectories is not None, f'Shortcut to variable directories {string} not recognised'

    return variableDirectories


def getFileLines(file_=None):
    assert type(file_) is str

    assert Path(file_).is_file(), f'Cannot find file {file_}'

    with open(file_) as f:
        lines = f.read().splitlines()

    return lines


def unitConvert(value=None, fromUnit=None, toUnit=None):
    assert type(value) in (int, float)
    assert type(fromUnit) is str
    assert type(toUnit) is str

    fromUnit = fromUnit.strip().lower()
    toUnit = toUnit.strip().lower()

    '''
    conversions = unitConversions.get(fromUnit, None)

    if conversions is None:
        raise ValueError(f'Do not know unit {fromUnit} to convert from')

    conversion = conversions.get(toUnit, None)

    if conversion is None:
        raise ValueError(f'Do not know unit {toUnit} to convert to')
    '''

    try:
        fromUnit = eval(fromUnit)
    except NameError:
        raise NameError(f'Do not know unit {fromUnit} to convert from')

    try:
        toUnit = eval(toUnit)
    except NameError:
        raise NameError(f'Do not know unit {toUnit} to convert to')

    conversion = toUnit / fromUnit

    return value / conversion


# Dummy class to return True for any equals call.
class Any:
    def __init__(self, type_=None):
        self.type_ = type_

    def __eq__(self, other):
        if self.type_ is None:
            return True

        if type(other) is not self.type_:
            return False

        return True


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
    lightOrange = '\033[38;5;202m'

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

                   'ev/ang' : 'eV/Ang',

                   'ang' : 'Ang',
                   'bohr' : 'Bohr',

                   '1/ang' : '1/Ang',

                   'tesla' : 'Tesla',
                   'gauss' : 'Gauss',

                   'radsectesla' : 'RadSecTesla',

                   'hbar/2' : 'hbar/2'
                   }

unitToUnitType = { 'ev' : 'energy',
                   'ha' : 'energy',
                   'j' : 'energy',
                   'ry' : 'energy',
                   'mhz' : 'energy',

                   'ev/ang': 'force',

                   'ang' : 'length',
                   'bohr' : 'length',

                   '1/ang' : 'inverselength',

                   'tesla' : 'bfield',
                   'gauss' : 'bfield',

                   'radsectesla' : 'gyromagnetic',

                   'hbar/2' : 'spin'
                   }

unitTypeToUnit = { 'energy' : ['ev', 'ha', 'j', 'ry', 'mhz'],

                   'force' : ['ev/ang'],

                   'length' : ['ang', 'bohr'],

                   'inverselength' : ['1/ang'],

                   'bfield' : ['tesla', 'gauss'],

                   'gyromagnetic' : ['radsectesla'],

                   'spin' : ['hbar/2']
                   }



stringToVariableDirectories = {'halides': ['001_HF', '002_HCl', '003_HBr', '004_HI'],

                               'chalcogenides': ['001_H2O', '002_H2S', '003_H2Se', '004_H2Te'],

                               'methylhalides': ['001_CH3F', '002_CH3Cl', '003_CH3Br', '004_CH3I'],

                               'alkalihydrides': ['001_LiH', '002_NaH', '003_KH', '004_RbH'],

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

                               'vectordensity': ['000_orig',
                                                 '001_scalar_soc_false',
                                                 '002_spinor_soc_false_x',
                                                 '002_spinor_soc_false_y',
                                                 '002_spinor_soc_false_z',
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

                               'bfieldlinearity': ['00000T/density_in_x', '00000T/density_in_y', '00000T/density_in_z',
                                                   '00001T/density_in_x', '00001T/density_in_y', '00001T/density_in_z',
                                                   '00002T/density_in_x', '00002T/density_in_y', '00002T/density_in_z',
                                                   '00003T/density_in_x', '00003T/density_in_y', '00003T/density_in_z',
                                                   '00004T/density_in_x', '00004T/density_in_y', '00004T/density_in_z',
                                                   '00005T/density_in_x', '00005T/density_in_y', '00005T/density_in_z',
                                                   '00006T/density_in_x', '00006T/density_in_y', '00006T/density_in_z',
                                                   '00007T/density_in_x', '00007T/density_in_y', '00007T/density_in_z',
                                                   '00008T/density_in_x', '00008T/density_in_y', '00008T/density_in_z',
                                                   '00009T/density_in_x', '00009T/density_in_y', '00009T/density_in_z',
                                                   '00010T/density_in_x', '00010T/density_in_y', '00010T/density_in_z',
                                                   '00020T/density_in_x', '00020T/density_in_y', '00020T/density_in_z',
                                                   '00030T/density_in_x', '00030T/density_in_y', '00030T/density_in_z',
                                                   '00040T/density_in_x', '00040T/density_in_y', '00040T/density_in_z',
                                                   '00050T/density_in_x', '00050T/density_in_y', '00050T/density_in_z',
                                                   '00060T/density_in_x', '00060T/density_in_y', '00060T/density_in_z',
                                                   '00070T/density_in_x', '00070T/density_in_y', '00070T/density_in_z',
                                                   '00080T/density_in_x', '00080T/density_in_y', '00080T/density_in_z',
                                                   '00090T/density_in_x', '00090T/density_in_y', '00090T/density_in_z',
                                                   '00100T/density_in_x', '00100T/density_in_y', '00100T/density_in_z',
                                                   '00200T/density_in_x', '00200T/density_in_y', '00200T/density_in_z',
                                                   '00300T/density_in_x', '00300T/density_in_y', '00300T/density_in_z',
                                                   '00400T/density_in_x', '00400T/density_in_y', '00400T/density_in_z',
                                                   '00500T/density_in_x', '00500T/density_in_y', '00500T/density_in_z',
                                                   '00600T/density_in_x', '00600T/density_in_y', '00600T/density_in_z',
                                                   '00700T/density_in_x', '00700T/density_in_y', '00700T/density_in_z',
                                                   '00800T/density_in_x', '00800T/density_in_y', '00800T/density_in_z',
                                                   '00900T/density_in_x', '00900T/density_in_y', '00900T/density_in_z',
                                                   '01000T/density_in_x', '01000T/density_in_y', '01000T/density_in_z',
                                                   '02000T/density_in_x', '02000T/density_in_y', '02000T/density_in_z',
                                                   '03000T/density_in_x', '03000T/density_in_y', '03000T/density_in_z',
                                                   '04000T/density_in_x', '04000T/density_in_y', '04000T/density_in_z',
                                                   '05000T/density_in_x', '05000T/density_in_y', '05000T/density_in_z',
                                                   '06000T/density_in_x', '06000T/density_in_y', '06000T/density_in_z',
                                                   '07000T/density_in_x', '07000T/density_in_y', '07000T/density_in_z',
                                                   '08000T/density_in_x', '08000T/density_in_y', '08000T/density_in_z',
                                                   '09000T/density_in_x', '09000T/density_in_y', '09000T/density_in_z',
                                                   '10000T/density_in_x', '10000T/density_in_y', '10000T/density_in_z'],

                               'bfield': ['00T', '01T', '02T', '03T', '04T', '05T', '06T', '07T', '08T', '09T', '10T'],
                               'tensbfield': ['000T', '010T', '020T', '030T', '040T', '050T', '060T', '070T', '080T', '090T', '100T'],
                               'hundredsbfield': ['0000T', '0100T', '0200T', '0300T', '0400T', '0500T', '0600T', '0700T', '0800T', '0900T', '1000T'],
                               'kilosbfield': ['00kT', '01kT', '02kT', '03kT', '04kT', '05kT', '06kT', '07kT', '08kT', '09kT', '10kT']
                               }

stringToVariableDirectoriesAliases = {'xbfield': stringToVariableDirectories.get('bfield'),
                                      'ybfield': stringToVariableDirectories.get('bfield'),
                                      'zbfield': stringToVariableDirectories.get('bfield'),

                                      'hydrogenhalides': stringToVariableDirectories.get('halides')
                                      }

stringToVariableDirectories = stringToVariableDirectories | stringToVariableDirectoriesAliases
