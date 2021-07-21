from calc.data import assertCount, stringToVariableDirectories
from calc.settings import Setting,\
    stringToShortcuts, stringToVariableSettings,\
    orderSettings, parseArgs

from itertools import product


def getShortcut(*strings):
    """ This function gets a specific shortcut from a string.
        A string maps to a list of cells/params and is simply
        an easy way to generate common settings in calculations. """

    settings = []

    for string in strings:
        assert type(string) is str

        newSettings = stringToShortcuts.get(string.lower(), None)

        assert newSettings is not None, 'Shortcut string {} not recognised'.format(string)

        settings += newSettings

    return settings


def getVariableSettings(string=None):
    """ This function gets a specific shortcut from a string.
        The string will map to a list that contains lists of
        cells/params, each to be used as a different setting. """

    assert type(string) is str

    variableSettings = stringToVariableSettings.get(string.lower(), None)

    assert variableSettings is not None, 'Shortcut to variable settings {} not recognised'.format(string)

    return variableSettings


def getVariableDirectories(string=None):
    """ This function gets a specific shortcut from a string.
        The string will map to a list that contains several
        directory names. """

    assert type(string) is str

    variableDirectories = stringToVariableDirectories.get(string.lower(), None)

    assert variableDirectories is not None, 'Shortcut to variable directories {} not recognised'.format(string)

    return variableDirectories


def setupCalculations(*args, globalSettings=None, directories=None):
    print('Beginning setup of calculations')

    settingsGeneral = []

    # Check if there are any general cells or params defined.
    if globalSettings is not None:
        print('Collecting general settings...', end=' ', flush=True)
        globalSettings = [globalSettings] if type(globalSettings) is str else globalSettings

        assert type(globalSettings) in [list, tuple]
        settingsGeneral, strings = parseArgs(*globalSettings)

        # Check that we have one of each string.
        assertCount([string.strip().lower() for string in strings])

        # The strings are shortcuts to one or more params/cells.
        # "Translate" from the string to these shortcuts and get them.
        # E.g. 'soc' is spin_treatment=vector and spin_orbit_coupling=true.
        settings = getShortcut(*strings)

        for setting in settings:
            if type(setting) is Setting:
                settingsGeneral.append(setting)
            else:
                raise TypeError('{} type not recognised in shortcut'.format(type(setting)))

        # Check that none of the shortcuts themselves have now duplicated any cells/params.
        assertCount([setting.key for setting in settings])
        print('Done!')

    # Now that we have dealt with the general cells/params of the calculations, we now work on the variable cells/params.
    arguments = []
    numbering = []

    # Loop through the different combinations.
    print('Generating variable settings...', end=' ', flush=True)
    for arg in args:
        assert type(arg) in [str, list],\
            'Specify only shortcut strings or lists for variable cells/params, not {}'.format(type(arg))

        # Strings are shortcuts, but shortcuts to specific combinations of cells/params.
        # E.g. 'soc' is a tuple of three different settings:
        # 1 -> spin_treatment=scalar and spin_orbit_coupling=false
        # 2 -> spin_treatment=vector and spin_orbit_coupling=false
        # 3 -> spin_treatment=vector and spin_orbit_coupling=true
        # So let's turn the shortcut string (if needed) into its list combination.
        arg = getVariableSettings(arg.strip().lower()) if type(arg) is str else arg

        # Create a list to store this combination.
        lst = []

        for strListSetting in arg:
            type_ = type(strListSetting)

            # Shortcut string.
            if type_ is str:
                variableSettings = getShortcut(strListSetting.strip().lower())
                lst.append(variableSettings)

            # User defined.
            elif type_ in [list, tuple]:
                assert all(type(setting) is Setting for setting in strListSetting), 'Settings should only be cells or params'
                lst.append(list(strListSetting))

            elif type_ is Setting:
                lst.append([strListSetting])

            else:
                raise TypeError('A specific setting of several cells/params must be given as a shortcut or tuple')

        arguments.append(lst)
        numbering.append(list(range(1, len(arg)+1)))

    # Now let's deal with the directory names if given
    if directories is not None:
        assert type(directories) is list
        assert all(type(directory) in [str, list] for directory in directories)

        for directory in directories:
            assert type(directory) in [str, list], \
                'Specify only shortcut strings or lists for directories, not {}'.format(type(directory))

        directories = [(getVariableDirectories(directory.strip().lower()) if type(directory) is str else directory)
                       for directory in directories]

        directories = [[string.strip() for string in direc] for direc in directories]

        assert len(arguments) == len(directories), 'Number of variable settings must match directory depth'
        assert all(len(arguments[num]) == len(directories[num]) for num in range(len(arguments))),\
            'Variable settings shape must match directories shape'

        directories = list(product(*directories))

    #assert sum(any(type(a) is str for a in arg) for arg in arguments) == 1,\
    #    'Can only have one iterable argument that is not a cell or param'

    # arguments looks like = [argument1, argument2, etc...]   ~ this is all the information
    # argumentI looks like = [sett1, sett2, sett3, etc...]    ~ each argument will be a directory
    # settI     looks like = [param1, param2, cell1, etc...]  ~ each setting has specific cells/params for that directory

    # Combinations will expand out the arguments and create every possible combination of the variable settings.
    # E.g. If we have argument1=['HF', 'HCl'] and argument2=[Cell(bField=1.0T), Cell(bField=2.0T)]
    # Then combinations will be: [(HF, bField 1.0T), (HF, bField 2.0T), (HCl, bField 1.0T), (HCl, bField 2.0T)]
    combinations = list(product(*arguments))
    numbering = list(product(*numbering))

    print('Done!')

    print('Creating calculations...', end=' ', flush=True)
    calculations = []

    # Loop through the possible combinations.
    for combNum, combination in enumerate(combinations):
        nums = numbering[combNum]
        name = None

        directory = '' # '{}'.format(get current working directory)

        # For the specific variable cells/params.
        settingsSpecific = []

        # Loop through the tuples of specific cells/params of this combination.
        for listNum, listOfSettings in enumerate(combination):
            n = nums[listNum]

            directory += '{:03}'.format(n)
            if directories is not None:
                directory += '_{}'.format(directories[combNum][listNum])

            # Loop through the specific tuple that contains many cells or params or both.
            for setting in listOfSettings:
                if type(setting) is Setting:
                    settingsSpecific.append(setting)
                    #directory += '_{}'.format(setting.lines)

                else:
                    raise TypeError('Only cells/params define a calculation, not {}'.format(type(setting)))

            directory += '/'

        # Combine the general cells/params we want with the variable cells/params.
        settings = settingsGeneral + settingsSpecific

        # Create the calculation.
        calculations.append(Calculation(name=name,
                                        directory=directory,
                                        settings=settings))

    print('Done!')

    print('Finalising setup of calculations')
    print('Note: remember to check you\'re happy with the directory setup')

    return calculations



class Calculation:
    def __init__(self, name=None, directory=None,
                 settings=None):
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

        self.settings = orderSettings(settings)

    def __str__(self):
        string = 'Calculation ->'

        if self.name is not None:
            string += ' {}'.format(self.name)

        if self.directory is not None:
            string += ' ({})'.format(self.directory)

        if self.settings is None:
            string += '\n  *** empty ***'
            return string

        spaces = 20

        string += '\n'

        self.settings = orderSettings(self.settings)

        for setting in self.settings:
            string += '  {key:>{spaces}} : {value:<{spaces}}\n'.format(key=setting.key,
                                                                       spaces=spaces,
                                                                       value=str(setting))

        return string