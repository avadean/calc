from calc.calculation import Calculation

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

    def run(self, force=False, test=False):
        assert type(force) is bool
        assert type(test) is bool

        if len(self.calculations) > 3 and not force:
            raise MemoryError('Too many calculations to run at once - use force=True to ignore')

        if len(self.calculations) > 5:
            raise MemoryError('No seriously - don\'t do this many calculations...')

        serial = False  # TODO: add this option
        bashAliasesFile = '/home/dean/.bash_aliases'  # TODO: move this somewhere better
        notificationAlias = 'noti'  # TODO: move this somewhere better

        if not Path(bashAliasesFile).is_file():
            raise FileNotFoundError('Cannot find alias file {}'.format(bashAliasesFile))

        for calculation in self.calculations:
            calculation.run(serial=serial,
                            bashAliasesFile=bashAliasesFile,
                            notificationAlias=notificationAlias,
                            test=test)

        if test:
            print('*** Total of {} calculations to run - none have gone yet! ***'.format(len(self.calculations)))
        else:
            print('*** Ran {} calculations ***'.format(len(self.calculations)))

    def sub(self, test=False):
        assert type(test) is bool

        queueFile = '/home/dean/tools/files/castep_queue.txt'  # TODO: move this somewhere better

        if not Path(queueFile).is_file():
            raise FileNotFoundError('Cannot find queue file {}'.format(queueFile))

        for calculation in self.calculations:
            calculation.sub(queueFile=queueFile,
                            test=test)

        if test:
            print('*** Total of {} calculations to submit - none have gone yet! ***'.format(len(self.calculations)))
        else:
            print('*** Submitted {} calculations ***'.format(len(self.calculations)))
