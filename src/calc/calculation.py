from calc.data import assertCount, Block
from calc.settings import Setting, stringToShortcuts, stringToVariableSettings

from itertools import product



def parseArgs(*args):
    if len(args) == 0:
        return [], [], []

    settings = []
    strings = []

    for arg in args:
        t = type(arg)

        if t is str:
            strings.append(arg)

        elif t is Setting:
            settings.append(arg)

        elif t is tuple:
            for arg2 in arg:
                t2 = type(arg2)

                if t2 is str:
                    strings.append(arg2)

                elif t2 is Setting:
                    settings.append(arg2)

                else:
                    raise TypeError('Cannot have type {} in tuple'.format(t2))

        elif t is list:
            for arg2 in arg:
                t2 = type(arg2)

                if t2 is str:
                    strings.append(arg2)

                elif t2 is Setting:
                    settings.append(arg2)

                else:
                    raise TypeError('Cannot have type {} in list'.format(t2))

        else:
            raise TypeError('Cannot have type {}'.format(t))

    return settings, strings


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
        cells/params, each to be used as a different setting """

    assert type(string) is str

    variableSettings = stringToVariableSettings.get(string.lower(), None)

    assert variableSettings is not None, 'Shortcut to variable settings {} not recognised'.format(string)

    return variableSettings


def setupCalculations(*args, generalSettings=None):
    settingsGeneral = []

    # Check if there are any general cells or params defined.
    if generalSettings is not None:
        generalSettings = [generalSettings] if type(generalSettings) is str else generalSettings

        assert type(generalSettings) in [list, tuple]
        settingsGeneral, strings = parseArgs(*generalSettings)

        # Check that we have one of each string.
        assertCount([string.lower() for string in strings])

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

    # Now that we have dealt with the general cells/params of the calculations, we now work on the variable cells/params.

    arguments = []
    numbering = []

    # Loop through the different combinations.
    for arg in args:
        assert type(arg) in [str, list],\
            'Specify only shortcut strings or lists for variable cells/params, not {}'.format(type(arg))

        # Strings are shortcuts, but shortcuts to specific combinations of cells/params.
        # E.g. 'soc' is a tuple of three different settings:
        # 1 -> spin_treatment=scalar and spin_orbit_coupling=false
        # 2 -> spin_treatment=vector and spin_orbit_coupling=false
        # 3 -> spin_treatment=vector and spin_orbit_coupling=true
        # So let's turn the shortcut string (if needed) into its list combination.
        arg = getVariableSettings(arg) if type(arg) is str else arg

        # Create a list to store this combination.
        lst = []

        for strListSetting in arg:
            type_ = type(strListSetting)

            # Shortcut string.
            if type_ is str:
                variableSettings = getShortcut(strListSetting)
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
            assert all(type(setting) == Setting for setting in settings)
            assertCount([setting.key for setting in settings])

        self.settings = settings

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

        cells = []
        params = []
        for setting in self.settings:
            if setting.file == 'cell':
                cells.append(setting)
            elif setting.file == 'param':
                params.append(setting)
            else:
                raise ValueError('File {} not recognised'.format(setting.file))

        for cell in cells:
            value = '; '.join(setting.lines) if setting.type is Block else setting.value
            string += '  {key:>{spaces}} : {value:<{spaces}}\n'.format(key=setting.key,
                                                                       spaces=spaces,
                                                                       value=value)

        return string
