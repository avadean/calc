from calc.calculation import Calculation


class Model:
    name = None

    calculations = None

    def __init__(self, name=None, calculations=None):
        if name is not None:
            assert type(name) is str

        self.name = name

        if calculations is not None:
            assert type(calculations) is list
            assert all(type(calculation) == Calculation for calculation in calculations)

        self.calculations = calculations
