from casbot.calculation import Calculation

from collections import Counter
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
            string += calculation.__str__() + '\n'

        string = string[:-1] # Remove last line break.

        return string

    def analyse(self, *toAnalyse, passive=False, reset=True):
        assert all(type(type_) is str for type_ in toAnalyse)
        assert type(passive) is bool
        assert type(reset) is bool

        assert len(self.calculations) > 0, 'No calculations to analyse'

        completedCalculations = [c for c in self.calculations if c.getStatus() == 'completed']

        assert len(completedCalculations) > 0, 'No calculations have completed'

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

    def print(self, *args, **kwargs):
        assert all(type(arg) is str for arg in args)

        args = set([arg.strip().lower() for arg in args])

        for calculation in self.calculations:
            string = 'Calculation ->'

            if calculation.name is not None:
                string += f' {calculation.name}'

            if calculation.directory is not None:
                string += f' ({calculation.directory})'

            print(string)

            if {'spindensity', 'spin density', 'spin_density'}.intersection(args):
                calculation.printSpinDensity(**kwargs)
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

    def sub(self, test=False, force=False, passive=False, shuffle=False, queueFile=None):
        assert type(test) is bool
        assert type(force) is bool
        assert type(passive) is bool
        assert type(shuffle) is bool

        if not force:
            calculations = [c for c in self.calculations if c.getStatus() not in ['completed', 'running', 'submitted']]

            if len(calculations) != len(self.calculations) and not passive:
                raise ValueError('Some calculations are complete, running or already submitted - use passive=True to skip them or force=True to re-run them')
        else:
            calculations = self.calculations

        if queueFile is not None:
            assert type(queueFile) is str

        calculations = sample(calculations, k=len(calculations)) if shuffle else calculations

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

        pickleDump(self, open(file, 'wb'))

        print(f'Model with {len(self.calculations)} calculations saved to {file} successfully')

    @staticmethod
    def load(file=None):
        assert type(file) is str
        assert Path(file).is_file(), f'Cannot find file {file}'

        model = pickleLoad(open(file, 'rb'))

        print(f'Model with {len(model.calculations)} calculations loaded successfully')

        return model

    def updateSettings(self, *settings):
        for calculation in self.calculations:
            calculation.updateSettings(*settings)

    def removeSettings(self, *settingsToDeleteKeys):
        for calculation in self.calculations:
            calculation.removeSettings(*settingsToDeleteKeys)
