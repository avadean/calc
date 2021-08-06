from casbot.data import assertCount, createDirectories,\
    serialDefault, bashAliasesFileDefault, notificationAliasDefault, queueFileDefault
from casbot.settings import Setting, createSettings, createVariableSettings, readSettings

from collections import Counter
from datetime import datetime
from fnmatch import filter
from itertools import product
from math import floor
from os import chdir, getcwd, listdir
from pathlib import Path
from subprocess import run as subProcessRun


def createCalculations(variableSettings=None, globalSettings=None, directoryNames=None, withDefaults=True, verbose=False):
    assert type(verbose) is bool
    assert type(withDefaults) is bool

    if verbose: print('Beginning setup of calculations')

    if verbose: print('Generating variable settings...', end=' ', flush=True)
    variableSettings = createVariableSettings(*variableSettings) if variableSettings is not None else []
    if verbose: print('Done!')

    # Now that we have dealt with the variable cells/params of the calculations, we now work on the general cells/params.
    if verbose: print('Collecting general settings...', end=' ', flush=True)
    globalSettings = createSettings(*globalSettings) if globalSettings is not None else []
    if verbose: print('Done!')

    # Now let's deal with the directory names if given
    if verbose: print('Creating directories...', end=' ', flush=True)
    directoryNames = createDirectories(*directoryNames) if directoryNames is not None else []
    if verbose: print('Done!')

    # Some checks on the calculations and directories.
    if directoryNames:
        assert len(variableSettings) == len(directoryNames), 'Number of variable settings must match directory depth'
        assert all(len(variableSettings[num]) == len(directoryNames[num]) for num in range(len(variableSettings))), \
            'Variable settings shape must match directories shape'

        # Add numbers to the start of each directory name.
        #directoryNames = [['{:03}_{}'.format(n, directoryNames[num][n-1]) for n in range(1, len(var) + 1)]
        directoryNames = [['{}'.format(directoryNames[num][n-1]) for n in range(1, len(var) + 1)]
                          for num, var in enumerate(variableSettings)]
    else:
        # If we don't have directory names then default to just numbers.
        directoryNames = [['{:03}'.format(n) for n in range(1, len(var) + 1)] for var in variableSettings]

    #assert sum(any(type(a) is str for a in variable) for variable in varSettingsProcessed) == 1,\
    #    'Can only have one iterable argument that is not a cell or param'

    # varSettingsProcessed looks like = [argument1, argument2, etc...]   ~ this is all the information
    # argumentI looks like = [sett1, sett2, sett3, etc...]    ~ each argument will be a directory
    # settI     looks like = [param1, param2, cell1, etc...]  ~ each setting has specific cells/params for that directory

    # Combinations will expand out the varSettingsProcessed and create every possible combination of the variable settings.
    # E.g. If we have argument1=['HF', 'HCl'] and argument2=[Cell(bField=1.0T), Cell(bField=2.0T)]
    # Then combinations will be: [(HF, bField 1.0T), (HF, bField 2.0T), (HCl, bField 1.0T), (HCl, bField 2.0T)]
    varSettingsProcessed = list(product(*variableSettings))
    directoryNames = list(product(*directoryNames))

    if withDefaults:
        if verbose: print('Adding in any default settings not set...', end=' ', flush=True)

        specifiedKeys = []

        for combination in varSettingsProcessed:
            for listOfSettings in combination:
                for setting in listOfSettings:
                    if setting.key not in specifiedKeys:
                        specifiedKeys.append(setting.key)
            ## Will already have all of the specifiedKeys by this point.
            ## Don't use varSettingsProcessed[0] just incase varSettingsProcessed is empty.
            #break

        specifiedKeys += [setting.key for setting in globalSettings]

        defaultSettings = createSettings('defaults')

        globalSettings += [setting for setting in defaultSettings if setting.key not in specifiedKeys]

        if verbose: print('Done!')

    if verbose: print('Creating calculations...', end=' ', flush=True)
    calculations = []

    # Loop through the possible combinations.
    for combNum, combination in enumerate(varSettingsProcessed):
        name = None

        directory = '' # '{}'.format(get current working directory)

        # For the specific variable cells/params.
        specificSettings = []

        # Loop through the tuples of specific cells/params of this combination.
        for listNum, listOfSettings in enumerate(combination):
            directory += directoryNames[combNum][listNum]

            # Loop through the specific tuple that contains many cells or params or both.
            for setting in listOfSettings:
                if type(setting) is Setting:
                    specificSettings.append(setting)

                else:
                    raise TypeError('Only cells/params define a calculation, not {}'.format(type(setting)))

            directory += '/'

        # Combine the general cells/params we want with the variable cells/params.
        settings = globalSettings + specificSettings

        # Create the calculation.
        calculations.append(Calculation(name=name,
                                        directory=directory,
                                        settings=settings))

    if verbose: print('Done!')

    if verbose: print('Finalising setup of calculations')

    return calculations



