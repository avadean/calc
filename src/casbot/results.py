from casbot.data import getAllowedUnits, getNiceUnit, getFromDict,\
    Block, VectorInt, VectorFloat


resultKnown = []

resultTypes = {}

resultUnits = {}


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
            # Includes VectorInt, VectorFloat and TensorFloat as well as strings
            return str(self.value)

    def getLines(self, longestSetting=None):
        if longestSetting is not None:
            assert type(longestSetting) is int

        lines = ['{}{} : {} {}\n'.format(self.key,
                                         '' if longestSetting is None else ' ' * (longestSetting - len(self.key)),
                                         self.value,
                                         '' if self.unit is None else self.unit)]

        return lines
