from casbot.calculation import Calculation

from collections import Counter
from pathlib import Path
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

        print('*** Model defined with {} calculation{} ***'.format(len(self.calculations),
                                                                   '' if len(self.calculations) == 1 else 's'))

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
        self.setSpecies(strict=True)

        speciesCompletedTime = {species: 0.0 for species in self.species.keys()}
        speciesRunningTime = {species: 0.0 for species in self.species.keys()}

        speciesNumCompleted = Counter()
        speciesNumRunning = Counter()

        for c in self.calculations:
            status = c.getStatus()

            if status == 'completed':
                speciesNumCompleted.update(c.name)
                speciesCompletedTime[c.name] = speciesCompletedTime.get(c.name) + c.getCompletedTime()

            elif status == 'running':
                speciesNumRunning.update(c.name)
                speciesRunningTime[c.name] = speciesRunningTime.get(c.name) + c.getRunningTime()

        for c in self.calculations:
            c.check()

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

        if all(self.species.keys()):
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

    def run(self, test=False, force=False, serial=None, bashAliasesFile=None, notificationAlias=None):
        assert type(test) is bool
        assert type(force) is bool

        if serial is not None:
            assert type(serial) is bool

        if bashAliasesFile is not None:
            assert type(bashAliasesFile) is str

        if notificationAlias is not None:
            assert type(notificationAlias) is str

        if len(self.calculations) > 3 and not force:
            if test:
                print('*** WARNING: this is a lot of calculations to run at once - use force=True to ignore on real run ***')
                print('*** Continuing test... ***')
            else:
                raise MemoryError('Too many calculations to run at once - use force=True to ignore')

        if len(self.calculations) > 5:
            if test:
                print('*** WARNING: this is too many calculations ***')
                print('*** Continuing test... ***')
            else:
                raise MemoryError('No seriously - don\'t do this many calculations...')

        for calculation in self.calculations:
            calculation.run(test=test,
                            serial=serial,
                            bashAliasesFile=bashAliasesFile,
                            notificationAlias=notificationAlias)

        if test:
            print('*** Total of {} calculations to run - none have gone yet ***'.format(len(self.calculations)))
        else:
            print('*** Ran {} calculations ***'.format(len(self.calculations)))

    def sub(self, test=False, force=False, queueFile=None):
        assert type(test) is bool
        assert type(force) is bool

        if queueFile is not None:
            assert type(queueFile) is str

        for calculation in self.calculations:
            calculation.sub(test=test,
                            force=force,
                            queueFile=queueFile)

        if test:
            print('*** Total of {} calculations to submit - none have gone yet ***'.format(len(self.calculations)))
        else:
            print('*** Submitted {} calculations ***'.format(len(self.calculations)))

    def updateSettings(self, *settings):
        for calculation in self.calculations:
            calculation.updateSettings(*settings)
