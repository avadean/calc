from casbot.calculation import Calculation, groupDensityCalculations

from collections import Counter
from matplotlib.pyplot import plot, scatter, show, xscale, xlabel, ylabel
from numpy import ndarray
from numpy.linalg import norm
from pathlib import Path
from pickle import dump as pickleDump, load as pickleLoad
from random import sample
from tqdm import tqdm


class Model:
    def __init__(self, calculations=None, name=None):
        if name is not None:
            assert type(name) is str

        self.name = name

        self.calculations = []

        if calculations is not None:
            assert type(calculations) is list
            assert all(type(calculation) is Calculation for calculation in calculations)
            self.calculations = calculations

        self.species = self.getSpecies(calculations=self.calculations, strict=False)

    def __str__(self):
        string = ''

        for calculation in self.calculations:
            string += f'{calculation}\n'

        string = string[:-1] # Remove last line break.

        return string

    def __len__(self):
        return len(self.calculations)

    def analyse(self, *toAnalyse, passive=False, reset=True):
        assert all(type(type_) is str for type_ in toAnalyse)
        assert type(passive) is bool
        assert type(reset) is bool

        assert len(self.calculations) > 0, 'No calculations to analyse'

        completedCalculations = [c for c in self.calculations if c.getStatus() == 'completed']

        if len(completedCalculations) == 0:
            print('No calculations have completed')
            return

        #assert len(completedCalculations) > 0, 'No calculations have completed'

        if len(completedCalculations) == len(self.calculations):
            print(f'All {len(self.calculations)} calculations have completed. Analysing...')

        elif not passive:
            raise ValueError('Not all calculations have completed - use passive=True to ignore incomplete calculations')

        else:
            print(f'{len(completedCalculations)} calculations have completed out of {len(self.calculations)}. Analysing completed calculations...')

        toAnalyse = [type_.strip().lower() for type_ in toAnalyse]

        # tqdm is for loading bar
        for calculation in tqdm(iterable=completedCalculations, ncols=100, unit='calculation'):
            calculation.analyse(*toAnalyse, reset=reset)

    def check(self):
        # TODO: add in summary option and maybe default to only showing running and the next 3(?) submitted calculations - could also print the expected finish time of the fine calculation, too
        self.species = self.getSpecies(calculations=self.calculations, strict=True)

        totalTimeCompleted = {species: 0.0 for species in self.species.keys()}

        numCompleted = Counter()
        numRunning = Counter()
        numSubmitted = Counter()

        for c in self.calculations:
            status = c.getStatus()

            #if status in ['no directory specified', 'errored', 'created', 'not yet created']:
            #    continue

            if status == 'completed':
                numCompleted[c.name] += 1
                totalTimeCompleted[c.name] += c.getCompletedTime()

            elif status == 'running':
                numRunning[c.name] += 1

            elif status == 'submitted':
                numSubmitted[c.name] += 1

        if sum((numRunning + numSubmitted).values()) and sum(numCompleted.values()):
            averageTimeCompleted = {species: None if numCompleted[species] == 0 else totalTimeCompleted[species] / numCompleted[species] for species in self.species.keys()}

            # Get the running calculations first
            calculations = [calc for calc in self.calculations if calc.getStatus() == 'running']

            # Now add the submitted calculations based on when they were submitted
            # We need them ordered this way so we know what order they will be ran in
            # Of course, this doesn't matter for the running calculations because they've already started!
            # If a running calculation started from calling run and not being submitted then it won't have a subTime
            # This is why we can't just create the calculations in one list... We could using this:
            # calculations = sorted([calc for calc in self.calculations if calc.getStatus() in ['running', 'submitted']],
            #                        key=lambda calc: (calc.getRunTime() or float("inf"), calc.getSubTime() or float("inf")))
            # but that's a bit messy and is technically a little hard-codey - the inf are to account for None values
            calculations += sorted([calc for calc in self.calculations if calc.getStatus() == 'submitted'],
                                   key=lambda calc: calc.getSubTime())

            # If we can run n calculations at once, we don't need to work in serial, so we create a parallel set of finish times where n = number running at that moment.
            numRunning = max(sum(numRunning.values()), 1)
            finishTimes = [0.0] * numRunning  # Number of seconds away from now a calculation is expected to finish.

            for c in calculations:

                # If there are completed calculations for this species, take the average of those, otherwise take the average of all the completed calculations.
                # Note: sum(numCompleted.values()) cannot be zero due to the if statement check above - so no worries on ZeroDivisionError here.
                timeForThisCalculation = averageTimeCompleted[c.name] if numCompleted[c.name] > 0 else sum(totalTimeCompleted.values()) / float(sum(numCompleted.values()))

                if c.getStatus() == 'running':
                    timeForThisCalculation -= c.getRunningTime()
                    timeForThisCalculation = max(0.0, timeForThisCalculation)

                nextFinishTime = min(finishTimes)
                index = finishTimes.index(nextFinishTime)

                finishTimes[index] += timeForThisCalculation

                c.expectedSecToFinish = finishTimes[index]

        maxNameLen = max(map(lambda calc: len(calc.name or ''), self.calculations), default=0)
        maxDirLen = max(map(lambda calc: len(calc.directory or ''), self.calculations), default=0)
        latestFinishTime = max(map(lambda calc: calc.expectedSecToFinish or 0.0, self.calculations), default=0.0)

        calculations = sorted(self.calculations, key=lambda calc: (calc.expectedSecToFinish or 0.0, calc.directory or ''))

        for c in calculations:
            c.check(nameOutputLen=maxNameLen, dirOutputLen=maxDirLen, latestFinishTime=latestFinishTime)

        for c in self.calculations:
            c.expectedSecToFinish = None

    def create(self, force=False, passive=False):
        assert type(force) is bool
        assert type(passive) is bool

        if force and passive:
            raise ValueError('Cannot create model with force=True and passive=True - use one option as True only')

        if len(self.calculations) == 0:
            raise ValueError('No calculations to create')

        if any(calculation.directory is None for calculation in self.calculations):
            raise ValueError('Cannot create calculations when directories are not defined')

        if not force and not passive and any(Path(calculation.directory).exists() for calculation in self.calculations):
            raise FileExistsError('Some directories already exist - use force=True to overwrite or passive=True to ignore')

        for calculation in self.calculations:
            calculation.create(force=force, passive=passive)

    def edit(self, parameter=None, **kwargs):  # def edit(self, parameter=None, *names, **kwargs):
        assert type(parameter) is str

        parameter = parameter.strip().lower()

        if parameter in ['rotate', 'rotation']:
            for calculation in self.calculations:
                calculation.rotate(**kwargs)

        elif parameter in ['translate', 'translation']:
            raise NotImplementedError('Translation editing not yet implemented')

        else:
            raise ValueError(f'Parameter {parameter} not known')

    @staticmethod
    def getSpecies(calculations=None, strict=False):
        assert type(strict) is bool
        assert type(calculations) is list
        assert all(type(calculation) is Calculation for calculation in calculations)

        for calculation in calculations:
            calculation.setName(strict=strict)

        return Counter(calculation.name for calculation in calculations)

    def plot(self, x=None, y=None, **kwargs):
        assert type(x) in [str, list, ndarray]
        assert type(y) in [str, list, ndarray]
        assert all(type(kwarg) is str for kwarg in kwargs)

        kwargs = {key.strip().lower(): val for key, val in kwargs.items()}

        density = kwargs.get('density', True)

        doneX, doneY = False, False

        if type(x) is list: x, doneX = x, True
        if type(x) is ndarray: x, doneX = x, True
        if type(y) is list: y, doneY = y, True
        if type(y) is ndarray: y, doneY = y, True

        calculations = groupDensityCalculations(calculations=self.calculations) if density else self.calculations

        if not doneX and not doneY:
            xlabel(x)
            ylabel(y)
            x, y = self.processStrAxis(x, y, calculations=calculations, **kwargs)

        elif not doneX:
            xlabel(x)
            x, = self.processStrAxis(x, calculations=calculations, **kwargs)

        elif not doneY:
            ylabel(y)
            y, = self.processStrAxis(y, calculations=calculations, **kwargs)

        assert len(x) == len(y), f'Mismatch in x and y axis lengths: x is {len(x)}, y is {len(y)}'

        typeOfPlot = kwargs.get('type', 'plot')
        assert type(typeOfPlot) is str, 'Enter plot type as string'
        typeOfPlot = typeOfPlot.strip().lower()
        assert typeOfPlot in ['plot', 'scatter', 'both'], f'Plotting type should be {", ".join(["plot", "scatter", "both"])}'

        logarithmic = kwargs.get('log', False)
        assert type(logarithmic) is bool, 'Enter logarithmic type as bool'

        if typeOfPlot in ['plot', 'both']:
            plot(x, y)

        if typeOfPlot in ['scatter', 'both']:
            scatter(x, y)

        if logarithmic:
            xscale('log')

        show()

    @staticmethod
    def processStrAxis(*args, calculations=None, **kwargs):
        assert all(type(arg) is str for arg in args)
        assert len(args) != 0, 'Enter at least one axis to process'
        assert len(args) in (1, 2), 'Can only plot 2 dimensions for now'
        assert all(type(kwarg) is str for kwarg in kwargs)

        knownPlots = {'bfield', 'nmriso', 'fermiiso', 'fermiisobfield', 'kpointspacing'}

        args = [arg.strip().lower() for arg in args]

        # Don't set args to a set as it randomly changes the ordering and thus the ordering of the returned x and y values.

        assert not set(args) - knownPlots, f'Do not know how to plot {", ".join(set(args) - knownPlots)}'

        assert type(calculations) is list
        assert all(type(c) is Calculation for c in calculations)

        # Generalised in case n dimensions is needed.
        values = []  # Values of each argument for each calculation.

        # Settings for specific argument.
        kwargs = {key.strip().lower(): val for key, val in kwargs.items()}
        element = kwargs.get('element', None)
        ion = kwargs.get('ion', None)

        for c in calculations:
            cValues = []  # Values of each argument for this specific calculation.

            for arg in args:
                cValue = None  # Value of argument for this specific calculation.

                if arg == 'bfield':
                    # Due to the groupDensityCalculations, the bfield will only pick up one component if density = True.
                    cValue = norm(c.getSettingValue('external_bfield'))

                elif arg in ['nmriso']:
                    if not c.nmrTotalTensors:
                        continue

                    assert type(element) is str, 'Enter element to get NMR total tensor for'
                    assert type(ion) is int, 'Enter ion to get NMR total tensor for'

                    element = element.strip()

                    assert element, 'Enter element to get NMR total tensor for'

                    elementTensors = [tensor for tensor in c.nmrTotalTensors if tensor.element.strip().lower() == element.lower()]

                    assert elementTensors, f'Cannot find any NMR total tensors corresponding to element {element}'

                    assert len(elementTensors) >= ion, f'Ion requested for NMR total tensor does not exist, found {len(elementTensors)} tensors'

                    cValue = elementTensors[ion-1].iso  # -1 because of Python indexing.

                elif arg in ['fermiiso', 'fermiisobfield']:
                    if not c.hyperfineFermiTensors:
                        continue

                    assert type(element) is str, 'Enter element to get Fermi tensor for'
                    assert type(ion) is int, 'Enter ion to get Fermi tensor for'

                    element = element.strip()

                    assert element, 'Enter element to get Fermi tensor for'

                    elementTensors = [tensor for tensor in c.hyperfineFermiTensors if tensor.element.strip().lower() == element.lower()]

                    assert elementTensors, f'Cannot find any Fermi tensors corresponding to element {element}'

                    assert len(elementTensors) >= ion, f'Ion requested for Fermi tensor does not exist, found {len(elementTensors)} tensors'

                    cValue = elementTensors[ion-1].iso  # -1 because of Python indexing.

                    # If fermiisobfield then we want the Fermi iso value divided by the bfield.
                    if arg == 'fermiisobfield':
                        cValue /= norm(c.getSettingValue('external_bfield'))

                elif arg == 'kpointspacing':
                    cValue = c.getSettingValue('kpoint_mp_spacing')

                cValues.append(cValue)

            # If we didn't find something correctly then we will have a None value - so ignore this point.
            # Also, if we ignored a calculation because there was no value to find then our calcValues will not be the same lengths as the number of arguments asked for.
            if any(val is None for val in cValues) or len(cValues) != len(args):
                continue

            # Concatenate new values onto current stack of values.
            values.append(cValues)

        # Each calculation's values are stored in a tuple in the values list. Zip the list together to return the x, y, etc. axis values individually.
        values = zip(*values)  # We won't lose anything through zipping because of the len(cValues) != len(args) check above.

        return values  #axisValues if len(axisValues) > 1 else axisValues[0]  # length can't be 0

    def print(self, *args, **kwargs):
        if len(args) == 0:
            return

        assert all(type(arg) is str for arg in args)

        args = set([arg.strip().lower() for arg in args])

        assert all(type(kwarg) is str for kwarg in kwargs)

        kwargs = {kwarg.strip().lower(): val for kwarg, val in kwargs.items()}

        group = kwargs.get('group', True)

        calculations = self.calculations

        # Hyperfine calculations are a bit odd so we treat them separately for now as a hack.
        # If we are doing a density_in_x, density_in_y, density_in_z calculation, then temporarily make the calculations in groups of 3.
        # Only do this if hyperfine is the only thing we're asking for.
        if len(args) == 1 and 'hyperfine' in args and group:
            # and len(self.calculations) % 3 == 0\
            # and all([c.directory[:-2].endswith('density_in_') for c in self.calculations]):  # 2 characters for '/' and, 'x' or 'y' or 'z'

            calculations = groupDensityCalculations(calculations=self.calculations)

        for calculation in calculations:
            string = 'Calculation ->'

            if calculation.name is not None:
                string += f' {calculation.name}'

            if calculation.directory is not None:
                string += f' ({calculation.directory})'

            print(string)

            if {'forces'}.intersection(args):
                calculation.printForces(**kwargs)
                print('')

            if {'spindensity', 'spin density', 'spin_density'}.intersection(args):
                calculation.printSpinDensity(**kwargs)
                print('')

            if {'nmr'}.intersection(args):
                calculation.printNMR(**kwargs)
                print('')

            if {'efg', 'efgs'}.intersection(args):
                calculation.printEFG(**kwargs)
                print('')

            if {'hyperfine'}.intersection(args):
                calculation.printHyperfine(**kwargs)
                print('')

    def run(self, test=False, force=False, passive=False, shuffle=False, serial=None, bashAliasesFile=None, notificationAlias=None):
        assert type(test) is bool
        assert type(force) is bool
        assert type(passive) is bool
        assert type(shuffle) is bool

        if serial is not None:
            assert type(serial) is bool

        if bashAliasesFile is not None:
            assert type(bashAliasesFile) is str

        if notificationAlias is not None:
            assert type(notificationAlias) is str

        calculations = [c for c in self.calculations if c.getStatus() not in ['completed', 'running', 'submitted']]

        if len(calculations) != len(self.calculations) and not passive:
            raise ValueError('Some calculations are complete, already running or submitted - use passive=True to skip them')

        if len(calculations) > 3 and not force:
            if test:
                print('*** WARNING: this is a lot of calculations to run at once - use force=True to ignore on real run ***')
                print('*** Continuing test... ***')
            else:
                raise MemoryError('Too many calculations to run at once - use force=True to ignore')

        if len(calculations) > 5:
            if test:
                print('*** WARNING: this is too many calculations - consider calling sub instead ***')
                print('*** Continuing test... ***')
            else:
                raise MemoryError('No seriously - don\'t do this many calculations - consider calling sub instead')

        calculations = sample(calculations, k=len(calculations)) if shuffle else calculations

        for calculation in calculations:
            calculation.run(test=test,
                            serial=serial,
                            bashAliasesFile=bashAliasesFile,
                            notificationAlias=notificationAlias)

        if test:
            print(f'*** Total of {len(calculations)} calculations to run - none have gone yet ***')
        else:
            print(f'*** Ran {len(calculations)} calculations ***')

    def sub(self, test=False, force=False, passive=False, shuffle=False, reverse=False, queueFile=None):
        assert type(test) is bool
        assert type(force) is bool
        assert type(passive) is bool
        assert type(shuffle) is bool
        assert type(reverse) is bool

        if not force:
            calculations = [c for c in self.calculations if c.getStatus() not in ['completed', 'running', 'submitted']]

            if len(calculations) != len(self.calculations) and not passive:
                raise ValueError('Some calculations are complete, running or already submitted - use passive=True to skip them or force=True to re-run them')
        else:
            calculations = self.calculations

        if shuffle:
            assert not reverse

        if queueFile is not None:
            assert type(queueFile) is str

        calculations = sample(calculations, k=len(calculations)) if shuffle else calculations

        if reverse:
            calculations.reverse()

        for calculation in calculations:
            calculation.sub(test=test,
                            force=force,
                            queueFile=queueFile)

        if test:
            print(f'*** Total of {len(calculations)} calculations to submit - none have gone yet ***')
        else:
            print(f'*** Submitted {len(calculations)} calculations ***')

    def save(self, file=None, overwrite=False):
        assert type(file) is str
        assert type(overwrite) is bool

        assert not Path(file).is_file() or overwrite, f'File {file} exists - use overwrite=True to overwrite'

        with open(file, 'wb') as f:
            pickleDump(self, f)

        print(f'Model with {len(self.calculations)} calculations saved to {file} successfully')

    @staticmethod
    def load(file=None):
        assert type(file) is str
        assert Path(file).is_file(), f'Cannot find file {file}'

        with open(file, 'rb') as f:
            model = pickleLoad(f)

        print(f'Model with {len(model.calculations)} calculations loaded successfully')

        return model

    def updateSettings(self, *settings):
        for calculation in self.calculations:
            calculation.updateSettings(*settings)

    def removeSettings(self, *settingsToDeleteKeys):
        for calculation in self.calculations:
            calculation.removeSettings(*settingsToDeleteKeys)

    def addProf(self, *args, **kwargs):
        # TODO: profiling
        for calculation in self.calculations:
            calculation.addProf(*args, **kwargs)
