from calc.cells import Cell
from calc.params import Param

from itertools import product


def setupCalculations(*args):
    arguments = []
    numbering = []

    for arg in args:
        assert type(arg) in [str, list], 'Cannot have type {} for calculation setup'.format(type(arg))

        if type(arg) is str:
            arguments.append([arg])
            numbering.append([1])

        elif type(arg) is list:
            assert all(type(a) in [str, Cell, Param] for a in arg),\
                'Arguments for calculation setup must be string, cell or param'.format(type(arg))
            arguments.append(arg)
            numbering.append(list(range(1, len(arg)+1)))

    assert sum(any(type(a) is str for a in arg) for arg in arguments) == 1,\
        'Can only have one iterable argument that is not a cell or param'

    combinations = list(product(*arguments))
    numbering = list(product(*numbering))

    calculations = []
    for combNum, combination in enumerate(combinations):
        nums = numbering[combNum]
        name = None
        directory = '' # '{}'.format(get current working directory)
        cells = []
        params = []

        for settNum, setting in enumerate(combination):
            print(settNum, nums)
            n = nums[settNum]

            if type(setting) is str:
                name = setting
                directory += '{:03}_{}/'.format(n, name)

            elif type(setting) is Cell:
                cells.append(setting)
                directory += '{:03}_{}/'.format(n, setting.value)

            elif type(setting) is Param:
                params.append(setting)
                directory += '{:03}_{}/'.format(n, setting.value)

        calculations.append(Calculation(name=name,
                                        directory=directory,
                                        cells=cells,
                                        params=params))

    for calculation in calculations:
        print(calculation)



class Calculation:
    name = None
    directory = None
    cells = None
    params = None

    def __init__(self, name=None, directory=None,
                 cells=None, params=None):
        if name is not None:
            assert type(name) is str

        self.name = name

        if directory is not None:
            assert type(directory) is str

        self.directory = directory

        if cells is not None:
            assert type(cells) is list
            assert all(type(cell) == Cell for cell in cells)

        if params is not None:
            assert type(params) is list
            assert all(type(param) == Param for param in params)

        self.cells = cells
        self.params = params

    def __str__(self):
        string = 'Calculation ->'

        if self.name is not None:
            string += ' {}'.format(self.name)

        if self.directory is not None:
            string += ' ({})'.format(self.directory)

        if self.params is None and self.cells is None:
            string += '\n  *** empty ***'
            return string

        spaces = 15

        if self.cells is not None:
            string += '\n'

            for cell in self.cells:
                string += '  {key:>{spaces}} : {lines:<{spaces}}\n'.format(key=cell.key,
                                                                           spaces=spaces,
                                                                           lines=', '.join(cell.lines))

        if self.params is not None:
            string += '\n'

            for param in self.params:
                string += '  {key:>{spaces}} : {value:<{spaces}}\n'.format(key=param.key,
                                                                           spaces=spaces,
                                                                           value=param.value)

        return string