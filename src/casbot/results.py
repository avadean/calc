from casbot.data import elements,\
    getAllowedUnits, getNiceUnit, getFromDict,\
    PrintColors,\
    VectorInt, VectorFloat

from casbot.data import strListToArray

import numpy as np


resultKnown = ['hyperfine_dipolarbare', 'hyperfine_dipolaraug', 'hyperfine_dipolaraug2', 'hyperfine_dipolar',
               'hyperfine_fermi', 'hyperfine_total']

resultTypes = {'hyperfine_dipolarbare': np.ndarray,
               'hyperfine_dipolaraug': np.ndarray,
               'hyperfine_dipolaraug2': np.ndarray,
               'hyperfine_dipolar': np.ndarray,
               'hyperfine_fermi': np.ndarray,
               'hyperfine_total': np.ndarray}

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

                    tensor = NMRTensor(key=resultToGet, value=arr, unit='MHz', element=element, ion=ion)

                    tensors.append(tensor)

        if len(tensors) == 0:
            raise ValueError('Could not find any hyperfine dipolar bare tensors in results file')

        return tensors


    else:
        raise ValueError('Do not know how to get result {}'.format(resultToGet))




class Result:
    def __init__(self, key=None, value=None, unit=None):
        assert type(key) is str

        key = key.strip().lower()

        assert key in resultKnown, '{} not a known result'.format(key)

        self.key = key
        self.type = getFromDict(key=key, dct=resultTypes, strict=True)
        self.name = getFromDict(key=key, dct=resultNames, strict=True)

        if type(value) is int and self.type is float:
            value = float(value)

        if type(value) in [str, VectorInt] and self.type is VectorFloat:
            value = VectorFloat(vector=value)

        if type(value) in [list, tuple] and self.type is np.ndarray:
            value = np.array(value)

        assert type(value) is self.type, 'Value {} not acceptable for {}, should be {}'.format(value, self.key, self.type)

        # Quick basic checks on bool, other result types aren't checked
        if self.type is bool:
            assert value in [True, False], 'Value of {} not accepted for {}, should be True or False'.format(value, self.key)

        self.value = value

        if unit is not None:
            self.unitType = getFromDict(key=key, dct=resultUnits, strict=False, default=None)

            assert type(unit) is str

            unit = unit.strip().lower()

            assert unit in getAllowedUnits(self.unitType)

            unit = getNiceUnit(unit)

        self.unit = unit

    def __str__(self):
        if self.type is float:
            return '{:<12.4f}{}'.format(self.value, ' {}'.format(self.unit) if self.unit is not None else '')

        elif self.type is int:
            return '{:<3d}'.format(self.value)

        elif self.type is np.ndarray:
            return '   {:>12.5E}   {:>12.5E}   {:>12.5E}\n   {:>12.5E}   {:>12.5E}   {:>12.5E}\n   {:>12.5E}   {:>12.5E}   {:>12.5E}\n'.format(
                self.value[0][0], self.value[0][1], self.value[0][2],
                self.value[1][0], self.value[1][1], self.value[1][2],
                self.value[2][0], self.value[2][1], self.value[2][2])

        else:
            # Includes VectorInt and VectorFloat as well as strings
            return str(self.value)


class NMRTensor(Result):
    def __init__(self, key=None, value=None, unit=None, element=None, ion=None):
        super().__init__(key=key, value=value, unit=unit)

        assert np.shape(self.value) == (3, 3), 'NMR tensors should be dimension (3,3), not {}'.format(np.shape(self.value))

        assert type(element) is str

        element = element.lower()

        assert element in elements

        self.element = element[0].upper() + element[1:].lower()

        assert type(ion) is str
        assert ion.isdigit()

        self.ion = str(int(float(ion)))

        self.trace = np.trace(self.value)
        self.iso = self.trace / 3.0

        self.diag = np.diag(np.linalg.eigvals(self.value))

    def __str__(self, color='', showTensors=False):
        assert type(color) is str
        assert type(showTensors) is bool

        string = '  |->   {:<3s} {}{:^16}{} {:>11.5f}   <-|'.format(self.element + self.ion, color, self.name, PrintColors.reset, self.iso)

        if showTensors:
            string += '\n   {:>12.5E}   {:>12.5E}   {:>12.5E}\n   {:>12.5E}   {:>12.5E}   {:>12.5E}\n   {:>12.5E}   {:>12.5E}   {:>12.5E}'.format(*self.value.flatten())

        return string
