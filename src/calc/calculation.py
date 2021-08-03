from calc.data import assertCount, createDirectories
from calc.settings import Setting, createSettings, createVariableSettings

from collections import Counter
from itertools import product
from math import floor
from pathlib import Path


def createCalculations(*variableSettings, globalSettings=None, directoryNames=None, withDefaults=True, verbose=False):
    assert type(verbose) is bool

    if verbose: print('Beginning setup of calculations')

    assert type(withDefaults) is bool

    if verbose: print('Generating variable settings...', end=' ', flush=True)
    varSettingsProcessed = createVariableSettings(*variableSettings)
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
        assert len(varSettingsProcessed) == len(directoryNames), 'Number of variable settings must match directory depth'
        assert all(len(varSettingsProcessed[num]) == len(directoryNames[num]) for num in range(len(varSettingsProcessed))), \
            'Variable settings shape must match directories shape'

        # Add numbers to the start of each directory name.
        #directoryNames = [['{:03}_{}'.format(n, directoryNames[num][n-1]) for n in range(1, len(var) + 1)]
        directoryNames = [['{}'.format(directoryNames[num][n-1]) for n in range(1, len(var) + 1)]
                          for num, var in enumerate(varSettingsProcessed)]
    else:
        # If we don't have directory names then default to just numbers.
        directoryNames = [['{:03}'.format(n) for n in range(1, len(var) + 1)] for var in varSettingsProcessed]

    #assert sum(any(type(a) is str for a in variable) for variable in varSettingsProcessed) == 1,\
    #    'Can only have one iterable argument that is not a cell or param'

    # varSettingsProcessed looks like = [argument1, argument2, etc...]   ~ this is all the information
    # argumentI looks like = [sett1, sett2, sett3, etc...]    ~ each argument will be a directory
    # settI     looks like = [param1, param2, cell1, etc...]  ~ each setting has specific cells/params for that directory

    # Combinations will expand out the varSettingsProcessed and create every possible combination of the variable settings.
    # E.g. If we have argument1=['HF', 'HCl'] and argument2=[Cell(bField=1.0T), Cell(bField=2.0T)]
    # Then combinations will be: [(HF, bField 1.0T), (HF, bField 2.0T), (HCl, bField 1.0T), (HCl, bField 2.0T)]
    varSettingsProcessed = list(product(*varSettingsProcessed))
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



class Calculation:
    def __init__(self, name=None, directory=None, settings=None):
        if name is not None:
            assert type(name) is str

        self.name = name

        if directory is not None:
            assert type(directory) is str

        self.directory = directory

        if settings is not None:
            assert type(settings) is list
            assert all(type(setting) is Setting for setting in settings)
            assertCount([setting.key for setting in settings])

        self.settings = sorted(settings, key=lambda setting: (setting.file, setting.priority))

    def __str__(self):
        string = 'Calculation ->'

        if self.name:
            string += ' {}'.format(self.name)

        if self.directory:
            string += ' ({})'.format(self.directory)

        if not self.settings:
            string += '\n  *** empty ***'
            return string

        spaces = 20

        string += '\n'

        for setting in self.settings:
            string += '  {key:>{spaces}} : {value:<{spaces}}\n'.format(key=setting.key,
                                                                       spaces=spaces,
                                                                       value=str(setting))

        return string

    def create(self):
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

        # Work out CASTEP prefix intelligently
        positionCell = None

        for cell in cells:
            if cell.key in ['positions_frac', 'positions_abs']:
                positionCell = cell
                break

        assert positionCell is not None, \
            'Cannot find positions_frac/abs in cell, therefore cannot deduce CASTEP prefix (this will not run anyway)'

        elements = []

        for line in positionCell.lines:
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

        prefix = ''

        for element, num in elements.items():
            prefix += '{}{}'.format(element, '' if num == 1 else num)

        if len(cells) > 0:
            cellFile = '{}/{}.cell'.format(directory, prefix)

            with open(cellFile, 'w') as f:
                for cell in cells:
                    for line in cell.getLines():
                        f.write(line)

                    f.write('\n')

        if len(params) > 0:
            paramFile = '{}/{}.param'.format(directory, prefix)

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

        print('Created calculation for {} in {}'.format(prefix, directory))
