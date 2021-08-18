from casbot.data import elements,\
    getAllowedUnits, getNiceUnit, getFromDict,\
    PrintColors,\
    strListToArray

from numpy import ndarray


resultKnown = ['hyperfine_dipolarbare', 'hyperfine_dipolaraug', 'hyperfine_dipolaraug2', 'hyperfine_dipolar',
               'hyperfine_fermi', 'hyperfine_total']

resultNames = {'hyperfine_dipolarbare': 'DIPOLAR BARE',
               'hyperfine_dipolaraug': 'DIPOLAR AUG',
               'hyperfine_dipolaraug2': 'DIPOLAR AUG2',
               'hyperfine_dipolar': 'DIPOLAR',
               'hyperfine_fermi': 'FERMI',
               'hyperfine_total': 'TOTAL'}

resultUnits = {'hyperfine_dipolarbare': 'energy',
               'hyperfine_dipolaraug': 'energy',
               'hyperfine_dipolaraug2': 'energy',
               'hyperfine_dipolar': 'energy',
               'hyperfine_fermi': 'energy',
               'hyperfine_total': 'energy'}



def getResult(resultToGet=None, lines=None):
    assert type(resultToGet) is str
    assert type(lines) is list
    assert all(type(line) is str for line in lines)

    resultToGet = resultToGet.strip().lower()

    assert resultToGet in resultKnown


    if resultToGet in ['hyperfine_dipolarbare', 'hyperfine_dipolaraug', 'hyperfine_dipolaraug2', 'hyperfine_dipolar',
                       'hyperfine_fermi', 'hyperfine_total']:

        wordToLookFor = {'hyperfine_dipolarbare': 'd_bare',
                         'hyperfine_dipolaraug': 'd_aug',
                         'hyperfine_dipolaraug2': 'd_aug2',
                         'hyperfine_dipolar': 'dipolar',
                         'hyperfine_fermi': 'fermi',
                         'hyperfine_total': 'total'}.get(resultToGet)

        tensors = []

        for num, line in enumerate(lines):
            parts = line.strip().lower().split()

            if len(parts) == 4:
                if parts[2] == wordToLookFor and parts[3] == 'tensor':
                    element = parts[0][0].upper() + parts[0][1:].lower()
                    ion = parts[1]

                    assert ion.isdigit(), 'Error in element ion on line {} of results file'.format(num)

                    arrLines = lines[num+2:num+5]

                    arr = strListToArray(arrLines)

                    tensor = NMR(key=resultToGet, value=arr, unit='MHz', element=element, ion=ion)

                    tensors.append(tensor)

        if len(tensors) == 0:
            raise ValueError('Could not find any hyperfine dipolar bare tensors in results file')

        return tensors


    else:
        raise ValueError('Do not know how to get result {}'.format(resultToGet))


def getUnit(key=None, unit=None):
    assert type(key) is str
    assert type(unit) is str

    unitType = getFromDict(key=key, dct=resultUnits, strict=True)

    unit = unit.strip().lower()

    assert unit in getAllowedUnits(unitType)

    unit = getNiceUnit(unit)

    return unit


class Result:
    def __init__(self, key=None):
        assert type(key) is str

        key = key.strip().lower()

        assert key in resultKnown, '{} not a known result'.format(key)

        self.key = key
        self.name = getFromDict(key=key, dct=resultNames, strict=True)


class Tensor(Result):
    def __init__(self, key=None, value=None, unit=None, shape=None):
        super().__init__(key=key)

        assert type(value) is ndarray, 'Value {} not acceptable for {}, should be {}'.format(value, self.key, ndarray)

        self.value = value
        self.unit = unit if unit is None else getUnit(key=key, unit=unit)

        assert type(shape) is tuple

        assert self.value.shape == shape, 'Tensor should be dimension {} not {}'.format(shape, self.value.shape)

        self.shape = self.value.shape
        self.size = self.value.size

        self.trace = self.value.trace()

    def __str__(self):
        return '  '.join('{:>12.5E}' for _ in range(self.size)).format(*self.value.flatten())


class NMR(Tensor):
    def __init__(self, key=None, value=None, unit=None, element=None, ion=None):
        super().__init__(key=key, value=value, unit=unit, shape=(3, 3))

        assert type(element) is str

        element = element.strip().lower()

        assert len(element) > 0
        assert element in elements

        self.element = element[0].upper() + element[1:].lower()

        assert type(ion) is str
        assert ion.isdigit()

        self.ion = str(int(float(ion)))

        self.iso = self.trace / 3.0

    def __str__(self, nameColor='', showTensor=False):
        assert type(nameColor) is str
        assert type(showTensor) is bool

        string = '  |->   {:<3s} {}{:^16}{} {:>11.5f}   <-|'.format(self.element + self.ion,
                                                                    nameColor,
                                                                    self.name,
                                                                    PrintColors.reset,
                                                                    self.iso)

        if showTensor:
            rows = 3 * '\n   {:>12.5E}   {:>12.5E}   {:>12.5E}'
            string += rows.format(*self.value.flatten())

        return string
