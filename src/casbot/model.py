from casbot.calculation import Calculation

from pathlib import Path

class Model:
    name = None

    calculations = None

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

        print('*** Model created with {} calculation{} ***'.format(len(self.calculations),
                                                                   '' if len(self.calculations) == 1 else 's'))
        #print(self.getDirString())

    def __str__(self):
        string = ''

        for calculation in self.calculations:
            string += calculation.__str__() + '\n'

        string = string[:-1] # Remove last line break.

        return string

    def getDirString(self):
        if len(self.calculations) == 0:
            return ''

        string = ''

        for calculation in self.calculations:
            string += '{}\n'.format(calculation.directory)

        string = string[:-1]  # Remove last line break.

        return string

    def create(self, force=False):
        assert type(force) is bool

        if len(self.calculations) == 0:
            raise ValueError('No calculations to create')
        elif len(self.calculations) != 1 and any(calculation.directory is None for calculation in self.calculations):
            raise ValueError('Cannot create multiple calculations when (a) directory/ies is/are not supplied')

        if not force and any(Path(calculation.directory).exists() for calculation in self.calculations):
            raise FileExistsError('Some directories already exist - use force=True to overwrite')

        for calculation in self.calculations:
            calculation.create()

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

    def sub(self, test=False, queueFile=None):
        assert type(test) is bool

        if queueFile is not None:
            assert type(queueFile) is str

        for calculation in self.calculations:
            calculation.sub(test=test,
                            queueFile=queueFile)

        if test:
            print('*** Total of {} calculations to submit - none have gone yet ***'.format(len(self.calculations)))
        else:
            print('*** Submitted {} calculations ***'.format(len(self.calculations)))

    def updateSettings(self, *settings):
        for calculation in self.calculations:
            calculation.updateSettings(*settings)
