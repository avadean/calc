from casbot.calculation import Calculation

from collections import Counter
from pathlib import Path
from random import sample
from tqdm import tqdm


class Model:
    def __init__(self, calculations=None, name=None):
        if name is not None:
            assert type(name) is str

        self.name = name

        if calculations is None:
            self.calculations = []
        else:
            assert type(calculations) is list
            assert all(type(calculation) == Calculation for calculation in calculations)
            self.calculations = calculations

        self.species = Counter()
        self.setSpecies(strict=False)

        #print(self.getDirString())

    def __str__(self):
        string = ''

        for calculation in self.calculations:
            string += calculation.__str__() + '\n'

        string = string[:-1] # Remove last line break.

        return string

    def analyse(self, type_=None, passive=False):
        assert type(type_) is str
        assert type(passive) is bool

        type_ = type_.strip().lower()

        numCompleted = sum(c.getStatus() == 'completed' for c in self.calculations)

        if numCompleted == len(self.calculations):
            print('All {} calculations have completed. Analysing...'.format(len(self.calculations)))

        elif not passive:
            raise ValueError('Not all calculations have completed - use passive=True to ignore incomplete calculations')

        else:
            print('{} calculations have completed out of {}. Analysing completed calculations...'.format(numCompleted, len(self.calculations)))

        # tqdm is for loading bar
        for calculation in tqdm(iterable=self.calculations, ncols=100, unit='calculation'):
            if calculation.getStatus() == 'completed':
                calculation.analyse(type_=type_)

    def check(self):
        # TODO: add in summary option and maybe default to only showing running and the next 3(?) submitted calculations - could also print the expected finish time of the fine calculation, too
        self.setSpecies(strict=True)

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

        if sum((numRunning + numSubmitted).values()) > 0 and sum(numCompleted.values()):
            averageTimeCompleted = {species: None if numCompleted[species] == 0 else totalTimeCompleted[species] / numCompleted[species] for species in self.species.keys()}

            # Get the running calculations first
            calculations = [calc for calc in self.calculations if calc.getStatus() == 'running']

            # Now add the submitted calculations based on when they were submitted
            # We need them ordered this way so we know what order they will be ran in
            # Of course, this doesn't matter for the running calculations because they've already started!
            calculations += sorted([calc for calc in self.calculations if calc.getStatus() == 'submitted'],
                                   key=lambda calc: calc.getSubTime())

            # If we can run n calculations at once, we don't need to work in serial, so we create a parallel set of finish times where n = number running at that moment.
            numRunning = max(sum(numRunning.values()), 1)
            finishTimes = [0.0 for _ in range(numRunning)]  # Number of seconds away from now a calculation is expected to finish.

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

        maxNameLen = max([len(calc.name) for calc in self.calculations if calc.name is not None], default=0)
        maxDirLen = max([len(calc.directory) for calc in self.calculations if calc.directory is not None], default=0)

        for c in self.calculations:
            c.check(nameOutputLen=maxNameLen, dirOutputLen=maxDirLen)

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

    def getDirString(self):
        if len(self.calculations) == 0:
            return ''

        string = ''

        for calculation in self.calculations:
            string += '{}\n'.format(calculation.directory)

        string = string[:-1]  # Remove last line break.

        return string

    def setSpecies(self, strict=False):
        assert type(strict) is bool

        if len(self.species) > 0 and all(self.species.keys()):
            return

        for calculation in self.calculations:
            calculation.setName(strict=strict)

        self.species = Counter(calculation.name for calculation in self.calculations)

    def printHyperfine(self, all_=False, dipolar=False, fermi=False, showTensors=False, element=None):
        assert type(all_) is bool
        assert type(dipolar) is bool
        assert type(fermi) is bool
        assert type(showTensors) is bool

        if element is not None:
            assert type(element) is str

            element = element.strip()
            element = None if element == '' else element[0].upper() + element[1:].lower()

        for calculation in self.calculations:
            calculation.printHyperfine(all_=all_, dipolar=dipolar, fermi=fermi, showTensors=showTensors, element=element)
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
            print('*** Total of {} calculations to run - none have gone yet ***'.format(len(calculations)))
        else:
            print('*** Ran {} calculations ***'.format(len(calculations)))

    def sub(self, test=False, force=False, passive=False, shuffle=False, queueFile=None):
        assert type(test) is bool
        assert type(force) is bool
        assert type(passive) is bool
        assert type(shuffle) is bool

        calculations = [c for c in self.calculations if c.getStatus() not in ['completed', 'running', 'submitted']]

        if len(calculations) != len(self.calculations) and not passive:
            raise ValueError('Some calculations are complete, running or already submitted - use passive=True to skip them')

        if queueFile is not None:
            assert type(queueFile) is str

        calculations = sample(calculations, k=len(calculations)) if shuffle else calculations

        for calculation in calculations:
            calculation.sub(test=test,
                            force=force,
                            queueFile=queueFile)

        if test:
            print('*** Total of {} calculations to submit - none have gone yet ***'.format(len(calculations)))
        else:
            print('*** Submitted {} calculations ***'.format(len(calculations)))

    def updateSettings(self, *settings):
        for calculation in self.calculations:
            calculation.updateSettings(*settings)
