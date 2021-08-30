from casbot.data import assertCount, createDirectories,\
    serialDefault, bashAliasesFileDefault, notificationAliasDefault, queueFileDefault,\
    PrintColors
from casbot.settings import Setting, Keyword, Block, createSettings, createVariableSettings, readSettings
from casbot.results import getResult

from datetime import datetime
from dateutil import parser
from fnmatch import filter
from itertools import product
from math import floor, pi, sin, cos, sqrt
from numpy import array, asarray, dot
from os import chdir, getcwd, listdir
from pathlib import Path
#from re import search
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
        directoryNames = [[f'{directoryNames[num][n-1]}' for n in range(1, len(var) + 1)]
                          for num, var in enumerate(variableSettings)]
    else:
        # If we don't have directory names then default to just numbers.
        directoryNames = [[f'{n:03}' for n in range(1, len(var) + 1)] for var in variableSettings]

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
                if isinstance(setting, Setting):
                    specificSettings.append(setting)

                else:
                    raise TypeError(f'Only cells/params define a calculation, not {type(setting)}')

            directory += '/'

        # Combine the general cells/params we want with the variable cells/params.
        settings = globalSettings + specificSettings

        # Calculation should have their own copy of settings.
        settings = settings.copy()

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
        assert Path(directory).is_dir(), f'Cannot find directory {directory}'

        prefix = None
        cellPrefix = None
        paramPrefix = None

        # Get settings from cell file.
        cellFiles = filter(listdir(directory), '*.cell')
        cells = []

        if len(cellFiles) == 1:
            cellPrefix = cellFiles[0][:-5] # Removes '.cell'
            cells = readSettings(file_=f'{directory}{cellFiles[0]}')

        elif len(cellFiles) > 1:
            raise NameError(f'Too many cell files to read in directory {directory}')

        else:
            print(f'*** Caution: no cell file found in {directory}')

        # Now do param file.
        paramFiles = filter(listdir(directory), '*.param')
        params = []

        if len(paramFiles) == 1:
            paramPrefix = paramFiles[0][:-6]  # Removes '.param'
            params = readSettings(file_=f'{directory}{paramFiles[0]}')

        elif len(paramFiles) > 1:
            raise NameError(f'Too many param files to read in directory {directory}')

        else:
            print(f'*** Caution: no param file found in {directory}')

        # Check cell and param prefixes are the same.
        if cellPrefix is not None and paramPrefix is not None:
            assert paramPrefix == cellPrefix, \
                f'Different prefixes for cell and param files: {cellPrefix}.cell, {paramPrefix}.param'
            prefix = cellPrefix

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
    hyperfineDipolarBareTensors = []
    hyperfineDipolarAugTensors = []
    hyperfineDipolarAug2Tensors = []
    hyperfineDipolarTensors = []
    hyperfineFermiTensors = []
    hyperfineTotalTensors = []

    def __init__(self, directory=None, settings=None, name=None):
        if directory is not None:
            assert type(directory) is str

        if settings is not None:
            assert type(settings) is list
            assert all(isinstance(setting, Setting) for setting in settings)
            assertCount([setting.key for setting in settings])

        if name is not None:
            assert type(name) is str
            assert ' ' not in name, 'Cannot have spaces in name'

        self.directory = directory

        self.settings = settings
        self.sortSettings()

        self.name = name
        self.setName(strict=False)

        self.expectedSecToFinish = None

    def __str__(self):
        string = 'Calculation ->'

        if self.name is not None:
            string += f' {self.name}'

        if self.directory is not None:
            string += f' ({self.directory})'

        if self.settings is None:
            string += '\n  *** empty ***'
            return string

        spaces = 25

        string += '\n'

        for setting in self.settings:
            string += f'  {setting.key:>{spaces}} : {str(setting):<{spaces}}\n'

        return string

    def analyse(self, type_=None):
        assert self.getStatus() == 'completed', 'Calculation not completed therefore cannot analyse'

        assert type(type_) is str

        type_ = type_.strip().lower()

        self.setName(strict=True)

        # TODO: allow for looking in different files (e.g .magres) not just .castep
        castepFile = f'{self.directory}{self.name}.castep'

        assert Path(castepFile).is_file(), f'Cannot find castep file {castepFile}'

        with open(castepFile) as f:
            castepLines = f.read().splitlines()

        if type_ == 'hyperfine':
            self.hyperfineDipolarBareTensors = getResult(resultToGet='hyperfine_dipolarbare', lines=castepLines)
            self.hyperfineDipolarAugTensors = getResult(resultToGet='hyperfine_dipolaraug', lines=castepLines)
            self.hyperfineDipolarAug2Tensors = getResult(resultToGet='hyperfine_dipolaraug2', lines=castepLines)
            self.hyperfineDipolarTensors = getResult(resultToGet='hyperfine_dipolar', lines=castepLines)
            self.hyperfineFermiTensors = getResult(resultToGet='hyperfine_fermi', lines=castepLines)
            self.hyperfineTotalTensors = getResult(resultToGet='hyperfine_total', lines=castepLines)

        else:
            raise ValueError(f'Do not know how to put result {type_} into calculation (yet)')

    def check(self, nameOutputLen=0, dirOutputLen=0, latestFinishTime=0.0):
        assert type(nameOutputLen) is int
        assert type(dirOutputLen) is int
        assert type(latestFinishTime) in [int, float]

        latestFinishTime = float(latestFinishTime)

        self.setName(strict=False)

        string = ' ->'

        if self.name is not None:
            nameOutputLen = max(len(self.name), nameOutputLen)
            string += f'  {self.name:<{nameOutputLen}}'

        if self.directory is None:
            string += '  (no directory specified)'
            return
        else:
            dirOutputLen = max(len(self.directory), dirOutputLen)
            directory = f'({self.directory})'
            string += f'  {directory:<{dirOutputLen+2}}'  # +2 for brackets, ()

        status = self.getStatus()

        statusColor = {  # 'no directory specified': PrintColors.black,
            'errored': PrintColors.errored,
            'completed': PrintColors.completed,
            'running': PrintColors.running,
            'submitted': PrintColors.submitted,
            'created': PrintColors.created,
            'not yet created': PrintColors.notYetCreated}.get(status, None)

        assert statusColor is not None, f'Status {status} not recognised'

        if status in ['running', 'submitted'] and self.expectedSecToFinish is not None:
            finishDateTimeInSec = datetime.now().timestamp() + self.expectedSecToFinish
            finishDateTime = datetime.fromtimestamp(finishDateTimeInSec)
            finishDateTime = finishDateTime.strftime('%Y-%m-%d %H:%M:%S')

            timeColor = ''

            if latestFinishTime:
                perCent = int(100.0 * self.expectedSecToFinish / latestFinishTime)

                #if 0 <= perCent < 10:
                #    timeColor = PrintColors.lightCyan
                #elif 10 <= perCent < 20:
                #    timeColor = PrintColors.cyan
                #elif 20 <= perCent < 30:
                #    timeColor = PrintColors.lightBlue
                #elif 30 <= perCent < 40:
                #    timeColor = PrintColors.blue
                #elif 40 <= perCent < 50:
                #    timeColor = PrintColors.lightGreen
                #elif 50 <= perCent < 60:
                #    timeColor = PrintColors.green
                #elif 60 <= perCent < 70:
                #    timeColor = PrintColors.lightYellow
                #elif 70 <= perCent < 80:
                #    timeColor = PrintColors.yellow
                #elif 80 <= perCent < 90:
                #    timeColor = PrintColors.orange
                #elif 90 <= perCent < 100:
                #    timeColor = PrintColors.lightRed
                #elif perCent == 100:
                #    timeColor = PrintColors.red

                #timeColor = f'\033[38;5;{int(perCent * 255 / 100.0)}m'

                if 0 <= perCent < 25:
                    timeColor = PrintColors.lightCyan
                elif 25 <= perCent < 50:
                    timeColor = PrintColors.lightGreen
                elif 50 <= perCent < 75:
                    timeColor = PrintColors.lightYellow
                elif 75 <= perCent < 100:
                    timeColor = PrintColors.lightOrange
                elif perCent == 100:
                    timeColor = PrintColors.underline + PrintColors.lightRed

            extraMessage = f'  expected finish time {timeColor}{finishDateTime}{PrintColors.reset}'
        else:
            extraMessage = ''

        string += f'  *** {statusColor}{status:^15}{PrintColors.reset} ***{extraMessage}'

        print(string)

    def create(self, force=False, passive=False):
        assert type(force) is bool
        assert type(passive) is bool

        if force and passive:
            raise ValueError('Cannot create calculation with force=True and passive=True - use one option as True only')

        if self.directory is None:
            raise ValueError('Cannot create calculation when there is no directory specified')

        directory = Path(self.directory)

        if directory.exists():
            if passive:
                print(f'Skipping creation of calculation for {self.name} in {directory}')
                return

            elif not force:
                raise FileExistsError('Directory for calculation already exists - use force=True to overwrite or passive=True to ignore')

        try:
            directory.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            raise FileExistsError(f'Directory {directory} exists but is a file')

        cells = [setting for setting in self.settings if setting.file == 'cell']
        params = [setting for setting in self.settings if setting.file == 'param']

        cells = sorted(cells, key=lambda c: c.priority)
        params = sorted(params, key=lambda p: p.priority)

        assert len(cells) + len(params) == len(self.settings), \
            'Setting in calculation cannot be categorised as a cell or param'

        # Work out CASTEP prefix intelligently if calculation does not have a name
        self.setName(strict=True)

        if len(cells) > 0:
            cellFile = f'{directory}/{self.name}.cell'

            with open(cellFile, 'w') as f:
                for cell in cells:

                    for line in self.getSettingLines(setting=cell, maxSettingLength=0):
                        f.write(f'{line}\n')

                    f.write('\n')

        if len(params) > 0:
            paramFile = f'{directory}/{self.name}.param'

            longestParam = max([len(param.key) for param in params])

            currentPriorityLevel = floor(params[0].priority)

            with open(paramFile, 'w') as f:
                for param in params:

                    # If we're at a new priority level then add a line
                    if currentPriorityLevel != floor(param.priority):
                        f.write('\n')
                        currentPriorityLevel = floor(param.priority)

                    for line in self.getSettingLines(setting=param, maxSettingLength=longestParam):
                        f.write(f'{line}\n')

        print(f'Created calculation for {self.name} in {directory}')

    def getCompletedTime(self):
        """ This function will work out (in seconds) how long it will take this calculation to complete """

        assert self.getStatus() == 'completed', 'Calculation not complete so cannot get completed time'

        castepFile = f'{self.directory}{self.name}.castep'

        assert Path(castepFile).is_file(), 'Cannot find castep file to get completed time'

        with open(castepFile) as f:
            castepLines = f.read().splitlines()

        castepLines.reverse()

        for line in castepLines:
            line = line.strip().lower()

            if line.startswith('total time'):
                index = line.index('=')

                assert index != -1, f'Error in total time in castep file {castepFile}'

                line = line[index+1:].strip()

                line = line[:-1].strip()

                try:
                    return float(line)
                except ValueError:
                    raise ValueError(f'Error in total time in castep file {castepFile}')
        else:
            raise ValueError(f'Cannot find total time in castep file {castepFile}')

    def getRunningTime(self):
        """ This function will work out how long (in seconds) this calculation has been running for """

        assert self.getStatus() == 'running', 'Calculation not running so cannot get running time'

        return datetime.now().timestamp() - self.getStartTime()

    def getStartTime(self):
        """ This function will work out when the calculation started as a timestamp """

        #assert self.getStatus() in ['completed', 'running'], 'Calculation not completed or running so cannot get start time'

        castepFile = f'{self.directory}{self.name}.castep'

        if not Path(castepFile).is_file():
            return None
        #assert Path(castepFile).is_file(), 'Cannot find castep file to get running time'

        with open(castepFile) as f:
            castepLines = f.read().splitlines()

        castepLines.reverse()  # If multiple 'run started:' lines then the most recent will be last

        for line in castepLines:
            line = line.strip()

            if line.lower().startswith('run started:'):
                line = line[12:].strip()  # len('Run started:') = 12

                try:
                    return datetime.strptime(line, '%a, %d %b %Y %H:%M:%S %z').timestamp()
                except ValueError:
                    pass
        else:
            raise ValueError(f'Cannot find start time in castep file {castepFile}')

    def getSubTime(self):
        """ This function will find the sub time as a timestamp """

        #assert self.getStatus() in ['completed', 'running', 'submitted'],\
        #    'Calculation not completed, running or submitted so cannot get submitted time'

        subFile = f'{self.directory}{self.name}.sub'

        if not Path(subFile).is_file():
            return None

        #assert Path(subFile).is_file(), 'Cannot find sub file to get submitted time'

        with open(subFile) as f:
            subLines = f.read().splitlines()

        subLines.reverse()  # Most recent submit will be last if there are multiple

        for line in subLines:
            line = line.strip()

            # Names with numbers in seem to break the date-time parser (TODO: consider using a different parser for date-time is this one is rubbish)
            if self.name is None:
                return None
            elif line.startswith(self.name):
                line = line[len(self.name):].strip()

            line = line[:-1].strip() if line.endswith('.') else line  # Get rid of annoying full stop which will cause chaos

            '''
            subTime = search(r'\d{4}[/-]\d{2}[/-]\d{2} \d{2}:\d{2}:\d{2}.\d{6}', line)

            if subTime is not None:
                subTime = subTime.group()

                subTime.replace('/', '-')

                return datetime.strptime(subTime, '%Y-%m-%d %H:%M:%S.%f').timestamp()
            '''

            try:
                return parser.parse(line, fuzzy=True).timestamp()
            except parser.ParserError:
                pass

        else:
            raise ValueError(f'Cannot find submitted time in sub file {subFile}')

    def getStatus(self):
        if self.directory is None:
            return 'no directory specified'

        if not Path(self.directory).is_dir():
            return 'not yet created'

        if any((self.name in file_ and '.err' in file_) for file_ in listdir(self.directory)):
            return 'errored'

        self.setName(strict=True)

        subFile = f'{self.directory}{self.name}.sub'
        castepFile = f'{self.directory}{self.name}.castep'

        if Path(castepFile).is_file():
            with open(castepFile) as f:
                castepLines = f.read().splitlines()

            castepLines.reverse()  # Total time will be at the end of the file so will speed up the next loop.

            for line in castepLines:
                if line.strip().lower().startswith('total time'):
                    return 'completed'

            return 'running'

        elif Path(subFile).is_file():
            return 'submitted'

        else:
            return 'created'

    @staticmethod
    def getSettingLines(setting=None, maxSettingLength=0):
        assert isinstance(setting, Keyword) or isinstance(setting,
                                                          Block), f'Setting {setting} not a class of Keyword or Block'
        assert type(maxSettingLength) is int

        if isinstance(setting, Keyword):
            spaces = max(len(setting.key), maxSettingLength)
            unit = '' if setting.unit is None else f' {setting.unit}'
            return [f'{setting.key:<{spaces}s} : {setting.value}{unit}']

        elif isinstance(setting, Block):
            return [f'%block {setting.key}'] + setting.getLines() + [f'%endblock {setting.key}']

        else:
            raise TypeError(f'Setting {setting} not a class of Keyword or Block')

    def printHyperfine(self, all_=False, dipolar=False, fermi=False, showTensors=False, element=None):
        assert type(all_) is bool
        assert type(dipolar) is bool
        assert type(fermi) is bool
        assert type(showTensors) is bool

        if element is not None:
            assert type(element) is str

            element = element.strip()
            element = None if element == '' else element[0].upper() + element[1:].lower()

        string = 'Calculation ->'

        if self.name is not None:
            string += f' {self.name}'

        if self.directory is not None:
            string += f' ({self.directory})'

        string += '\n'

        if all_:
            tensorsList = [(self.hyperfineDipolarBareTensors, PrintColors.blue),
                           (self.hyperfineDipolarAugTensors, PrintColors.blue),
                           (self.hyperfineDipolarAug2Tensors, PrintColors.blue),
                           (self.hyperfineDipolarTensors, PrintColors.blue),
                           (self.hyperfineFermiTensors, PrintColors.green),
                           (self.hyperfineTotalTensors, PrintColors.orange)]

        elif not dipolar and not fermi:
            tensorsList = [(self.hyperfineDipolarTensors, PrintColors.blue),
                           (self.hyperfineFermiTensors, PrintColors.green),
                           (self.hyperfineTotalTensors, PrintColors.orange)]

        else:
            tensorsList = []

            if dipolar:
                tensorsList += [(self.hyperfineDipolarBareTensors, PrintColors.blue),
                                (self.hyperfineDipolarAugTensors, PrintColors.blue),
                                (self.hyperfineDipolarAug2Tensors, PrintColors.blue),
                                (self.hyperfineDipolarTensors, PrintColors.blue)]

            if fermi:
                tensorsList += [(self.hyperfineFermiTensors, PrintColors.green)]

        for tensors, color in tensorsList:
            for tensor in tensors:
                if element is None or (element is not None and tensor.element == element):
                    string += tensor.__str__(nameColor=color, showTensor=showTensors) + '\n'

        string = string[:-1]  # Remove last line break.

        print(string)

    def rotate(self, axis=None, angle=None, degrees=True):
        try:
            axis = asarray(axis, dtype=float)
        except ValueError:
            raise ValueError('Supply axis to rotate around as array-like e.g. [1, 1, 1]')

        assert type(angle) in [float, int]
        assert type(degrees) is bool

        angle = float(angle)

        # Convert angle to radians if needed.
        angle = pi * angle / 180.0 if degrees else angle

        # Normalise the axis to rotate around.
        axis = axis / sqrt(dot(axis, axis))

        # Ugly rotation matrix generation.
        a = cos(angle / 2.0)
        b, c, d = -axis * sin(angle / 2.0)
        aa, bb, cc, dd = a * a, b * b, c * c, d * d
        bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d

        rotationMatrix = array([[aa + bb - cc - dd,  2.0 * (bc + ad)  ,  2.0 * (bd - ac)  ],
                                [2.0 * (bc - ad)  ,  aa + cc - bb - dd,  2.0 * (cd + ab)  ],
                                [2.0 * (bd + ac)  ,  2.0 * (cd - ab)  ,  aa + dd - bb - cc]])

        for setting in self.settings:
            if setting.key in ['positions_frac', 'positions_abs']:
                setting.rotate(rotationMatrix=rotationMatrix)
                break
        else:
            raise ValueError('Could not find a setting for element positions')

    # TODO: consider fractional coordinates
    '''
    def translate(self, vector=None, unit='ang'):
        try:
            vector = asarray(vector, dtype=float)
        except ValueError:
            raise ValueError('Supply vector to translate by as array-like e.g. [1, 2, 3]')

        assert type(unit) is str

        unit = unit.strip().lower()

        # Extra unit checks and unit conversion done in setting object

        for setting in self.settings:
            if setting.key in ['positions_frac', 'positions_abs']:
                elementPositionSetting = setting
                break
        else:
            raise ValueError('Could not find a setting for element positions')

        if elementPositionSetting.key == 'positions_frac':
            for setting in self.settings:
                if setting.key in ['lattice_abc', 'lattice_cart']:
                    # TODO: consider fractional coordinates
                    pass

        elementPositionSetting.translate(translationVector=vector, unit=unit)
    '''

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
                raise FileNotFoundError(f'Cannot find alias file {bashAliasesFile}')

        if notificationAlias is None:
            notificationAlias = notificationAliasDefault
        else:
            assert type(notificationAlias) is str

        # Work out CASTEP prefix intelligently if calculation does not have a name
        self.setName(strict=True)

        directory = Path(self.directory)

        if not directory.is_dir():
            raise NotADirectoryError(f'Cannot find directory {self.directory} to run calculation')

        origDir = getcwd()

        chdir(self.directory)

        castep = f'castep.serial {self.name}' if serial else f'castep.mpi {self.name}'

        command = f'bash -c \'. {bashAliasesFile} ; {notificationAlias} {castep} &\''

        if test:
            print(f'|-> {command} <-| will be run in {getcwd()}')
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
            raise FileNotFoundError(f'Cannot find queue file {queueFile}')
        elif test:
            print(f'Found queue file {queueFile}')

        # Work out CASTEP prefix intelligently if calculation does not have a name
        self.setName(strict=True)

        directory = Path(self.directory)

        if not directory.is_dir():
            raise NotADirectoryError(f'Cannot find directory {self.directory} to run calculation')

        subFile = f'{self.directory}{self.name}.sub'

        if test:
            print(f'|-> {self.name} calculation queued at {datetime.now()} <-| will be appended to {subFile}')

            print(f'|-> {self.name}  {directory.resolve()} <-| will be appended to {queueFile}')

            if Path(subFile).is_file():
                print(f'*** CAUTION: sub file {subFile} found - calculation may already be submitted ***')

            print('')

        else:
            if Path(subFile).is_file() and not force:
                raise FileExistsError(f'Calculation may already be submitted {subFile} - use force=True to ignore')

            with open(subFile, 'a') as f:
                f.write(f'{self.name} calculation queued at {datetime.now()}\n')

            with open(queueFile, 'a') as f:
                f.write(f'{self.name}  {directory.resolve()}\n')

    def setName(self, strict=False):
        assert type(strict) is bool

        if self.name is not None:
            return

        self.name = None

        for setting in self.settings:
            if setting.key in ['positions_frac', 'positions_abs']:
                self.name = setting.findName()

        if self.name is None and strict:
            raise ValueError('Cannot find positions_frac/abs in cell, therefore cannot deduce CASTEP prefix (this will not run anyway)')

    def sortSettings(self):
        self.settings = sorted(self.settings, key=lambda setting: (setting.file, setting.priority))

    def updateSettings(self, *settings):
        settings = createSettings(*settings)

        for setting in settings:
            self.settings = [otherSetting for otherSetting in self.settings if otherSetting.key != setting.key]

            self.settings.append(setting)

            self.sortSettings()

    def removeSettings(self, *settingsToDeleteKeys):
        assert all(type(settingToDeleteKey) is str for settingToDeleteKey in settingsToDeleteKeys)

        for settingToDeleteKey in settingsToDeleteKeys:
            if settingToDeleteKey not in [setting.key for setting in self.settings]:
                print(f'*** Setting {settingToDeleteKey} not in settings - skipping ***')
                continue

            self.settings = [setting for setting in self.settings if setting.key != settingToDeleteKey]
