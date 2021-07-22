from calc.data import assertCount, createDirectories
from calc.settings import Setting, createSettings, createVariableSettings

from itertools import product


def createCalculations(*variableSettings, globalSettings=None, directoryNames=None, withDefaults=True):
    print('Beginning setup of calculations')

    assert type(withDefaults) is bool

    print('Generating variable settings...', end=' ', flush=True)
    varSettingsProcessed = createVariableSettings(*variableSettings)
    print('Done!')

    # Now that we have dealt with the variable cells/params of the calculations, we now work on the general cells/params.
    print('Collecting general settings...', end=' ', flush=True)
    globalSettings = createSettings(*globalSettings) if globalSettings is not None else []
    print('Done!')

    # Now let's deal with the directory names if given
    print('Creating directories...', end=' ', flush=True)
    directoryNames = createDirectories(*directoryNames) if directoryNames is not None else []
    print('Done!')

    # Some checks on the calculations and directories.
    if directoryNames:
        assert len(varSettingsProcessed) == len(directoryNames), 'Number of variable settings must match directory depth'
        assert all(len(varSettingsProcessed[num]) == len(directoryNames[num]) for num in range(len(varSettingsProcessed))), \
            'Variable settings shape must match directories shape'

        # Add numbers to the start of each directory name.
        directoryNames = [['{:03}_{}'.format(n, directoryNames[num][n-1]) for n in range(1, len(var) + 1)]
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
        print('Adding in any default settings not set...', end=' ', flush=True)

        specifiedKeys = []

        for combination in varSettingsProcessed:
            for listOfSettings in combination:
                for setting in listOfSettings:
                    specifiedKeys.append(setting.key)
            # Will already have all of the specifiedKeys by this point.
            # Don't use varSettingsProcessed[0] just incase varSettingsProcessed is empty.
            break

        specifiedKeys += [setting.key for setting in globalSettings]

        defaultSettings = createSettings('defaults')

        globalSettings += [setting for setting in defaultSettings if setting.key not in specifiedKeys]

        print('Done!')

    print('Creating calculations...', end=' ', flush=True)
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

    print('Done!')

    print('Finalising setup of calculations')
    print('Note: remember to check you\'re happy with the directory setup')

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