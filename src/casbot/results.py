#from casbot.data import getAllowedUnits, getNiceUnit, getFromDict,\
#    VectorInt, VectorFloat
from casbot.data import strListToArray

from numpy import ndarray


resultKnown = ['hyperfine_dipolarbare', 'hyperfine_dipolaraug', 'hyperfine_dipolaraug2', 'hyperfine_dipolar',
               'hyperfine_fermi', 'hyperfine_total']

resultTypes = {'hyperfine_dipolarbare': ndarray,
               'hyperfine_dipolaraug': ndarray,
               'hyperfine_dipolaraug2': ndarray,
               'hyperfine_dipolar': ndarray,
               'hyperfine_fermi': ndarray,
               'hyperfine_total': ndarray}

#resultUnits = {}



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
        tensors = {}

        for num, line in enumerate(lines):
            parts = line.strip().lower().split()

            if len(parts) == 4:
                if parts[2] == wordToLookFor and parts[3] == 'tensor':
                    element = parts[0][0].upper() + parts[0][1:].lower()
                    elementNum = parts[1]

                    assert elementNum.isdigit(), 'Error in digit on line {} of results file'.format(num)

                    tensor = strListToArray(lines[num+2:num+5])

                    tensors[element + elementNum] = tensor

        if len(tensors) == 0:
            raise ValueError('Could not find any hyperfine dipolar bare tensors in results file')

        return tensors



    else:
        raise ValueError('Do not know how to get result {}'.format(resultToGet))



'''
class Result:
    def __init__(self, key=None, value=None, unit=None):
        assert type(key) is str, 'Key for result should be a string'
        key = key.strip().lower()

        assert key in resultKnown, '{} not a known result'.format(key)

        self.key = key
        self.type = getFromDict(key, resultTypes)

        if type(value) is int and self.type is float:
            value = float(value)

        if type(value) is VectorInt and self.type is VectorFloat:
            value = VectorFloat(vector=value)

        assert type(value) is self.type, 'Value {} not acceptable for {}, should be {}'.format(value,
                                                                                               self.key,
                                                                                               self.type)

        # Quick basic check on bool, other result types aren't checked
        if self.type is bool:
            assert value in [True, False],\
                'Value of {} not accepted for {}, should be True or False'.format(value, self.key)

        self.value = value
        self.unit = unit

        if unit is not None:
            self.unitType = getFromDict(key=key, dct=resultUnits, strict=False, default=None)

            assert type(unit) is str

            unit = unit.strip().lower()

            assert unit in getAllowedUnits(self.unitType)

            self.unit = getNiceUnit(unit)

    def __str__(self):
        if self.type is float:
            return '{:<12.4f}{}'.format(self.value, ' {}'.format(self.unit) if self.unit is not None else '')

        elif self.type is int:
            return '{:<3d}'.format(self.value)

        else:
            # Includes VectorInt and VectorFloat as well as strings
            return str(self.value)

    def getLines(self, longestSetting=None):
        if longestSetting is not None:
            assert type(longestSetting) is int

        lines = ['{}{} : {} {}\n'.format(self.key,
                                         '' if longestSetting is None else ' ' * (longestSetting - len(self.key)),
                                         self.value,
                                         '' if self.unit is None else self.unit)]

        return lines
'''
