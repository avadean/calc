from casbot.data import elements,\
    getUnit, getFromDict,\
    PrintColors,\
    strListToArray

from numpy import ndarray


resultKnown = ['hyperfine_dipolarbare', 'hyperfine_dipolaraug', 'hyperfine_dipolaraug2', 'hyperfine_dipolar',
               'hyperfine_fermi', 'hyperfine_total',

               'spin_density',

               'forces']

resultNames = {'hyperfine_dipolarbare': 'DIPOLAR BARE',
               'hyperfine_dipolaraug': 'DIPOLAR AUG',
               'hyperfine_dipolaraug2': 'DIPOLAR AUG2',
               'hyperfine_dipolar': 'DIPOLAR',
               'hyperfine_fermi': 'FERMI',
               'hyperfine_total': 'TOTAL',

               'spin_density': 'SPIN DENSITY',

               'forces': 'FORCES'}

resultUnits = {'hyperfine_dipolarbare': 'energy',
               'hyperfine_dipolaraug': 'energy',
               'hyperfine_dipolaraug2': 'energy',
               'hyperfine_dipolar': 'energy',
               'hyperfine_fermi': 'energy',
               'hyperfine_total': 'energy',

               'spin_density': 'spin',

               'forces': 'force'}



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

                    assert ion.isdigit(), f'Error in element ion on line {num+1} of results file'

                    arrLines = lines[num+2:num+5]

                    arr = strListToArray(arrLines)

                    tensor = NMR(key=resultToGet, value=arr, unit='MHz', element=element, ion=ion)

                    tensors.append(tensor)

        #if len(tensors) == 0:
        #    raise ValueError(f'Could not find any {resultToGet} tensors in results file')

        return tensors


    elif resultToGet == 'spin_density':
        hits = []

        for num, line in enumerate(lines):
            line = line.strip().lower()

            if 'integrated spin density' in line:
                parts = line.split('=')

                assert len(parts) == 2, f'Error in spin density on line {num+1} of results file'

                parts = parts[1].strip().split()

                assert len(parts) in [2, 4], f'Could not determine scalar or vector spin density on line {num+1} of results file'

                arr = strListToArray(parts[:-1])

                density = SpinDensity(key=resultToGet, value=arr, unit='hbar/2', shape=(len(parts)-1, 1))

                hits.append(density)

        #if len(hits) == 0:
        #    raise ValueError(f'Could not find any spin density values/vectors in result file')

        return None if len(hits) == 0 else hits[-1]


    elif resultToGet == 'forces':
        # Groups are groups of forces: one for each ion.
        # Hits are each individual force on each ion.
        groups = []
        hits = []

        for num, line in enumerate(lines):
            line = line.strip().lower()

            if 'Forces' in line and line.startswith('*') and line.endswith('*'):

                for numInBlock, lineInBlock in enumerate(lines[num:]):
                    if all(char == '*' for char in lineInBlock):
                        break
                    else:
                        parts = line.split()

                        if len(parts) == 5:
                            element, ion, x, y, z = parts

                            element = element[0].upper() + element[1:].lower()

                            assert ion.isdigit(), f'Error in element ion on line {numInBlock + 1} of results file'

                            vector = strListToArray([x, y, z])

                            force = Force(key=resultToGet, value=vector, unit='eV/Ang', element=element, ion=ion)

                            hits.append(force)
                else:
                    raise ValueError('Cannot find end of forces block in results file')

                groups.append(hits)

                hits = []

        #if len(hits) == 0:
        #   raise ValueError(f'Could not find any force vectors in result file')

        return None if len(groups) == 0 else groups[-1]


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


class Vector(Result):
    def __init__(self, key=None, value=None, unit=None, shape=None):
        super().__init__(key=key)

        assert type(value) is ndarray, f'Value {value} not acceptable for {self.key}, should be {ndarray}'

        self.value = value
        self.unit = unit if unit is None else getUnit(key=key, unit=unit, unitTypes=resultUnits, strict=True)

        assert type(shape) is tuple

        assert self.value.shape == shape, f'Array should be dimension {shape} not {self.value.shape}'

        self.shape = self.value.shape
        self.size = self.value.size

        self.norm = sum(v ** 2.0 for v in self.value) ** 0.5

    def __str__(self):
        return '   '.join('{:>12.5E}' for _ in range(self.size)).format(*self.value.flatten())


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

        string = f'    |->   {self.element+self.ion:<3s} {nameColor}{self.name:^16}{PrintColors.reset} {self.iso:>11.5f}   <-|'

        if showTensor:
            rows = 3 * '\n     {:>12.5E}   {:>12.5E}   {:>12.5E}'
            string += rows.format(*self.value.flatten())

        return string

    def __add__(self, other):
        assert self.key == other.key, 'Cannot add different NMR tensors'
        assert self.unit == other.unit, 'Cannot add tensors of different units'
        assert self.element == other.element, 'Cannot add tensors relating to different elements'
        assert self.ion == other.ion, 'Cannot add tensors relating to different ions'

        newValue = self.value + other.value

        return NMR(key=self.key,
                   value=newValue,
                   unit=self.unit,
                   element=self.element,
                   ion=self.ion)

    def __iadd__(self, other):
        self.__add__(other=other)

    def __sub__(self, other):
        assert self.key == other.key, 'Cannot sub different NMR tensors'
        assert self.unit == other.unit, 'Cannot sub tensors of different units'
        assert self.element == other.element, 'Cannot sub tensors relating to different elements'
        assert self.ion == other.ion, 'Cannot sub tensors relating to different ions'

        newValue = self.value - other.value

        return NMR(key=self.key,
                   value=newValue,
                   unit=self.unit,
                   element=self.element,
                   ion=self.ion)

    def __isub__(self, other):
        self.__sub__(other=other)

    def __eq__(self, other):
        return (self.value == other.value).all()


class SpinDensity(Vector):
    def __init__(self, key=None, value=None, unit=None, shape=None):
        super().__init__(key=key, value=value, unit=unit, shape=shape)


class Force(Vector):
    def __init__(self, key=None, value=None, unit=None, element=None, ion=None):
        super().__init__(key=key, value=value, unit=unit, shape=(3, 1))

        assert type(element) is str

        element = element.strip().lower()

        assert len(element) > 0
        assert element in elements

        self.element = element[0].upper() + element[1:].lower()

        assert type(ion) is str
        assert ion.isdigit()

        self.ion = str(int(float(ion)))

    def __str__(self):
        Fx, Fy, Fz = self.value

        return f'{self.element + self.ion:<3s}  {Fx:>12.5E}   {Fy:>12.5E}   {Fz:>12.5E}'