def processCalculations(*directories):
    directories = createDirectories(*directories)

    if len(directories) == 0:
        return []

    directories = list(product(*directories))

    directories = ['/'.join(directory) + '/' for directory in directories]

    calculations = []

    for directory in directories:
        assert Path(directory).is_dir(), 'Cannot find directory {}'.format(directory)

        prefix = None
        cellPrefix = None
        paramPrefix = None

        # Get settings from cell file.
        cellFiles = filter(listdir(directory), '*.cell')
        cells = []

        if len(cellFiles) == 1:
            cellPrefix = cellFiles[0][:-5] # Removes '.cell'
            cells = readSettings(file_='{}{}'.format(directory, cellFiles[0]))

        elif len(cellFiles) > 1:
            raise NameError('Too many cell files to read in directory {}'.format(directory))

        else:
            print('*** Caution: no cell file found in {}'.format(directory))

        # Now do param file.
        paramFiles = filter(listdir(directory), '*.param')
        params = []

        if len(paramFiles) == 1:
            paramPrefix = paramFiles[0][:-6]  # Removes '.param'

            params = readSettings(file_='{}{}'.format(directory, paramFiles[0]))
        elif len(paramFiles) > 1:
            raise NameError('Too many param files to read in directory {}'.format(directory))
        else:
            print('*** Caution: no param file found in {}'.format(directory))

        # Check cell and param prefixes are the same.
        if cellPrefix is not None and paramPrefix is not None:
            assert paramPrefix == cellPrefix, \
                'Different prefixes for cell and param files: {}.cell, {}.param'.format(cellPrefix, paramPrefix)

        elif cellPrefix is not None:
            prefix = cellPrefix

        elif paramPrefix is not None:
            prefix = paramPrefix

        # Group cell and param settings together.
        settings = cells + params

        # Create new calculation.
        newCalculation = Calculation(name=prefix,
                                     directory=directory,
                                     settings=settings)

        # And add it to the list!
        calculations.append(newCalculation)

    return calculations



