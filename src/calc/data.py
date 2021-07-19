

def getNiceUnit(unit=None, strict=True):
    assert type(unit) is str
    assert type(strict) is bool

    unit = unit.lower()

    niceUnit = unitToNiceUnit.get(unit, None)

    if niceUnit is None and strict:
        raise ValueError('Unit {} does not have any nice units'.format(unit))

    return niceUnit


def getAllowedUnits(unitType=None, strict=True):
    assert type(unitType) is str
    assert type(strict) is bool

    unitList = unitTypeToUnit.get(unitType, None)

    if unitList is None and strict:
        raise ValueError('Unit type {} does not have any allowed units'.format(unitType))

    return unitList


unitToNiceUnit = { 'ev' : 'eV',
                   'ha' : 'Ha',
                   'j' : 'J',
                   'ry' : 'Ry'
                   }

unitToUnitType = { 'ev' : 'energy',
                   'ha' : 'energy',
                   'j' : 'energy',
                   'ry' : 'energy'
                   }

unitTypeToUnit = { 'energy' : ['ev', 'ha', 'j', 'ry']
                   }
