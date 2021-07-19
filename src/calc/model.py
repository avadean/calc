from calc.cells import Cell
from calc.params import Param


class Model:
    def __init__(self, cells=None, params=None):
        if cells is not None:
            assert type(cells) is list
            assert all(type(cell) == Cell for cell in cells)

        if params is not None:
            assert type(params) is list
            assert all(type(param) == Param for param in params)

        self.cells = cells
        self.params = params

    def __str__(self):
        if self.params is None and self.cells is None:
            return 'Model -> *** empty ***'

        spaces = 15
        string = 'Model ->'

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