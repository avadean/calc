from casbot.data import assertCount, createDirectories,\
    pi, getElement,\
    getFileLines,\
    serialDefault, bashAliasesFileDefault, notificationAliasDefault, queueFileDefault,\
    PrintColors
from casbot.settings import Setting, createSettings, createVariableSettings, getSettings, getSettingLines, readSettings, StrBlock # TODO: profiling
from casbot.results import getResult

from copy import deepcopy
from datetime import datetime
from dateutil import parser
from fnmatch import filter
from itertools import product
from numpy import array, asarray, cos, dot, floor, sin, sqrt
from os import chdir, getcwd, listdir
from pathlib import Path
#from re import search
from subprocess import run as subProcessRun


def createCalculations(*variables, settings=None, directories=None, defaults=True):
    if settings is None:
        settings = []
    else:
        assert isinstance(settings, (list, tuple))

    if directories is None:
        directories = []
    else:
        assert isinstance(directories, (list, tuple))

    assert isinstance(defaults, bool)

    variableSettings = createVariableSettings(*variables)

    # Now that we have dealt with the variable cells/params of the calculations, we now work on the general cells/params.
    settings = createSettings(*settings)

    # Now let's deal with the directory names if given.
    directories = createDirectories(*directories)

    # If we've been given some directory names, then let's make sure they match the shape of the variable settings.
    if directories:
        if len(variableSettings) > 0:
            assert len(variableSettings) == len(directories), 'Number of variable settings must match directory depth'
            assert all(len(varSetts) == len(dirNames) for varSetts, dirNames in zip(variableSettings, directories)), \
                'Variable settings shape must match directories shape'

            # Add numbers to the start of each directory name.
            # directoryNames = [['{:03}_{}'.format(n, directoryNames[num][n-1]) for n in range(1, len(var) + 1)]
            # directoryNames = [[f'{directoryNames[num][n-1]}' for n in range(1, len(var) + 1)]
            #                  for num, var in enumerate(variableSettings)]
            directoryNames = [[f'{dirNames[n - 1]}' for n in range(1, len(varSetts) + 1)]
                              for varSetts, dirNames in zip(variableSettings, directories)]
        else:
            # If we don't actually have any variables settings, then make sure the number of directories is one.
            assert len(directories) == 1 == len(directories[0]), 'Only need one directory if no variable settings.'

            directoryNames = directories

    else:
        # If we don't have directory names then default to just numbers.
        if len(variableSettings) > 0:
            ## Try to use any specified strings from the variable settings as shortcuts for the directories, as often they are the same. Otherwise, just numbers.
            #directoryNames = [createDirectories(v1)[0] if isinstance(v1, str) else [f'{n:03}' for n in range(1, len(v2) + 1)] for v1, v2 in zip(variables, variableSettings)]
            # TODO: implement automatic directory names for variable shortcuts.

            directoryNames = [[f'{n:03}' for n in range(1, len(v) + 1)] for v in variableSettings]

        else:
            directoryNames = [['000']]

    #assert sum(any(isinstance(a, str) for a in variable) for variable in varSettingsProcessed) == 1,\
    #    'Can only have one iterable argument that is not a cell or param'

    # varSettingsProcessed looks like = [argument1, argument2, etc...]   ~ this is all the information
    # argumentI looks like = [sett1, sett2, sett3, etc...]    ~ each argument will be a directory
    # settI     looks like = [param1, param2, cell1, etc...]  ~ each setting has specific cells/params for that directory

    # Combinations will expand out the varSettingsProcessed and create every possible combination of the variable settings.
    # E.g. If we have argument1=['HF', 'HCl'] and argument2=[Cell(bField=1.0T), Cell(bField=2.0T)]
    # Then combinations will be: [(HF, bField 1.0T), (HF, bField 2.0T), (HCl, bField 1.0T), (HCl, bField 2.0T)]
    variables = list(product(*variableSettings))
    directoryNames = list(product(*directoryNames))

    if defaults:
        specifiedKeys = []

        for combination in variables:
            for listOfSettings in combination:
                for setting in listOfSettings:
                    if setting.key not in specifiedKeys:
                        specifiedKeys.append(setting.key)
            ## Will already have all of the specifiedKeys by this point.
            ## Don't use varSettingsProcessed[0] just incase varSettingsProcessed is empty.
            #break

        specifiedKeys += [setting.key for setting in settings]

        defaultSettings = createSettings('defaults')

        settings += [setting for setting in defaultSettings if setting.key not in specifiedKeys]

    calculations = []

    # Loop through the possible combinations.
    #for combNum, combination in enumerate(variables):
    for varSetts, dirNames in zip(variables, directoryNames):
        name = None

        directory = '' # '{}'.format(get current working directory)

        # For the specific variable cells/params.
        specificSettings = []

        # If we have variable settings, loop through the tuples of specific cells/params of this combination.
        if varSetts:
            for lstSetts, dirName in zip(varSetts, dirNames):
                directory += dirName

                # Loop through the specific tuple that contains many cells or params or both.
                for setting in lstSetts:
                    if isinstance(setting, Setting):
                        specificSettings.append(setting)

                    else:
                        raise TypeError(f'Only cells/params define a calculation, not {type(setting)}')

                directory += '/'

        else:
            # If we have no variable settings then there will only be on directory name.
            directory, = dirNames

        # Combine the general cells/params we want with the variable cells/params.
        # Specific settings override the global settings.
        settings = specificSettings + [setting for setting in settings if setting.key not in [setting2.key for setting2 in specificSettings]]

        # Calculation should have their own copy of settings.
        settings = deepcopy(settings)

        # Create the calculation.
        calculations.append(Calculation(name=name,
                                        directory=directory,
                                        settings=settings))

    return calculations



