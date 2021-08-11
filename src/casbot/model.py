from casbot.calculation import Calculation

from pathlib import Path


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
        #print(self.getDirString())

    def __str__(self):
        string = ''

        for calculation in self.calculations:
            string += calculation.__str__() + '\n'

        string = string[:-1] # Remove last line break.

        return string

    def analyse(self, force=False):
        assert type(force) is bool

        if not force:
            assert all(c.getStatus() == 'completed' for c in self.calculations),\
                'Not all calculations have completed - use force=True to ignore'

        analysis = {c: c.analyse() if c.getStatus() == 'completed' else [] for c in self.calculations}

        return analysis

    def check(self):
        for calculation in self.calculations:
            calculation.check()

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
