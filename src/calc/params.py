

class Params:
    task = 'singlepoint'
    magresTask = None
    magresMethod = None
    spectralTask = None

    xcFunctional = 'LDA'
    optStrategy = None
    cutOffEnergy = None
    fixOccupancy = None
    basisPrecision = None
    relativisticTreatment = None

    # etc ...

    def __init__(self):
        pass

    def __str__(self):
        attributes = [attr for attr in dir(self) if not attr.startswith('__') and
                      self.__getattribute__(attr) is not None]

        lengthLongestAttr = len(max(attributes))

        string = ''
        
        for attr in attributes:
            numSpaces = ' ' * (lengthLongestAttr - len(attr))
            value = self.__getattribute__(attr)
            string += '  {}{} : {}\n'.format(numSpaces, attr, value)

        return string