def processCalculations(*directories, parent=''):
    directories = createDirectories(*directories, parent=parent)

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
        cellFiles = [f for f in cellFiles if not f.endswith('-out.cell')]

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


def groupDensityCalculations(calculations=None):
    assert isinstance(calculations, list)
    assert all(isinstance(c, Calculation) for c in calculations)

    # calculations = sorted(self.calculations, key=lambda c: c.directory)
    # calculations = deepcopy(calculations)

    calculations = deepcopy(calculations)

    # We need to group together any xyz density-type calculations so they can be combined.
    # Let's set up the groups and a temp variable to hold each group.
    groups = []
    group = []

    # We are going to begin by searching for x, then y, then z.
    currentlyLookingFor = 'x'

    for c in calculations:
        if c.directory:

            # If we find this is an x type calculation.
            if c.directory[-2] == 'x' == currentlyLookingFor:
                currentlyLookingFor = 'y'  # Set the next search to be a y type calculation.

                if group:  # If the current group is not empty.
                    for g in group:
                        groups.append([g])  # Then just add those calculations as separate groups.

                group = [c]  # Make this x type calculation the start of a new group.

            # If we find this is a y type calculation.
            elif c.directory[-2] == 'y' == currentlyLookingFor:
                currentlyLookingFor = 'z'  # Set the next search to be a z type calculation.
                group.append(c)  # And add this one to the group.

            # If we find this is a z type calculation.
            elif c.directory[-2] == 'z' == currentlyLookingFor:
                currentlyLookingFor = 'x'  # Set the next search to be an x type calculation again.
                group.append(c)  # And add this one to the group.
                groups.append(group)  # And add that groups to the list of groups.
                group = []  # And start a new group again.

            # If we don't find this calculation to be of any specific type.
            else:
                # Add any current group calculations as separate groups.
                if group:
                    for g in group:
                        groups.append([g])

                groups.append([c])  # And then just add this calculation as a separate group too.

        else:  # If there is no directory name then just put this calculation in as a group on its own.
            groups.append([c])
            group = []

    if any([len(group) not in [1, 3] for group in groups]):
        return calculations

    calculations = []

    # for cX, cY, cZ in [calculations[n:n+3] for n in range(0, len(calculations), 3)]:
    for group in groups:

        # If we just have the one calculation then add that as normal.
        if len(group) == 1:
            calculations.append(group[0])
            continue

        # Otherwise, let's combine the three density calculations into one.
        # We will combine y and z into x.

        cX, cY, cZ = group

        if cX.name == cY.name == cZ.name:
            pass
        else:
            if cX.name is not None:
                cX.name = f'x:{cX.name} '

            if cY.name is not None:
                cX.name += f'y:{cY.name} '

            if cZ.name is not None:
                cX.name += f'z:{cZ.name} '

        if cX.name is not None:
            cX.name = cX.name.strip()

        cX.directory = f'{cX.directory[:-2]}xyz/'

        hyperfineDipolarBareTensors = [tensorX + tensorY + tensorZ
                                       for tensorX, tensorY, tensorZ in zip(cX.hyperfineDipolarBareTensors,
                                                                            cY.hyperfineDipolarBareTensors,
                                                                            cZ.hyperfineDipolarBareTensors)]

        hyperfineDipolarAugTensors = [tensorX + tensorY + tensorZ
                                      for tensorX, tensorY, tensorZ in zip(cX.hyperfineDipolarAugTensors,
                                                                           cY.hyperfineDipolarAugTensors,
                                                                           cZ.hyperfineDipolarAugTensors)]

        hyperfineDipolarAug2Tensors = [tensorX + tensorY + tensorZ
                                       for tensorX, tensorY, tensorZ in zip(cX.hyperfineDipolarAug2Tensors,
                                                                            cY.hyperfineDipolarAug2Tensors,
                                                                            cZ.hyperfineDipolarAug2Tensors)]

        hyperfineDipolarTensors = [tensorX + tensorY + tensorZ
                                   for tensorX, tensorY, tensorZ in zip(cX.hyperfineDipolarTensors,
                                                                        cY.hyperfineDipolarTensors,
                                                                        cZ.hyperfineDipolarTensors)]

        hyperfineFermiTensors = [tensorX + tensorY + tensorZ
                                 for tensorX, tensorY, tensorZ in zip(cX.hyperfineFermiTensors,
                                                                      cY.hyperfineFermiTensors,
                                                                      cZ.hyperfineFermiTensors)]

        hyperfineZFCTensors = [tensorX + tensorY + tensorZ
                               for tensorX, tensorY, tensorZ in zip(cX.hyperfineZFCTensors,
                                                                    cY.hyperfineZFCTensors,
                                                                    cZ.hyperfineZFCTensors)]

        hyperfineTotalTensors = [tensorX + tensorY + tensorZ
                                 for tensorX, tensorY, tensorZ in zip(cX.hyperfineTotalTensors,
                                                                      cY.hyperfineTotalTensors,
                                                                      cZ.hyperfineTotalTensors)]

        cX.hyperfineDipolarBareTensors = hyperfineDipolarBareTensors
        cX.hyperfineDipolarAugTensors = hyperfineDipolarAugTensors
        cX.hyperfineDipolarAug2Tensors = hyperfineDipolarAug2Tensors
        cX.hyperfineDipolarTensors = hyperfineDipolarTensors
        cX.hyperfineFermiTensors = hyperfineFermiTensors
        cX.hyperfineZFCTensors = hyperfineZFCTensors
        cX.hyperfineTotalTensors = hyperfineTotalTensors

        calculations.append(cX)

    return calculations


