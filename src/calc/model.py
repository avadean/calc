from calc.calculation import Calculation

class Model:
    name = None

    calculations = None

    def __init__(self, calculations=None, name=None):
        if name is not None:
            assert type(name) is str

        self.name = name

        if calculations is not None:
            assert type(calculations) is list
            assert all(type(calculation) == Calculation for calculation in calculations)

        self.calculations = calculations

        print('*** Model created with {} calculations ***'.format(len(self.calculations)))
        print(self.getDirs())

    def __str__(self):
        string = ''

        for calculation in self.calculations:
            string += calculation.__str__() + '\n'

        string = string[:-1] # Remove last line break.

        return string

    def getDirs(self):
        if len(self.calculations) == 0:
            return ''

        string = ''

        for calculation in self.calculations:
            string += '{}\n'.format(calculation.directory)

        string = string[:-1]  # Remove last line break.

        return string

    def run(self):
        pass
