from casbot.data import elements,\
    getUnit, getFromDict,\
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

                    assert ion.isdigit(), f'Error in element ion on line {num} of results file'

                    arrLines = lines[num+2:num+5]

                    arr = strListToArray(arrLines)

                    tensor = NMR(key=resultToGet, value=arr, unit='MHz', element=element, ion=ion)

                    tensors.append(tensor)

        if len(tensors) == 0:
            raise ValueError(f'Could not find any {resultToGet} tensors in results file')

        return tensors


    else:
        raise ValueError(f'Do not know how to get result {resultToGet}')


class Result:
    def __init__(self, key=None):
        assert type(key) is str

        key = key.strip().lower()

        assert key in resultKnown, f'{key} not a known result'

        self.key = key
        self.name = getFromDict(key=key, dct=resultNames, strict=True)


class Tensor(Result):
    def __init__(self, key=None, value=None, unit=None, shape=None):
        super().__init__(key=key)

        assert type(value) is ndarray, f'Value {value} not acceptable for {self.key}, should be {ndarray}'

        self.value = value
        self.unit = unit if unit is None else getUnit(key=key, unit=unit, unitTypes=resultUnits, strict=True)

        assert type(shape) is tuple

        assert self.value.shape == shape, f'Tensor should be dimension {shape} not {self.value.shape}'

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

        string = f'  |->   {self.element+self.ion:<3s} {nameColor}{self.name:^16}{PrintColors.reset} {self.iso:>11.5f}   <-|'

        if showTensor:
            rows = 3 * '\n   {:>12.5E}   {:>12.5E}   {:>12.5E}'
            string += rows.format(*self.value.flatten())

        return string