class Calculation:
    nmrCoreTensors = []
    nmrBareTensors = []
    nmrDiaTensors = []
    nmrParaTensors = []
    nmrTotalTensors = []

    efgBareTensors = []
    efgIonTensors = []
    efgAugTensors = []
    efgAug2Tensors = []
    efgTotalTensors = []

    hyperfineDipolarBareTensors = []
    hyperfineDipolarAugTensors = []
    hyperfineDipolarAug2Tensors = []
    hyperfineDipolarTensors = []
    hyperfineFermiTensors = []
    hyperfineZFCTensors = []
    hyperfineTotalTensors = []

    forces = []

    spinDensity = None

    positionsFrac = None

    def __init__(self, directory=None, settings=None, name=None):
        if directory is not None:
            assert isinstance(directory, str)

        if settings is not None:
            assert isinstance(settings, list)
            assert all(isinstance(setting, Setting) for setting in settings)
            assertCount([setting.key for setting in settings])

        if name is not None:
            assert isinstance(name, str)
            assert ' ' not in name, 'Cannot have spaces in name'

        self.directory = directory

        self.settings = settings
        self.sortSettings()

        self.name = name
        self.setName(strict=False)

        self.expectedSecToFinish = None

    def __str__(self):
        string = 'Calculation ->'

        self.setName(strict=False)

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

    def analyse(self, *toAnalyse, reset=True):
        assert isinstance(reset, bool)

        assert self.getStatus() == 'completed', 'Calculation not completed therefore cannot analyse'

        assert all(isinstance(type_, str) for type_ in toAnalyse)

        toAnalyse = set(type_.strip().lower() for type_ in toAnalyse)

        NMR = {'nmr', 'nuclear_magnetic_resonance', 'nuclearmagneticresonance', 'shielding', 'magnetic_shielding', 'magneticshielding'}

        EFG = {'efg', 'efgs', 'electric_field_gradient', 'electric_field_gradients', 'electricfieldgradient', 'electricfieldgradients'}

        HYPERFINE = {'hyperfine'}

        FORCES = {'forces'}

        SPINDENSITY = {'spin density', 'spin_density', 'spindensity'}

        POSFRACS = {'pos frac', 'pos fracs', 'position frac', 'position fracs', 'positions frac', 'positions fracs',
                    'pos_frac', 'pos_fracs', 'position_frac', 'position_fracs', 'positions_frac', 'positions_fracs',
                    'posfrac', 'posfracs', 'positionfrac', 'positionfracs', 'positionsfrac', 'positionsfracs'}

        # Check if there is actually any work to do.
        if not reset:
            if toAnalyse.intersection(NMR) and all([self.nmrCoreTensors,
                                                    self.nmrBareTensors,
                                                    self.nmrDiaTensors,
                                                    self.nmrParaTensors,
                                                    self.nmrTotalTensors]):
                toAnalyse -= NMR

            if toAnalyse.intersection(EFG) and all([self.efgBareTensors,
                                                    self.efgIonTensors,
                                                    self.efgAugTensors,
                                                    self.efgAug2Tensors,
                                                    self.efgTotalTensors]):
                toAnalyse -= EFG

            if toAnalyse.intersection(HYPERFINE) and all([self.hyperfineDipolarBareTensors,
                                                          self.hyperfineDipolarAugTensors,
                                                          self.hyperfineDipolarAug2Tensors,
                                                          self.hyperfineDipolarTensors,
                                                          self.hyperfineFermiTensors,
                                                          self.hyperfineTotalTensors]):
                toAnalyse -= HYPERFINE

            if toAnalyse.intersection(SPINDENSITY) and self.spinDensity:
                toAnalyse -= SPINDENSITY

            if toAnalyse.intersection(POSFRACS) and self.positionsFrac:
                toAnalyse -= POSFRACS

            if toAnalyse.intersection(FORCES) and self.forces:
                toAnalyse -= FORCES

        # If there is no work to do then return.
        if len(toAnalyse) == 0:
            return

        # We definitely need the name of the calculation so we can find files correctly.
        self.setName(strict=True)

        # Get the files.
        castepLines = None  # .castep file.
        magresLines = None  # .magres file.
        bandsLines = None  # .bands file.
        geomLines = None  # .geom file.

        outSettings = None  # -out.cell file.

        if toAnalyse.intersection(NMR) or toAnalyse.intersection(EFG) or toAnalyse.intersection(HYPERFINE) or toAnalyse.intersection(SPINDENSITY) or toAnalyse.intersection(FORCES):
            castepLines = getFileLines(file_=f'{self.directory}{self.name}.castep')
            castepLines = self.getFinalRunLines(lines=castepLines)

        if toAnalyse.intersection(POSFRACS):
            outSettings = readSettings(file_=f'{self.directory}{self.name}-out.cell')


        if toAnalyse.intersection(NMR):
            self.nmrCoreTensors = getResult(resultToGet='nmr_core', lines=castepLines)
            self.nmrBareTensors = getResult(resultToGet='nmr_bare', lines=castepLines)
            self.nmrDiaTensors = getResult(resultToGet='nmr_dia', lines=castepLines)
            self.nmrParaTensors = getResult(resultToGet='nmr_para', lines=castepLines)
            self.nmrTotalTensors = getResult(resultToGet='nmr_total', lines=castepLines)

            toAnalyse -= NMR

        if toAnalyse.intersection(EFG):
            self.efgBareTensors = getResult(resultToGet='efg_bare', lines=castepLines)
            self.efgIonTensors = getResult(resultToGet='efg_ion', lines=castepLines)
            self.efgAugTensors = getResult(resultToGet='efg_aug', lines=castepLines)
            self.efgAug2Tensors = getResult(resultToGet='efg_aug2', lines=castepLines)
            self.efgTotalTensors = getResult(resultToGet='efg_total', lines=castepLines)

            toAnalyse -= EFG

        if toAnalyse.intersection(HYPERFINE):
            self.hyperfineDipolarBareTensors = getResult(resultToGet='hyperfine_dipolarbare', lines=castepLines)
            self.hyperfineDipolarAugTensors = getResult(resultToGet='hyperfine_dipolaraug', lines=castepLines)
            self.hyperfineDipolarAug2Tensors = getResult(resultToGet='hyperfine_dipolaraug2', lines=castepLines)
            self.hyperfineDipolarTensors = getResult(resultToGet='hyperfine_dipolar', lines=castepLines)
            self.hyperfineFermiTensors = getResult(resultToGet='hyperfine_fermi', lines=castepLines)
            self.hyperfineZFCTensors = getResult(resultToGet='hyperfine_zfc', lines=castepLines)
            self.hyperfineTotalTensors = getResult(resultToGet='hyperfine_total', lines=castepLines)

            toAnalyse -= HYPERFINE

        if toAnalyse.intersection(SPINDENSITY):
            self.spinDensity = getResult(resultToGet='spin_density', lines=castepLines)

            toAnalyse -= SPINDENSITY

        if toAnalyse.intersection(FORCES):
            self.forces = getResult(resultToGet='forces', lines=castepLines)

            toAnalyse -= FORCES

        if toAnalyse.intersection(POSFRACS):
            self.positionsFrac = getSettings('positions_frac', settings=outSettings, attr='value')

            toAnalyse -= POSFRACS

        if toAnalyse:
            print(f'Skipping result{"" if len(toAnalyse) == 1 else "s"} {", ".join(toAnalyse)} as do not know how to analyse (yet)')

    def check(self, **kwargs):
        latestFinishTime = kwargs.get('latestFinishTime', 0.0)
        assert isinstance(latestFinishTime, (int, float))
        latestFinishTime = float(latestFinishTime)

        self.setName(strict=False)

        string = ' ->'

        if self.name is not None:
            nameOutputLen = kwargs.get('nameOutputLen', 0)
            assert isinstance(nameOutputLen, int) and nameOutputLen >= 0
            string += f'  {self.name:<{nameOutputLen}}'

        if self.directory is None:
            string += '  (no directory specified)'
            return
        else:
            dirOutputLen = kwargs.get('dirOutputLen', 0)
            assert isinstance(dirOutputLen, int) and dirOutputLen >= 0
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
            finishDateTime = datetime.fromtimestamp(datetime.now().timestamp() + self.expectedSecToFinish).strftime('%Y-%m-%d %H:%M:%S')

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

                #if 0 <= perCent < 25:
                #    timeColor = PrintColors.lightCyan
                #elif 25 <= perCent < 50:
                #    timeColor = PrintColors.lightGreen
                #elif 50 <= perCent < 75:
                #    timeColor = PrintColors.lightYellow
                #elif 75 <= perCent < 100:
                #    timeColor = PrintColors.lightOrange
                #elif perCent == 100:
                #    timeColor = PrintColors.underline + PrintColors.lightRed

                if 0 <= perCent < 33:
                    timeColor = PrintColors.lightGreen
                elif 33 <= perCent < 66:
                    timeColor = PrintColors.lightYellow
                elif 66 <= perCent < 99:
                    timeColor = PrintColors.lightOrange
                elif 99 <= perCent < 100:
                    timeColor = PrintColors.lightRed
                elif perCent == 100:
                    timeColor = PrintColors.underline + PrintColors.lightRed

            extraMessage = f'  expected finish time {timeColor}{finishDateTime}{PrintColors.reset}'
        else:
            extraMessage = ''

        string += f'  *** {statusColor}{status:^15}{PrintColors.reset} ***{extraMessage}'

        print(string)

    def create(self, force=False, passive=False):
        assert isinstance(force, bool)
        assert isinstance(passive, bool)

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

                    for line in getSettingLines(sttng=cell, maxSettingLength=0):
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

                    for line in getSettingLines(sttng=param, maxSettingLength=longestParam):
                        f.write(f'{line}\n')

        print(f'Created calculation for {self.name} in {directory}')

    def getFortFile(self, i=90, lines=True):
        assert isinstance(i, int)
        assert i >= 0, 'Cannot have negative fort file numbers'

        assert isinstance(lines, bool)

        if self.directory is None:
            raise FileNotFoundError('Calculation does not have a directory to find fort file')

        fortFile = f'{self.directory}fort.{i}'

        assert Path(fortFile).is_file(), f'Cannot find fort file {i}'

        if not lines:
            return fortFile

        with open(fortFile) as f:
            fortLines = f.read().splitlines()

        return fortLines

    @staticmethod
    def getFinalRunLines(lines=None):
        assert isinstance(lines, list)
        assert all(isinstance(line, str) for line in lines)

        # Reverse lines in case there were multiple continuations in CASTEP file.
        lines.reverse()

        for num, line in enumerate(lines):
            line = line.strip().lower()

            if line.startswith('run started:'):
                lines = lines[:num+1]  # :num and not num: due to .reverse() above.
                break
        else:
            raise ValueError('Cannot find any run started line in lines')

        # And reverse back to normal.
        lines.reverse()

        return lines

    def getCompletedTime(self):
        """ This function will work out (in seconds) how long it will take this calculation to complete """

        assert self.getStatus() == 'completed', 'Calculation not complete so cannot get completed time'

        castepFile = f'{self.directory}{self.name}.castep'

        assert Path(castepFile).is_file(), 'Cannot find castep file to get completed time'

        with open(castepFile) as f:
            castepLines = f.read().splitlines()

        castepLines = self.getFinalRunLines(lines=castepLines)

        castepLines.reverse()  # Total time at the end so quicker to reverse lines and go backwards.

        for line in castepLines:
            line = line.strip().lower()

            if line.startswith('total time'):

                # Check for sure it is indeed the total time printed at the end of the file.
                parts = line.split()

                if len(parts) <= 2 or parts[2] != '=':
                    continue

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

        castepLines = self.getFinalRunLines(lines=castepLines)

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

            # Names with numbers in seem to break the date-time parser (TODO: consider using a different parser for date-time as this one is rubbish)
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

        self.setName(strict=False)

        if self.name is None:
            return 'unnameable'

        subFile = f'{self.directory}{self.name}.sub'
        castepFile = f'{self.directory}{self.name}.castep'

        if Path(castepFile).is_file():
            with open(castepFile) as f:
                castepLines = f.read().splitlines()

            castepLines = self.getFinalRunLines(lines=castepLines)

            castepLines.reverse()  # Total time will be at the end of the file so will speed up the next loop.

            for line in castepLines:
                line = line.strip().lower()

                if line.startswith('total time'):
                    # Check for sure it is indeed the total time printed at the end of the file.
                    parts = line.split()

                    if len(parts) <= 2 or parts[2] != '=':
                        continue

                    return 'completed'

            return 'running'

        elif Path(subFile).is_file():
            return 'submitted'

        else:
            return 'created'

    def printNMR(self, **kwargs):
        element = kwargs.get('element', None)

        if element is not None:
            assert isinstance(element, str)

            element = getElement(element)

        all_ = kwargs.get('all', False)
        core = kwargs.get('core', False)
        bare = kwargs.get('bare', False)
        dia = kwargs.get('dia', False)
        para = kwargs.get('para', False)

        if all_:
            tensorsList = [self.nmrCoreTensors,
                           self.nmrBareTensors,
                           self.nmrDiaTensors,
                           self.nmrParaTensors,
                           self.nmrTotalTensors]

        elif not core and not bare and not dia and not para:
            tensorsList = [self.nmrTotalTensors]

        else:
            tensorsList = []

            if core:
                tensorsList.append(self.nmrCoreTensors)

            if bare:
                tensorsList.append(self.nmrBareTensors)

            if dia:
                tensorsList.append(self.nmrDiaTensors)

            if para:
                tensorsList.append(self.nmrParaTensors)

        string = ''

        for tensors in tensorsList:
            for tensor in tensors:
                if element is None or (element is not None and tensor.element == element):
                    string += f'{tensor}\n'

        if string:
            print(string[:-1])  # Remove last line break.

    def printEFG(self, **kwargs):
        element = kwargs.get('element', None)

        if element is not None:
            assert isinstance(element, str)

            element = getElement(element)

        all_ = kwargs.get('all', False)
        bare = kwargs.get('bare', False)
        ion = kwargs.get('ion', False)
        aug = kwargs.get('aug', False)

        if all_:
            tensorsList = [self.efgBareTensors,
                           self.efgIonTensors,
                           self.efgAugTensors,
                           self.efgAug2Tensors,
                           self.efgTotalTensors]

        elif not bare and not ion and not aug:
            tensorsList = [self.efgTotalTensors]

        else:
            tensorsList = []

            if bare:
                tensorsList.append(self.efgBareTensors)

            if ion:
                tensorsList.append(self.efgIonTensors)

            if aug:
                tensorsList.append(self.efgAugTensors)
                tensorsList.append(self.efgAug2Tensors)

        string = ''

        for tensors in tensorsList:
            for tensor in tensors:
                if element is None or (element is not None and tensor.element == element):
                    string += f'{tensor}\n'

        if string:
            print(string[:-1])  # Remove last line break.

    def printHyperfine(self, **kwargs):
        element = kwargs.get('element', None)

        if element is not None:
            assert isinstance(element, str)

            element = getElement(element)

        all_ = kwargs.get('all', False)
        dipolar = kwargs.get('dipolar', False)
        fermi = kwargs.get('fermi', False)
        tesla = kwargs.get('tesla', False)
        ppm = kwargs.get('ppm', False)

        if tesla and ppm:
            raise ValueError('Cannot choose units of Tesla and ppm for hyperfine print')

        bfield = None

        if ppm:
            # To convert to ppm we need to know the applied bfield.
            bfield = getSettings('external_bfield', settings=self.settings, attr='value')

            # Now need to get norm of bfield.
            # To get from MHz to bfield we need to know the gyromagnetic ratio of the element in question.


        if all_:
            tensorsList = [self.hyperfineDipolarBareTensors,
                           self.hyperfineDipolarAugTensors,
                           self.hyperfineDipolarAug2Tensors,
                           self.hyperfineDipolarTensors,
                           self.hyperfineFermiTensors,
                           self.hyperfineZFCTensors,
                           self.hyperfineTotalTensors]

        elif not dipolar and not fermi:
            tensorsList = [self.hyperfineDipolarTensors,
                           self.hyperfineFermiTensors,
                           self.hyperfineZFCTensors,
                           self.hyperfineTotalTensors]

        else:
            tensorsList = []

            if dipolar:
                tensorsList += [self.hyperfineDipolarBareTensors,
                                self.hyperfineDipolarAugTensors,
                                self.hyperfineDipolarAug2Tensors,
                                self.hyperfineDipolarTensors]

            if fermi:
                tensorsList += [self.hyperfineFermiTensors,
                                self.hyperfineZFCTensors]

        string = ''

        for tensors in tensorsList:
            for tensor in tensors:
                if element is None or (element is not None and tensor.element == element):
                    string += f'{tensor}\n'

        if string:
            print(string[:-1])  # Remove last line break.

    def printForces(self, **kwargs):
        if self.forces:
            string = '             Fx             Fy             Fz'

            for force in self.forces:
                string += f'\n   {force}'

            print(string)

    def printSpinDensity(self, **kwargs):
        if self.spinDensity is not None:
            if self.spinDensity.shape == (3, 1):
                print(f'             Sx             Sy             Sz\n        {self.spinDensity}')
            else:
                print(f'                             S\n                       {self.spinDensity}')

    def rotate(self, axis=None, angle=None, degrees=True, setting=None):
        try:
            axis = asarray(axis, dtype=float)
        except ValueError:
            raise ValueError('Supply axis to rotate around as array-like e.g. [1, 1, 1]')

        assert isinstance(angle, (int, float))
        assert isinstance(degrees, bool)

        if setting is not None:
            assert isinstance(setting, str)
            setting = setting.strip().lower()

        angle = float(angle)

        # Convert angle to radians if needed.
        angle = pi * angle / 180.0 if degrees else angle

        # Normalise the axis to rotate around.
        length = sqrt(dot(axis, axis))

        assert length != 0.0, 'Cannot rotate around the zero vector'

        axis /= length

        # Ugly rotation matrix generation.
        a = cos(angle / 2.0)
        b, c, d = -axis * sin(angle / 2.0)
        aa, bb, cc, dd = a * a, b * b, c * c, d * d
        bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d

        rotationMatrix = array([[aa + bb - cc - dd,  2.0 * (bc + ad)  ,  2.0 * (bd - ac)  ],
                                [2.0 * (bc - ad)  ,  aa + cc - bb - dd,  2.0 * (cd + ab)  ],
                                [2.0 * (bd + ac)  ,  2.0 * (cd - ab)  ,  aa + dd - bb - cc]])

        if setting is None:
            s = getSettings('positions_abs', 'positions_frac', settings=self.settings)

            if s.count(None) == 0:
                raise ValueError('Cannot find positions_abs or positions_frac to rotate')

            if s.count(None) == 2:
                raise ValueError('Both positions_abs and positions_frac specified, do not know which to rotate')

            # Get whichever value is not None.
            s = next(sttng for sttng in s if sttng is not None)

        else:
            s, = getSettings(setting, settings=self.settings)

            if s is None:
                raise ValueError(f'Cannot find setting {setting} to rotate')

        try:
            s.rotate(rotationMatrix=rotationMatrix)
        except AttributeError:
            raise AttributeError(f'Setting {s.key} does not have a rotation definition')

    # TODO: consider fractional coordinates
    '''
    def translate(self, vector=None, unit='ang'):
        try:
            vector = asarray(vector, dtype=float)
        except ValueError:
            raise ValueError('Supply vector to translate by as array-like e.g. [1, 2, 3]')

        assert isinstance(unit, str)

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

        assert isinstance(test, bool)

        if serial is None:
            serial = serialDefault
        else:
            assert isinstance(serial, bool)

        if bashAliasesFile is None:
            bashAliasesFile = bashAliasesFileDefault

            if bashAliasesFile is None:
                raise FileNotFoundError('No bash aliases file loaded as default.')
        else:
            assert isinstance(bashAliasesFile, str)

            if not Path(bashAliasesFile).is_file():
                raise FileNotFoundError(f'Cannot find alias file {bashAliasesFile}')

        if notificationAlias is None:
            notificationAlias = notificationAliasDefault
        else:
            assert isinstance(notificationAlias, str)

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

        assert isinstance(test, bool)
        assert isinstance(force, bool)

        if queueFile is None:
            queueFile = queueFileDefault

            if queueFile is None:
                raise FileNotFoundError('No queue file loaded as default.')

        else:
            assert isinstance(queueFile, str)

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
        assert isinstance(strict, bool)

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
        assert all(isinstance(settingToDeleteKey, str) for settingToDeleteKey in settingsToDeleteKeys)

        for settingToDeleteKey in settingsToDeleteKeys:
            if settingToDeleteKey not in [setting.key for setting in self.settings]:
                print(f'*** Setting {settingToDeleteKey} not in settings - skipping ***')
                continue

            self.settings = [setting for setting in self.settings if setting.key != settingToDeleteKey]

    def addProf(self, *args, **kwargs):
        # TODO: profiling
        full = kwargs.get('full', False)

        assert isinstance(full, bool)

        develCode = getSettings('devel_code', settings=self.settings)

        if develCode is None:
            l = ['FULL_TRACE', 'PROF: * :ENDPROF'] if full else ['PROF: * :ENDPROF']

            develCode = StrBlock('devel_code', lines=l)

            self.updateSettings(develCode)

        else:
            if full and 'FULL_TRACE' not in develCode.lines:
                develCode.lines.append('FULL_TRACE')

            if 'PROF: * :ENDPROF' not in develCode.lines:
                develCode.lines.append('PROF: * :ENDPROF')