class Calculation:
    def __init__(self, directory=None, settings=None, name=None):
        if directory is not None:
            assert type(directory) is str

        if settings is not None:
            assert type(settings) is list
            assert all(type(setting) is Setting for setting in settings)
            assertCount([setting.key for setting in settings])

        if name is not None:
            assert type(name) is str
            assert ' ' not in name, 'Cannot have spaces in name'

        self.directory = directory

        self.settings = settings
        self.sortSettings()

        self.name = name
        self.setName(strict=False)

    def __str__(self):
        string = 'Calculation ->'

        if self.name is not None:
            string += ' {}'.format(self.name)

        if self.directory is not None:
            string += ' ({})'.format(self.directory)

        if self.settings is None:
            string += '\n  *** empty ***'
            return string

        spaces = 25

        string += '\n'

        for setting in self.settings:
            string += '  {key:>{spaces}} : {value:<{spaces}}\n'.format(key=setting.key,
                                                                       spaces=spaces,
                                                                       value=str(setting))

        return string

    def check(self):
        string = 'Calculation ->'

        if self.name is not None:
            string += ' {}'.format(self.name)

        if self.directory is None:
            string += ' (no directory specified)'
            return
        else:
            string += ' ({})'.format(self.directory)

        if Path(self.directory).is_dir():
            subFile = '{}{}.sub'.format(self.directory, self.name)
            castepFile = '{}{}.castep'.format(self.directory, self.name)

            if Path(castepFile).is_file():
                with open(castepFile) as f:
                    castepLines = f.read().splitlines()

                calculationFinished = False
                for line in castepLines:
                    if line.startswith('Total time'):
                        calculationFinished = True
                        break

                string += ' *** finished ***' if calculationFinished else ' *** started ***'

            elif Path(subFile).is_file():
                string += ' *** submitted ***'

        else:
            string += '*** WARNING: directory specified as {} but not found'.format(self.directory)

        print(string)

    def create(self):
        if self.directory is None:
            raise ValueError('Cannot create calculation when there is no directory specified')

        directory = Path(self.directory)

        try:
            directory.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            raise FileExistsError('Directory {} exists but is a file'.format(directory))

        cells = [setting for setting in self.settings if setting.file == 'cell']
        params = [setting for setting in self.settings if setting.file == 'param']

        cells = sorted(cells, key=lambda cell: cell.priority)
        params = sorted(params, key=lambda param: param.priority)

        assert len(cells) + len(params) == len(self.settings), \
            'Setting in calculation cannot be categorised as a cell or param'

        # Work out CASTEP prefix intelligently if calculation does not have a name
        self.setName(strict=True)

        if len(cells) > 0:
            cellFile = '{}/{}.cell'.format(directory, self.name)

            with open(cellFile, 'w') as f:
                for cell in cells:
                    for line in cell.getLines():
                        f.write(line)

                    f.write('\n')

        if len(params) > 0:
            paramFile = '{}/{}.param'.format(directory, self.name)

            longestParam = max([len(param.key) for param in params])

            currentPriorityLevel = floor(params[0].priority)

            with open(paramFile, 'w') as f:
                for param in params:

                    # If we're at a new priority level then add a line
                    if currentPriorityLevel != floor(param.priority):
                        f.write('\n')
                        currentPriorityLevel = floor(param.priority)

                    for line in param.getLines(longestParam):
                        f.write(line)

        print('Created calculation for {} in {}'.format(self.name, directory))

    def run(self, test=False, serial=None, bashAliasesFile=None, notificationAlias=None):
        if self.directory is None:
            raise ValueError('Cannot run calculation when there is no directory specified')

        assert type(test) is bool

        if serial is None:
            serial = serialDefault
        else:
            assert type(serial) is bool

        if bashAliasesFile is None:
            bashAliasesFile = bashAliasesFileDefault
        else:
            assert type(bashAliasesFile) is str

            if not Path(bashAliasesFile).is_file():
                raise FileNotFoundError('Cannot find alias file {}'.format(bashAliasesFile))

        if notificationAlias is None:
            notificationAlias = notificationAliasDefault
        else:
            assert type(notificationAlias) is str

        # Work out CASTEP prefix intelligently if calculation does not have a name
        self.setName(strict=True)

        directory = Path(self.directory)

        if not directory.is_dir():
            raise NotADirectoryError('Cannot find directory {} to run calculation'.format(self.directory))

        origDir = getcwd()

        chdir(self.directory)

        castep = 'castep.serial {}'.format(self.name) if serial else 'castep.mpi {}'.format(self.name)

        command = 'bash -c \'. {} ; {} {} &\''.format(bashAliasesFile, notificationAlias, castep)

        if test:
            print('|-> {} <-| will be run in {}'.format(command, getcwd()))
        else:
            result = subProcessRun(command, check=True, shell=True, text=True)

        chdir(origDir)

    def sub(self, test=False, force=False, queueFile=None):
        if self.directory is None:
            raise ValueError('Cannot submit calculation when there is no directory specified')

        assert type(test) is bool
        assert type(force) is bool

        if queueFile is None:
            queueFile = queueFileDefault
        else:
            assert type(queueFile) is str

        if not Path(queueFile).is_file():
            raise FileNotFoundError('Cannot find queue file {}'.format(queueFile))

        # Work out CASTEP prefix intelligently if calculation does not have a name
        self.setName(strict=True)

        directory = Path(self.directory)

        if not directory.is_dir():
            raise NotADirectoryError('Cannot find directory {} to run calculation'.format(self.directory))

        subFile = '{}{}.sub'.format(self.directory, self.name)

        if test:
            print('|-> {} calculation queued at {} <-| will be appended to {}'.format(self.name,
                                                                                      datetime.now(),
                                                                                      subFile))

            print('|-> {}  {} <-| will be appended to {}'.format(self.name,
                                                                 directory.resolve(),
                                                                 queueFile))

            if Path(subFile).is_file():
                print('*** CAUTION: sub file {} found - calculation may already be submitted ***'.format(subFile))

            print('')

        else:
            if Path(subFile).is_file() and not force:
                raise FileExistsError('Calculation may already be submitted {} - use force=True to ignore'.format(subFile))

            with open(subFile, 'a') as f:
                f.write('{} calculation queued at {}.\n'.format(self.name, datetime.now()))

            with open(queueFile, 'a') as f:
                f.write('{}  {}\n'.format(self.name, directory.resolve()))

    def setName(self, strict=False):
        assert type(strict) is bool

        if self.name is not None:
            return

        positionSetting = None

        for setting in self.settings:
            if setting.key in ['positions_frac', 'positions_abs']:
                positionSetting = setting
                break

        if strict and positionSetting is None:
            raise ValueError('Cannot find positions_frac/abs in cell, therefore cannot deduce CASTEP prefix (this will not run anyway)')

        elements = []

        for line in positionSetting.lines:
            try:
                element = line.split(' ')[0]
            except IndexError:
                raise ValueError('Cannot find element in atomic positions line {}'.format(line))

            element = element.strip()

            element = element[0].upper() + element[1:].lower()

            # Manually get rid of lines that are just units.
            if element not in ['Ang', 'Bohr']:
                elements.append(element)

        elements = Counter(elements)

        self.name = ''

        for element, num in elements.items():
            self.name += '{}{}'.format(element, '' if num == 1 else num)

    def sortSettings(self):
        self.settings = sorted(self.settings, key=lambda setting: (setting.file, setting.priority))

    def updateSettings(self, *settings):
        settings = createSettings(*settings)

        for setting in settings:
            self.settings = [otherSetting for otherSetting in self.settings if otherSetting.key != setting.key]

            self.settings.append(setting)

            self.sortSettings()
