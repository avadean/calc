from casbot.data import assertBetween, assertCount,\
    elements,\
    getUnit, getFromDict,\
    stringToValue

from collections import Counter
from numpy import array, ndarray, dot, set_printoptions
from pathlib import Path

set_printoptions(precision=15)


def checkForUnit(lines=None, unitLine=0):
    assert type(lines) is list
    assert type(unitLine) is int

    try:
        potentialUnitLine = lines[unitLine]
    except IndexError:
        return None

    comment = potentialUnitLine.find('!')

    if comment != -1:
        potentialUnitLine = potentialUnitLine[:comment].strip()

    parts = potentialUnitLine.split()

    if len(parts) != 1:
        return None

    unit = parts[0]

    return unit


class Setting:
    def __init__(self, key=None):
        assert type(key) is str, 'Key for setting should be a string'
        key = key.strip().lower()

        # See if we can find the key in cells, then params, if not then we don't know what it is.
        if key in cellKnown:
            self.file = 'cell'
        elif key in paramKnown:
            self.file = 'param'
        else:
            raise ValueError(f'{key} not a known setting')

        self.key = key

        self.priority = getFromDict(key=key, dct=settingPriorities, strict=False, default=None)


class Keyword(Setting):
    def __init__(self, key=None):
        super().__init__(key=key)

        self.value = None
        self.unit = None


class BoolKeyword(Keyword):
    def __init__(self, key=None, value=None):
        super().__init__(key=key)

        assert value is True or value is False, f'Value of {value} not accepted for {self.key}, should be True or False'

        self.value = bool(value)

    def __str__(self):
        return str(self.value)


class StrKeyword(Keyword):
    def __init__(self, key=None, value=None):
        super().__init__(key=key)

        assert type(value) is str

        value = value.strip().lower()

        assert value in settingValues.get(self.key), f'Value of {value} not accepted for {self.key}, should be a float'

        self.value = getFromDict(key=value, dct=stringToNiceValue, strict=False, default=value)

    def __str__(self):
        return str(self.value)


class FloatKeyword(Keyword):
    def __init__(self, key=None, value=None, unit=None):
        super().__init__(key=key)

        assert type(value) in [float, int], f'Value of {value} not accepted for {self.key}, should be an int or float'

        if type(value) is int:
            value = float(value)

        minimum = min(settingValues.get(self.key))
        maximum = max(settingValues.get(self.key))
        assertBetween(value, minimum=minimum, maximum=maximum, key=self.key)

        self.value = value

        self.unit = unit if unit is None else getUnit(key=key, unit=unit, unitTypes=settingUnits, strict=True)

        # self.format TODO: add a format variable

    def __str__(self):
        unit = f' {self.unit}' if self.unit is not None else ''

        return f'{self.value:<12.4f}{unit}'


class IntKeyword(Keyword):
    def __init__(self, key=None, value=None, unit=None):
        super().__init__(key=key)

        assert type(value) is int, f'Value of {value} not accepted for {self.key}, should be an int'

        minimum = min(settingValues.get(self.key))
        maximum = max(settingValues.get(self.key))
        assertBetween(value, minimum=minimum, maximum=maximum, key=self.key)

        self.value = value

        self.unit = unit if unit is None else getUnit(key=key, unit=unit, unitTypes=settingUnits, strict=True)

        # self.format TODO: add a format variable

    def __str__(self):
        return f'{self.value:<3d}'


class VectorFloatKeyword(Keyword):
    def __init__(self, key=None, value=None, unit=None):
        super().__init__(key=key)

        try:
            value = array(value, dtype=float)
        except ValueError:
            raise ValueError(f'Value of {value} not accepted for {self.key}, should be a float array')

        minimum = min(settingValues.get(self.key))
        maximum = max(settingValues.get(self.key))
        assertBetween(*value, minimum=minimum, maximum=maximum, key=self.key)

        self.value = value

        self.unit = unit if unit is None else getUnit(key=key, unit=unit, unitTypes=settingUnits, strict=True)

        # self.format TODO: add a format variable

    def __str__(self):
        return str(self.value)


class VectorIntKeyword(Keyword):
    def __init__(self, key=None, value=None, unit=None):
        super().__init__(key=key)

        try:
            value = array(value, dtype=int)
        except ValueError:
            raise ValueError(f'Value of {value} not accepted for {self.key}, should be an int array')

        minimum = min(settingValues.get(self.key))
        maximum = max(settingValues.get(self.key))
        assertBetween(*value, minimum=minimum, maximum=maximum, key=self.key)

        self.value = value

        self.unit = unit if unit is None else getUnit(key=key, unit=unit, unitTypes=settingUnits, strict=True)

        # self.format TODO: add a format variable

    def __str__(self):
        return str(self.value)


class Block(Setting):
    def __init__(self, key=None, lines=None):
        super().__init__(key=key)

        self.lines = lines

        if lines is not None:
            assert type(lines) is list, 'Lines for block should be a list'
            assert all(type(line) is str for line in lines), 'Each line for the block should be a string'

            self.lines = []

            for line in lines:
                line = line.strip()

                if line:
                    # Check for comment.
                    comment = line.find('!')

                    # Remove it if need be.
                    if comment != -1:
                        line = line[:comment].strip()

                    self.lines.append(line)

    def __str__(self):
        return '; '.join(self.lines)

    def getLines(self):
        return self.lines


class ElementThreeVectorFloatBlock(Block):
    def __init__(self, key=None, lines=None):
        super().__init__(key=key, lines=lines)

        self.values = []
        self.unit = 'Ang' if self.key == 'positions_abs' else None  # TODO: add a default unit feature

        if self.lines:
            linesToRead = self.lines

            # Check for unit line
            potentialUnit = checkForUnit(lines=self.lines, unitLine=0)
            potentialUnit = potentialUnit if potentialUnit is None else getUnit(key=key, unit=potentialUnit,
                                                                                unitTypes=settingUnits, strict=True)

            if potentialUnit is not None:
                self.unit = potentialUnit
                linesToRead = linesToRead[1:]

            for line in linesToRead:
                parts = line.split()

                assert len(parts) > 0, f'Error in {key} on line {line}'

                element = parts[0].strip().lower()

                assert element in elements, f'Element {element} not known'

                element = element[0].upper() + element[1:].lower()

                try:
                    value = array(parts[1:], dtype=float)
                except ValueError:
                    raise ValueError(f'Error in {key} on line {line}')

                assert value.shape == (3,), f'Shape error in {key} on line {line}'

                self.values.append((element, value))

    def getLines(self):
        unitPart = [self.unit] if self.unit is not None else []
        return unitPart + [f'{element:<3s}  ' + '   '.join('{:>15.12f}' for _ in range(len(vector))).format(*vector) for (element, vector) in self.values]

    def findName(self):
        if not self.values:
            return None

        return ''.join([f'{element}{"" if num == 1 else num}' for element, num in Counter(list(zip(*self.values))[0]).items()])

    def rotate(self, rotationMatrix=None):
        assert type(rotationMatrix) is ndarray
        assert rotationMatrix.shape == (3, 3)

        self.values = [(element, dot(rotationMatrix, vector)) for element, vector in self.values]

    # TODO: consider fractional coordinates
    '''
    def translate(self, translationVector=None, fromUnit='ang'):
        assert type(translationVector) is ndarray
        assert translationVector.shape == (3,)

        assert type(fromUnit) is str

        fromUnit = fromUnit.strip().lower()

        assert fromUnit in getAllowedUnits(unitType='length', strict=True)

        toUnit = self.unit if self.unit is not None else 'ang'  # Default in castep is ang

        translationVector = unitConvert(fromUnit=fromUnit, toUnit=toUnit)

        self.values = {element: vector + translationVector for element, vector in self.values.items()}
    '''


class ThreeVectorFloatBlock(Block):
    def __init__(self, key=None, lines=None):
        super().__init__(key=key, lines=lines)

        self.values = []
        self.unit = 'Ang' if self.key == 'lattice_cart' else 'Tesla' if self.key == 'external_bfield' else None  # TODO: add a default unit feature

        if self.lines:
            linesToRead = self.lines

            # Check for unit line
            potentialUnit = checkForUnit(lines=self.lines, unitLine=0)
            potentialUnit = potentialUnit if potentialUnit is None else getUnit(key=key, unit=potentialUnit,
                                                                                unitTypes=settingUnits, strict=True)

            if potentialUnit is not None:
                self.unit = potentialUnit
                linesToRead = linesToRead[1:]

            for line in linesToRead:
                try:
                    value = array(line.split(), dtype=float)
                except ValueError:
                    raise ValueError(f'Error in {key} on line {line}')

                assert value.shape == (3,), f'Shape error in {key} on line {line}'

                self.values.append(value)

    def getLines(self):
        unitPart = [self.unit] if self.unit is not None else []
        return unitPart + ['  ' + '   '.join('{:>15.12f}' for _ in range(len(vector))).format(*vector) for vector in self.values]


class ThreeVectorFloatWeightedBlock(Block):
    def __init__(self, key=None, lines=None):
        super().__init__(key=key, lines=lines)

        self.values = []

        for line in self.lines:
            try:
                value = array(line.split(), dtype=float)
            except ValueError:
                raise ValueError(f'Error in {key} on line {line}')

            assert value.shape == (4,), f'Shape error in {key} on line {line}'

            self.values.append(value)

    def getLines(self):
        return ['   '.join('{:>4.2f}' for _ in range(len(vector))).format(*vector) for vector in self.values]


class ThreeVectorIntBlock(Block):
    def __init__(self, key=None, lines=None):
        super().__init__(key=key, lines=lines)

        self.values = []

        for line in self.lines:
            try:
                value = array(line.split(), dtype=int)
            except ValueError:
                raise ValueError(f'Error in {key} on line {line}')

            assert value.shape == (3,), f'Shape error in {key} on line {line}'

            self.values.append(value)

    def getLines(self):
        return ['  ' + '   '.join('{:>3d}' for _ in range(len(vector))).format(*vector) for vector in self.values]


class StrBlock(Block):
    def __init__(self, key=None, lines=None):
        super().__init__(key=key, lines=lines)

        self.values = self.lines


'''
class ElementStrBlock(Block):
    def __init__(self, key=None, lines=None):
        super().__init__(key=key, lines=lines)

        self.values = {}

        for line in self.lines:
            parts = line.split()

            assert len(parts) == 2, f'Error in {key} on line {line}'

            element, string = parts

            element = element.strip().lower()

            assert element in elements, f'Element {element} not known'

            element = element[0].upper() + element[1:].lower()

            self.values[element] = string

    def getLines(self):
        return [f'{element:<3s}  {string}' for element, string in self.values.items()]
'''



cellKnown = [
    # Lattice.
    'lattice_abc',
    'lattice_cart',

    # Positions.
    'positions_abs',
    'positions_frac',

    # Constraints.
    'cell_constraints',

    # Pseudopotentials.
    'species_pot',

    # Symmetry.
    'symmetry_ops',

    # Fields.
    'external_bfield',

    # Kpoints.
    'kpoint_list',
    'kpoints_list',
    'bs_kpoint_list',
    'bs_kpoints_list',
    'phonon_kpoint_list',
    'phonon_kpoints_list',
    'phonon_fine_kpoint_list',
    'optics_kpoint_list',
    'optics_kpoints_list',
    'magres_kpoint_list',
    'supercell_kpoint_list',
    'supercell_kpoints_list',
    'spectral_kpoint_list',
    'spectral_kpoints_list',

    # Keywords.
    'kpoint_mp_spacing',
    'kpoints_mp_spacing',
    'kpoint_mp_grid',
    'kpoints_mp_grid',
    'kpoint_mp_offset',
    'kpoints_mp_offset',
    'fix_all_cell',
    'fix_com',
    'symmetry_tol',
    'symmetry_generate'
]

cellPriorities = {
    # Lattice.
    'lattice_abc': 5.0,
    'lattice_cart': 10.0,

    # Positions.
    'positions_abs': 15.0,
    'positions_frac': 20.0,

    # Constraints.
    'cell_constraints': 25.0,

    # Pseudopotentials.
    'species_pot': 30.0,

    # Symmetry.
    'symmetry_ops': 35.0,

    # Fields.
    'external_bfield': 40.0,

    # Kpoints.
    'kpoint_list': 45.0,
    'kpoints_list': 45.0,
    'bs_kpoint_list': 50.0,
    'bs_kpoints_list': 50.0,
    'phonon_kpoint_list': 55.0,
    'phonon_kpoints_list': 55.0,
    'phonon_fine_kpoint_list': 60.0,
    'optics_kpoint_list': 65.0,
    'optics_kpoints_list': 65.0,
    'magres_kpoint_list': 70.0,
    'supercell_kpoint_list': 75.0,
    'supercell_kpoints_list': 75.0,
    'spectral_kpoint_list': 80.0,
    'spectral_kpoints_list': 80.0,

    # Keywords.
    'kpoint_mp_spacing': 100.1,
    'kpoints_mp_spacing': 100.1,
    'kpoint_mp_grid': 100.2,
    'kpoints_mp_grid': 100.2,
    'kpoint_mp_offset': 100.3,
    'kpoints_mp_offset': 100.3,
    'fix_all_cell': 105.1,
    'fix_com': 105.2,
    'symmetry_tol': 110.1,
    'symmetry_generate': 110.2,
}

# cellDefaults = {}

cellTypes = {
    # Lattice.
    'lattice_abc': ThreeVectorFloatBlock,
    'lattice_cart': ThreeVectorFloatBlock,

    # Positions.
    'positions_abs': ElementThreeVectorFloatBlock,
    'positions_frac': ElementThreeVectorFloatBlock,

    # Constraints.
    'cell_constraints': ThreeVectorIntBlock,

    # Pseudopotentials.
    'species_pot': StrBlock,

    # Symmetry.
    'symmetry_ops': ThreeVectorFloatBlock,

    # Fields.
    'external_bfield': ThreeVectorFloatBlock,

    # Kpoints.
    'kpoint_list': ThreeVectorFloatWeightedBlock,
    'kpoints_list': ThreeVectorFloatWeightedBlock,
    'bs_kpoint_list': ThreeVectorFloatBlock,
    'bs_kpoints_list': ThreeVectorFloatBlock,
    'phonon_kpoint_list': ThreeVectorFloatBlock,
    'phonon_kpoints_list': ThreeVectorFloatBlock,
    'phonon_fine_kpoint_list': ThreeVectorFloatBlock,
    'optics_kpoint_list': ThreeVectorFloatWeightedBlock,
    'optics_kpoints_list': ThreeVectorFloatWeightedBlock,
    'magres_kpoint_list': ThreeVectorFloatWeightedBlock,
    'supercell_kpoint_list': ThreeVectorFloatWeightedBlock,
    'supercell_kpoints_list': ThreeVectorFloatWeightedBlock,
    'spectral_kpoint_list': ThreeVectorFloatWeightedBlock,
    'spectral_kpoints_list': ThreeVectorFloatWeightedBlock,

    # Keywords.
    'kpoint_mp_spacing': FloatKeyword,
    'kpoints_mp_spacing': FloatKeyword,
    'kpoint_mp_grid': VectorIntKeyword,
    'kpoints_mp_grid': VectorIntKeyword,
    'kpoint_mp_offset': VectorFloatKeyword,
    'kpoints_mp_offset': VectorFloatKeyword,
    'fix_all_cell': BoolKeyword,
    'fix_com': BoolKeyword,
    'symmetry_tol': FloatKeyword,
    'symmetry_generate': BoolKeyword
}

cellValues = {
    'kpoint_mp_spacing': [0.0, float('inf')],
    'kpoints_mp_spacing': [0.0, float('inf')],
    'kpoint_mp_grid': [0, float('inf')],
    'kpoints_mp_grid': [0, float('inf')],
    'kpoint_mp_offset': [-float('inf'), float('inf')],
    'kpoints_mp_offset': [-float('inf'), float('inf')],
    'symmetry_tol': [0.0, float('inf')]
}

cellUnits = {
    'lattice_abc': 'length',
    'lattice_cart': 'length',

    'positions_abs': 'length',
    'positions_frac': 'length',

    'external_bfield': 'bfield',

    'kpoint_mp_spacing': 'inverselength',
    'kpoints_mp_spacing': 'inverselength',

    'symmetry_tol': 'length'
}


paramKnown = [  # task
    'task',
    'magres_task',
    'magres_method',
    'spectral_task',

    # general
    'xcfunctional',
    'opt_strategy',
    'cut_off_energy',
    'fix_occupancy',
    'basis_precision',
    'relativistic_treatment',

    # metals
    'smearing_width',
    'metals_method',
    'nextra_bands',

    # spin
    'spin',
    'spin_polarised',
    # 'spin_polarized',
    'spin_treatment',
    'spin_orbit_coupling',

    # bandstructure
    'bs_nbands',

    # phonons
    'phonon_method',
    'phonon_sum_rule',
    'phonon_fine_cutoff_method',

    # charge
    'charge',

    # calculate
    'calc_molecular_dipole',
    'popn_calculate',
    'calculate_raman',
    'calculate_densdiff',

    # write
    'write_cell_structure',
    'write_formatted_density',
    'popn_write',

    # units
    'dipole_unit',

    # miscellaneous.
    'max_scf_cycles',
    'num_dump_cycles',
    'elec_energy_tol',
    'bs_eigenvalue_tol',

    # extra
    'continuation',
    'iprint',
    'rand_seed',
    'comment',

    # blocks
    'devel_code'
]

paramPriorities = {  # task
    'task': 0.1,
    'magres_task': 0.2,
    'magres_method': 0.3,
    'spectral_task': 0.4,

    # general
    'xcfunctional': 1.1,
    'opt_strategy': 1.2,
    'cut_off_energy': 1.3,
    'fix_occupancy': 1.4,
    'basis_precision': 1.5,
    'relativistic_treatment': 1.6,

    # metals
    'smearing_width': 2.1,
    'metals_method': 2.2,
    'nextra_bands': 2.3,

    # spin
    'spin': 3.1,
    'spin_polarised': 3.2,
    # 'spin_polarized': 3.2,
    'spin_treatment': 3.3,
    'spin_orbit_coupling': 3.4,

    # bandstructure
    'bs_nbands': 4.1,

    # phonons
    'phonon_method': 5.1,
    'phonon_sum_rule': 5.2,
    'phonon_fine_cutoff_method': 5.3,

    # charge
    'charge': 6.1,

    # calculate
    'calc_molecular_dipole': 7.1,
    'popn_calculate': 7.2,
    'calculate_raman': 7.3,
    'calculate_densdiff': 7.4,

    # write
    'write_cell_structure': 8.1,
    'write_formatted_density': 8.2,
    'popn_write': 8.3,

    # units
    'dipole_unit': 9.1,

    # miscellaneous.
    'max_scf_cycles': 10.1,
    'num_dump_cycles': 10.2,
    'elec_energy_tol': 10.3,
    'bs_eigenvalue_tol': 10.4,

    # extra
    'continuation': 11.1,
    'iprint': 11.2,
    'rand_seed': 11.3,
    'comment': 11.4,

    # blocks
    'devel_code': 12.1
}

'''
paramDefaults = {
    # tasks
    'task': 'singlepoint',
    'magres_task': 'shielding',
    'magres_method': 'crystal',
    'spectral_task': 'bandstructure',

    # general
    'xcfunctional': 'lda',
    'opt_strategy': 'default',
    'cut_off_energy': 'set by basis_precision=fine',
    'fix_occupancy': 'false',
    'basis_precision': 'fine',
    'relativistic_treatment': 'koelling-harmon',

    # metals
    'smearing_width': '0.2 ev',
    'metals_method': 'dm',
    'nextra_bands': '0 if fix_occupancy else 4',

    # spin
    'spin': '0.0',
    'spin_polarised': 'true if spin > 0 else false',
    #'spin_polarized': 'true if spin > 0 else false',
    'spin_treatment': 'none',
    'spin_orbit_coupling': 'false',

    # bandstructure
    'bs_nbands': 'see castep --help bs_nbands',

    # phonons
    'phonon_method': 'set by phonon_fine_method',
    'phonon_sum_rule': 'false',
    'phonon_fine_cutoff_method': 'cumulant',

    # charge
    'charge': '0.0',

    # calculate
    'calc_molecular_dipole': 'false',
    'popn_calculate': 'true',
    'calculate_raman': 'false',
    'calculate_densdiff': 'false',

    # write
    'write_cell_structure': 'false',
    'write_formatted_density': 'false',
    'popn_write': 'enhanced',

    # units
    'dipole_unit': 'debye',

    # miscellaneous.
    'max_scf_cycles': '30',
    'num_dump_cycles': '0',
    'elec_energy_tol': '10^-5 eV for most tasks',
    'bs_eigenvalue_tol': '10^-6 eV/eig (10^-9 eV/eig if task=magres or phonon)',

    # extra
    'continuation': 'null',
    'iprint': '1',
    'rand_seed': 0,
    'comment': '(empty)'
}
'''

paramTypes = {
    # tasks
    'task': StrKeyword,
    'magres_task': StrKeyword,
    'magres_method': StrKeyword,
    'spectral_task': StrKeyword,

    # general
    'xcfunctional': StrKeyword,
    'opt_strategy': StrKeyword,
    'cut_off_energy': FloatKeyword,
    'fix_occupancy': BoolKeyword,
    'basis_precision': StrKeyword,
    'relativistic_treatment': StrKeyword,

    # metals
    'smearing_width': FloatKeyword,
    'metals_method': StrKeyword,
    'nextra_bands': IntKeyword,

    # spin
    'spin': FloatKeyword,
    'spin_polarised': BoolKeyword,
    # 'spin_polarized': BoolKeyword,
    'spin_treatment': StrKeyword,
    'spin_orbit_coupling': BoolKeyword,

    # bandstructure
    'bs_nbands': IntKeyword,

    # phonons
    'phonon_method': StrKeyword,
    'phonon_sum_rule': BoolKeyword,
    'phonon_fine_cutoff_method': StrKeyword,

    # charge
    'charge': FloatKeyword,

    # calculate
    'calc_molecular_dipole': BoolKeyword,
    'popn_calculate': BoolKeyword,
    'calculate_raman': BoolKeyword,
    'calculate_densdiff': BoolKeyword,

    # write
    'write_cell_structure': BoolKeyword,
    'write_formatted_density': BoolKeyword,
    'popn_write': BoolKeyword,

    # units
    'dipole_unit': StrKeyword,

    # miscellaneous.
    'max_scf_cycles': IntKeyword,
    'num_dump_cycles': IntKeyword,
    'elec_energy_tol': FloatKeyword,
    'bs_eigenvalue_tol': FloatKeyword,

    # extra
    'continuation': StrKeyword,
    'iprint': IntKeyword,
    'rand_seed': IntKeyword,
    'comment': StrKeyword,

    # blocks
    'devel_code': StrBlock
}

paramValues = {
    # tasks
    'task': ['singlepoint', 'bandstructure', 'geometryoptimisation', 'geometryoptimization', 'moleculardynamics', 'optics',
             'transitionstatesearch', 'phonon', 'efield', 'phonon+efield', 'thermodynamics', 'wannier', 'magres', 'elnes',
             'spectral', 'epcoupling', 'geneticalgor'],
    'magres_task': ['shielding', 'efg', 'nmr', 'gtensor', 'hyperfine', 'epr', 'jcoupling'],
    'magres_method': ['crystal', 'molecular', 'molecular3'],
    'spectral_task': ['bandstructure', 'dos', 'optics', 'coreloss', 'all'],

    # general
    'xcfunctional': ['lda', 'pw91', 'pbe', 'pbesol', 'rpbe', 'wc', 'blyp', 'lda-c', 'lda-x', 'zero', 'hf', 'pbe0', 'b3lyp',
                     'hse03', 'hse06', 'exx-x', 'hf-lda', 'exx', 'exx-lda', 'shf', 'sx', 'shf-lda', 'sx-lda', 'wda', 'sex',
                     'sex-lda', 'rscan'],
    'opt_strategy': ['default', 'speed', 'memory'],
    'cut_off_energy': [0.0, float('inf')],
    'basis_precision': ['null', 'coarse', 'medium', 'fine', 'precise', 'extreme'],
    'relativistic_treatment': ['koelling-harmon', 'schroedinger', 'zora', 'dirac'],

    # metals
    'smearing_width': [0.0, float('inf')],
    'metals_method': ['none', 'dm', 'edft'],
    'nextra_bands': [0.0, float('inf')],

    # spin
    'spin': [-float('inf'), float('inf')],
    'spin_treatment': ['none', 'scalar', 'vector'],

    # bandstructure
    'bs_nbands': [0, float('inf')],

    # phonons
    'phonon_method': ['dfpt', 'linearresponse', 'finitedisplacement'],
    'phonon_fine_cutoff_method': ['cumulant', 'spherical'],

    # charge
    'charge': [-float('inf'), float('inf')],

    # miscellaneous.
    'max_scf_cycles': [0, float('inf')],
    'num_dump_cycles': [0, float('inf')],
    'elec_energy_tol': [0.0, float('inf')],
    'bs_eigenvalue_tol': [0.0, float('inf')],

    # extra
    'iprint': [1, 2, 3],
    'rand_seed': [-float('inf'), float('inf')],
}

paramUnits = {
    # general
    'cut_off_energy': 'energy',

    # metals
    'smearing_width': 'energy',

    # miscellaneous.
    'elec_energy_tol': 'energy',
    'bs_eigenvalue_tol': 'energy',
}


stringToNiceValue = {
    'lda': 'LDA',
    'pw91': 'PW91',
    'pbe': 'PBE',
    'pbesol': 'PBEsol',
    'rpbe': 'rPBE',
    'wc': 'WC',
    'blyp': 'BLYP',
    'lda-c': 'LDA-c',
    'lda-x': 'LDA-x',
    'zero': 'ZERO',
    'hf': 'HF',
    'pbe0': 'PBE0',
    'b3lyp': 'B3LYP',
    'hse03': 'HSE03',
    'hse06': 'HSE06',
    'exx-x': 'EXX-x',
    'hf-lda': 'HF-LDA',
    'exx': 'EXX',
    'exx-lda': 'EXX-LDA',
    'shf': 'SHF',
    'sx': 'SX',
    'shf-lda': 'SHF-LDA',
    'sx-lda': 'SX-LDA',
    'wda': 'WDA',
    'sex': 'SEX',
    'sex-lda': 'SEX-LDA',
    'rscan': 'rSCAN'
}



settingKnown = cellKnown + paramKnown
settingPriorities = cellPriorities | paramPriorities
settingTypes = cellTypes | paramTypes
settingValues = cellValues | paramValues
settingUnits = cellUnits | paramUnits

shortcutToCells = {'usp': StrBlock(key='species_pot', lines=[]),
                   'ncp': StrBlock(key='species_pot', lines=['NCP']),
                   'c19': StrBlock(key='species_pot', lines=['C19']),
                   'soc19': StrBlock(key='species_pot', lines=['SOC19']),

                   'h': [ThreeVectorFloatBlock(key='lattice_cart', lines=[' BOHR',
                                                                          '  10.0   0.0   0.0',
                                                                          '   0.0  10.0   0.0',
                                                                          '   0.0   0.0  10.0']),

                         ElementThreeVectorFloatBlock(key='positions_abs', lines=['H   0.0  0.0  0.0']),

                         ThreeVectorFloatWeightedBlock(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])],

                   'ch4distorted': [ThreeVectorFloatBlock(key='lattice_cart', lines=[' ANG',
                                                                                     '  10.0   0.0   0.0',
                                                                                     '   0.0  10.0   0.0',
                                                                                     '   0.0   0.0  10.0']),

                                    ElementThreeVectorFloatBlock(key='positions_abs', lines=['C    0.10000  -0.20000  -0.10000',
                                                                                             'H    1.18913   1.18913   1.18913',
                                                                                             'H   -1.18913  -1.18913   1.18913',
                                                                                             'H   -1.18913   1.48913  -1.18913',
                                                                                             'H    1.28913  -1.18913  -1.18913']),

                                    ThreeVectorFloatWeightedBlock(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])],

                   'ch3': [ThreeVectorFloatBlock(key='lattice_cart', lines=['BOHR',
                                                                            '  10.0   0.0   0.0',
                                                                            '   0.0  10.0   0.0',
                                                                            '   0.0   0.0  10.0']),

                           ElementThreeVectorFloatBlock(key='positions_abs', lines=['ANG',
                                                                                    'C   0.000000000  0.000000000  0.000000000',
                                                                                    'H   1.079000000  0.000000000  0.000000000',
                                                                                    'H  -0.539500000  0.934441411  0.000000000',
                                                                                    'H  -0.539500000 -0.934441411  0.000000000']),

                           ThreeVectorFloatWeightedBlock(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])],

                   'gao': [ThreeVectorFloatBlock(key='lattice_cart', lines=[' ANG',
                                                                            '  12.0   0.0   0.0',
                                                                            '   0.0  12.0   0.0',
                                                                            '   0.0   0.0  12.0']),

                           ElementThreeVectorFloatBlock(key='positions_abs',
                                                        lines=['Ang',
                                                               ' Ga  0.000  0.000  0.000',
                                                               '  O  0.000  0.000  1.744']),

                           ThreeVectorFloatWeightedBlock(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])],

                   'hf': [ThreeVectorFloatBlock(key='lattice_cart', lines=[' ANG',
                                                                           '  10.0   0.0   0.0',
                                                                           '   0.0  10.0   0.0',
                                                                           '   0.0   0.0  10.0']),

                          #ElementThreeVectorFloatBlock(key='positions_frac',
                          #                             lines=['  H   0.1   0.1   0.099380480724825',
                          #                                    '  F   0.1   0.1   0.192319519275175']),

                          ElementThreeVectorFloatBlock(key='positions_abs',
                                                       lines=['  H   0.000000000000000   0.000000000000000   0.0000000000000000',
                                                              '  F   0.000000000000000   0.000000000000000   0.9293903855034999']),

                          ThreeVectorFloatWeightedBlock(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])],

                   'hcl': [ThreeVectorFloatBlock(key='lattice_cart', lines=[' ANG',
                                                                            '  10.0   0.0   0.0',
                                                                            '   0.0  10.0   0.0',
                                                                            '   0.0   0.0  10.0']),

                           #ElementThreeVectorFloatBlock(key='positions_frac',
                           #                             lines=['  H    0.009999871806914   0.009999872045901   0.009226072370290',
                           #                                    '  Cl   0.010000128193086   0.010000127954099   0.138173927629710']),

                           ElementThreeVectorFloatBlock(key='positions_abs',
                                                        lines=['  H   0.000000000000000   0.000000000000000   0.0000000000000000',
                                                               '  Cl  0.000000000000000   0.000000000000000   1.2894785525992882']),

                           ThreeVectorFloatWeightedBlock(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])],

                   'hbr': [ThreeVectorFloatBlock(key='lattice_cart', lines=[' ANG',
                                                                            '  12.0   0.0   0.0',
                                                                            '   0.0  12.0   0.0',
                                                                            '   0.0   0.0  12.0']),

                           #ElementThreeVectorFloatBlock(key='positions_frac',
                           #                             lines=['  H    -0.000002946190640  -0.000003049675148   0.011117199951347',
                           #                                    '  Br    0.000002946190640   0.000003049675148   0.130282800048653']),

                           ElementThreeVectorFloatBlock(key='positions_abs',
                                                        lines=['  H   0.000000000000000   0.000000000000000   0.0000000000000000',
                                                               '  Br  0.000000000000000   0.000000000000000   1.4299872047889637']),

                           ThreeVectorFloatWeightedBlock(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])],

                   'hi': [ThreeVectorFloatBlock(key='lattice_cart', lines=[' ANG',
                                                                           '  12.0   0.0   0.0',
                                                                           '   0.0  12.0   0.0',
                                                                           '   0.0   0.0  12.0']),

                          #ElementThreeVectorFloatBlock(key='positions_frac',
                          #                             lines=['  H   0.000000000013618   0.000000000163156  -0.000952894767401',
                          #                                    '  I  -0.000000000013618  -0.000000000163156   0.135036228100734']),

                          ElementThreeVectorFloatBlock(key='positions_abs',
                                                       lines=['  H   0.000000000000000   0.000000000000000   0.0000000000000000',
                                                              '  I   0.000000000000000   0.000000000000000   1.6318694744176200']),

                          ThreeVectorFloatWeightedBlock(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])],

                   'hfrot': [ThreeVectorFloatBlock(key='lattice_cart', lines=[' ANG',
                                                                              '  10.0   0.0   0.0',
                                                                              '   0.0  10.0   0.0',
                                                                              '   0.0   0.0  10.0']),

                             ElementThreeVectorFloatBlock(key='positions_frac',
                                                          # lines=['  H   0.12040092  0.12040092 -0.02972739',
                                                          #       '  F   0.16687044  0.16687044  0.03599044']),
                                                          lines=['H         0.120400920000000  0.120400920000000 -0.029727390000000',
                                                                 'F         0.166870440000000  0.166870440000000  0.035990440000000']),

                             ThreeVectorFloatWeightedBlock(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])],

                   'hclrot': [ThreeVectorFloatBlock(key='lattice_cart', lines=[' ANG',
                                                                               '  10.0   0.0   0.0',
                                                                               '   0.0  10.0   0.0',
                                                                               '   0.0   0.0  10.0']),

                              ElementThreeVectorFloatBlock(key='positions_frac',
                                                           # lines=['  H    0.01168401  0.01168401 -0.00347605',
                                                           #       '  Cl   0.07615812  0.07615812  0.08770359']),
                                                           lines=['H         0.011684010000000  0.011684010000000 -0.003476050000000',
                                                                  'Cl        0.076158120000000  0.076158120000000  0.087703590000000']),

                              ThreeVectorFloatWeightedBlock(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])],

                   'hbrrot': [ThreeVectorFloatBlock(key='lattice_cart', lines=[' ANG',
                                                                               '  12.0   0.0   0.0',
                                                                               '   0.0  12.0   0.0',
                                                                               '   0.0   0.0  12.0']),

                              ElementThreeVectorFloatBlock(key='positions_frac',
                                                           # lines=['  H    0.00555653 0.00555643 0.00786405',
                                                           #       '  Br   0.06514347 0.06514357 0.09212085']),
                                                           lines=['H         0.005556530000000  0.005556430000000  0.007864050000000',
                                                                  'Br        0.065143470000000  0.065143570000000  0.092120850000000']),

                              ThreeVectorFloatWeightedBlock(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])],

                   'hirot': [ThreeVectorFloatBlock(key='lattice_cart', lines=[' ANG',
                                                                              '  12.0   0.0   0.0',
                                                                              '   0.0  12.0   0.0',
                                                                              '   0.0   0.0  12.0']),

                             ElementThreeVectorFloatBlock(key='positions_frac',
                                                          # lines=['  H   -0.00047645 -0.00047645 -0.0006738',
                                                          #       '  I    0.06751811  0.06751811  0.09548503']),
                                                          lines=['H        -0.000476450000000 -0.000476450000000 -0.000673800000000',
                                                                 'I         0.067518110000000  0.067518110000000  0.095485030000000']),

                             ThreeVectorFloatWeightedBlock(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])],

                   'hftrans': [ThreeVectorFloatBlock(key='lattice_cart', lines=[' ANG',
                                                                                '  10.0   0.0   0.0',
                                                                                '   0.0  10.0   0.0',
                                                                                '   0.0   0.0  10.0']),

                               ElementThreeVectorFloatBlock(key='positions_frac',
                                                            lines=['  H   1.1   -1.1   2.099380480724825',
                                                                   '  F   1.1   -1.1   2.192319519275175']),

                               ThreeVectorFloatWeightedBlock(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])],

                   'hcltrans': [ThreeVectorFloatBlock(key='lattice_cart', lines=[' ANG',
                                                                                 '  10.0   0.0   0.0',
                                                                                 '   0.0  10.0   0.0',
                                                                                 '   0.0   0.0  10.0']),

                                ElementThreeVectorFloatBlock(key='positions_frac',
                                                             lines=['  H    1.009999871806914  -1.009999872045901   2.009226072370290',
                                                                    '  Cl   1.010000128193086  -1.010000127954099   2.138173927629710']),

                                ThreeVectorFloatWeightedBlock(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])],

                   'hbrtrans': [ThreeVectorFloatBlock(key='lattice_cart', lines=[' ANG',
                                                                                 '  12.0   0.0   0.0',
                                                                                 '   0.0  12.0   0.0',
                                                                                 '   0.0   0.0  12.0']),

                                ElementThreeVectorFloatBlock(key='positions_frac',
                                                             lines=['  H     0.999997053809360  -1.000003049675148   2.011117199951347',
                                                                    '  Br    1.000002946190640  -0.999996950324852   2.130282800048653']),

                                ThreeVectorFloatWeightedBlock(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])],

                   'hitrans': [ThreeVectorFloatBlock(key='lattice_cart', lines=[' ANG',
                                                                                '  12.0   0.0   0.0',
                                                                                '   0.0  12.0   0.0',
                                                                                '   0.0   0.0  12.0']),

                               ElementThreeVectorFloatBlock(key='positions_frac',
                                                            lines=['  H   1.000000000013618  -0.999999999836844   1.999047105232599',
                                                                   '  I   0.999999999986382  -1.000000000163156   2.135036228100734']),

                               ThreeVectorFloatWeightedBlock(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])],

                   }

shortcutToCellsAliases = {}

shortcutToParams = {'singlepoint': StrKeyword(key='task', value='singlepoint'),
                    'geometryoptimisation': StrKeyword(key='task', value='geometryoptimisation'),

                    'lda': StrKeyword(key='xcfunctional', value='lda'),
                    'pbe': StrKeyword(key='xcfunctional', value='pbe'),
                    'pw91': StrKeyword(key='xcfunctional', value='pw91'),
                    'b3lyp': StrKeyword(key='xcfunctional', value='b3lyp'),

                    'lowcutoff': FloatKeyword(key='cut_off_energy', value=300.0, unit='eV'),
                    'normalcutoff': FloatKeyword(key='cut_off_energy', value=500.0, unit='eV'),
                    'cutoff': FloatKeyword(key='cut_off_energy', value=700.0, unit='eV'),
                    'highcutoff': FloatKeyword(key='cut_off_energy', value=900.0, unit='eV'),

                    'schroedinger': StrKeyword(key='relativistic_treatment', value='schroedinger'),
                    'dirac': StrKeyword(key='relativistic_treatment', value='dirac'),

                    'spinpolarised': BoolKeyword(key='spin_polarised', value=True),

                    'efg': [StrKeyword(key='task', value='magres'),
                            StrKeyword(key='magres_task', value='efg')],

                    'shielding': [StrKeyword(key='task', value='magres'),
                                  StrKeyword(key='magres_task', value='shielding')],

                    'nmr': [StrKeyword(key='task', value='magres'),
                            StrKeyword(key='magres_task', value='nmr')],

                    'hyperfine': [StrKeyword(key='task', value='magres'),
                                  StrKeyword(key='magres_task', value='hyperfine')],

                    # 'jcoupling': (!) NotImplementedError,

                    'soc': [BoolKeyword(key='spin_polarised', value=True),
                            StrKeyword(key='spin_treatment', value='vector'),
                            BoolKeyword(key='spin_orbit_coupling', value=True),
                            StrBlock(key='species_pot', lines=['SOC19'])],

                    'writecell': BoolKeyword(key='write_cell_structure', value=True),

                    'iprint': IntKeyword(key='iprint', value=3),

                    'xdensity': StrBlock('devel_code', lines=['density_in_x=true']),
                    'ydensity': StrBlock('devel_code', lines=['density_in_y=true']),
                    'zdensity': StrBlock('devel_code', lines=['density_in_z=true'])
                    }

shortcutToParamsAliases = {'geom': [shortcutToParams.get('geometryoptimisation'),
                                    shortcutToParams.get('writecell')],
                           'geometry': [shortcutToParams.get('geometryoptimisation'),
                                        shortcutToParams.get('writecell')],
                           'optimise': [shortcutToParams.get('geometryoptimisation'),
                                        shortcutToParams.get('writecell')],
                           'optimize': [shortcutToParams.get('geometryoptimisation'),
                                        shortcutToParams.get('writecell')],
                           'optimisation': [shortcutToParams.get('geometryoptimisation'),
                                            shortcutToParams.get('writecell')],
                           'optimization': [shortcutToParams.get('geometryoptimisation'),
                                            shortcutToParams.get('writecell')],
                           'geometryoptimization': [shortcutToParams.get('geometryoptimisation'),
                                                    shortcutToParams.get('writecell')],

                           'averagecutoff': shortcutToParams.get('normalcutoff'),
                           'middlecutoff': shortcutToParams.get('normalcutoff'),
                           'mediumcutoff': shortcutToParams.get('normalcutoff'),

                           'schrod': shortcutToParams.get('schroedinger'),
                           'schrodinger': shortcutToParams.get('schroedinger'),
                           'schroed': shortcutToParams.get('schroedinger'),

                           'polarised': shortcutToParams.get('spinpolarised'),
                           'polarized': shortcutToParams.get('spinpolarised'),
                           'spinpolarized': shortcutToParams.get('spinpolarised'),
                           'spin_polarised': shortcutToParams.get('spinpolarised'),
                           'spin_polarized': shortcutToParams.get('spinpolarised'),

                           'writestructure': shortcutToParams.get('writecell')
                           }

stringToVariableSettings = {'soc': [(StrKeyword(key='spin_treatment', value='scalar'), BoolKeyword(key='spin_orbit_coupling', value=False)),
                                    (StrKeyword(key='spin_treatment', value='vector'), BoolKeyword(key='spin_orbit_coupling', value=False)),
                                    (StrKeyword(key='spin_treatment', value='vector'), BoolKeyword(key='spin_orbit_coupling', value=True))],

                            'density': [StrBlock(key='devel_code', lines=['density_in_x=true']),
                                        StrBlock(key='devel_code', lines=['density_in_y=true']),
                                        StrBlock(key='devel_code', lines=['density_in_z=true'])],

                            'bfielddensity': [(StrBlock(key='devel_code', lines=['density_in_x=true']), ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '500.0 0.0 0.0'])),
                                              (StrBlock(key='devel_code', lines=['density_in_y=true']), ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 500.0 0.0'])),
                                              (StrBlock(key='devel_code', lines=['density_in_z=true']), ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 500.0']))],

                            'socdensity': [(StrKeyword(key='spin_treatment', value='scalar'), BoolKeyword(key='spin_orbit_coupling', value=False)),

                                           (StrKeyword(key='spin_treatment', value='vector'), BoolKeyword(key='spin_orbit_coupling', value=False)),

                                           (StrKeyword(key='spin_treatment', value='vector'), BoolKeyword(key='spin_orbit_coupling', value=True),
                                            StrBlock(key='devel_code', lines=['density_in_x=true'])),

                                           (StrKeyword(key='spin_treatment', value='vector'), BoolKeyword(key='spin_orbit_coupling', value=True),
                                            StrBlock(key='devel_code', lines=['density_in_y=true'])),

                                           (StrKeyword(key='spin_treatment', value='vector'), BoolKeyword(key='spin_orbit_coupling', value=True),
                                            StrBlock(key='devel_code', lines=['density_in_z=true']))],

                            'hyperfinebfield': [(StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '1.0 0.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 1.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 1.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '2.0 0.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 2.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 2.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '3.0 0.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 3.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 3.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '4.0 0.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 4.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 4.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '5.0 0.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 5.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 5.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '6.0 0.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 6.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 6.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '7.0 0.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 7.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 7.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '8.0 0.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 8.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 8.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '9.0 0.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 9.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 9.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '10.0 0.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 10.0 0.0'])),

                                                (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                 ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 10.0']))
                                                ],

                            'hyperfinetensbfield': [(StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '10.0 0.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 10.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 10.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '20.0 0.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 20.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 20.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '30.0 0.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 30.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 30.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '40.0 0.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 40.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 40.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '50.0 0.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 50.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 50.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '60.0 0.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 60.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 60.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '70.0 0.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 70.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 70.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '80.0 0.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 80.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 80.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '90.0 0.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 90.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 90.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '100.0 0.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 100.0 0.0'])),

                                                    (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                     ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 100.0']))
                                                    ],

                            'hyperfinehundredsbfield': [(StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '100.0 0.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 100.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 100.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '200.0 0.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 200.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 200.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '300.0 0.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 300.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 300.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '400.0 0.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 400.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 400.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '500.0 0.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 500.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 500.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '600.0 0.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 600.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 600.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '700.0 0.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 700.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 700.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '800.0 0.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 800.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 800.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '900.0 0.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 900.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 900.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '1000.0 0.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 1000.0 0.0'])),

                                                        (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                         ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 1000.0']))
                                                        ],

                            'hyperfinekilosbfield': [(StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '1000.0 0.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 1000.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 1000.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '2000.0 0.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 2000.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 2000.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '3000.0 0.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 3000.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 3000.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '4000.0 0.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 4000.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 4000.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '5000.0 0.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 5000.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 5000.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '6000.0 0.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 6000.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 6000.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '7000.0 0.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 7000.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 7000.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '8000.0 0.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 8000.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 8000.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '9000.0 0.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 9000.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 9000.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_x=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '10000.0 0.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_y=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 10000.0 0.0'])),

                                                     (StrBlock(key='devel_code', lines=['density_in_z=true']),
                                                      ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0 0.0 10000.0']))
                                                     ],

                            'xbfield': [ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 0.0  0.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 1.0  0.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 2.0  0.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 3.0  0.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 4.0  0.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 5.0  0.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 6.0  0.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 7.0  0.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 8.0  0.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 9.0  0.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '10.0  0.0   0.0'])],

                            'ybfield': [ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   1.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   2.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   3.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   4.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   5.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   6.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   7.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   8.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   9.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0  10.0   0.0'])],

                            'zbfield': [ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   0.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   1.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   2.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   3.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   4.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   5.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   6.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   7.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   8.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   9.0']),
                                        ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0  10.0'])],

                            'tensxbfield': [ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 0.0   0.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 10.0  0.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 20.0  0.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 30.0  0.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 40.0  0.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 50.0  0.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 60.0  0.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 70.0  0.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 80.0  0.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 90.0  0.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '100.0  0.0   0.0'])],

                            'tensybfield': [ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0    0.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   10.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   20.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   30.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   40.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   50.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   60.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   70.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   80.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   90.0   0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0  100.0   0.0'])],

                            'tenszbfield': [ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0    0.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   10.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   20.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   30.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   40.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   50.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   60.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   70.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   80.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   90.0']),
                                            ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0  100.0'])],

                            'hundredsxbfield': [ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 0.0   0.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 100.0  0.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 200.0  0.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 300.0  0.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 400.0  0.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 500.0  0.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 600.0  0.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 700.0  0.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 800.0  0.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 900.0  0.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '1000.0  0.0   0.0'])],

                            'hundredsybfield': [ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0    0.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   100.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   200.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   300.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   400.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   500.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   600.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   700.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   800.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   900.0   0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0  1000.0   0.0'])],

                            'hundredszbfield': [ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0    0.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   100.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   200.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   300.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   400.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   500.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   600.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   700.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   800.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   900.0']),
                                                ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0  1000.0'])],

                            'kilosxbfield': [ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 0.0   0.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 1000.0  0.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 2000.0  0.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 3000.0  0.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 4000.0  0.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 5000.0  0.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 6000.0  0.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 7000.0  0.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 8000.0  0.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', ' 9000.0  0.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '10000.0  0.0   0.0'])],

                            'kilosybfield': [ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0    0.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   1000.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   2000.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   3000.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   4000.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   5000.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   6000.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   7000.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   8000.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   9000.0   0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0  10000.0   0.0'])],

                            'kiloszbfield': [ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0    0.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   1000.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   2000.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   3000.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   4000.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   5000.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   6000.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   7000.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   8000.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0   9000.0']),
                                             ThreeVectorFloatBlock(key='external_bfield', lines=['TESLA', '0.0   0.0  10000.0'])],

                            'halides': [shortcutToCells.get('hf'),
                                        shortcutToCells.get('hcl'),
                                        shortcutToCells.get('hbr'),
                                        shortcutToCells.get('hi')],

                            'halidesrot': [shortcutToCells.get('hfrot'),
                                           shortcutToCells.get('hclrot'),
                                           shortcutToCells.get('hbrrot'),
                                           shortcutToCells.get('hirot')],

                            'halidestrans': [shortcutToCells.get('hftrans'),
                                             shortcutToCells.get('hcltrans'),
                                             shortcutToCells.get('hbrtrans'),
                                             shortcutToCells.get('hitrans')]
                            }

defaultShortcut = {'defaults': [ThreeVectorIntBlock(key='cell_constraints', lines=['0   0   0', '0   0   0']),
                                StrBlock(key='species_pot', lines=['SOC19']),
                                BoolKeyword(key='fix_com', value=True),
                                StrKeyword(key='task', value='singlepoint'),
                                StrKeyword(key='xcfunctional', value='LDA'),
                                FloatKeyword(key='cut_off_energy', value=700.0, unit='eV'),
                                BoolKeyword(key='fix_occupancy', value=True),
                                IntKeyword(key='iprint', value=3)]
                   }



stringToSettings = shortcutToCells | shortcutToCellsAliases | shortcutToParams | shortcutToParamsAliases | defaultShortcut




def getSetting(key=None, **kwargs):
    assert type(key) is str

    key = key.strip().lower()

    settingObject = settingTypes.get(key, None)

    assert settingObject is not None, f'Key {key} does not correspond to setting'

    newSetting = settingObject(key=key, **kwargs)

    return newSetting


def readSettings(file_=None):
    assert type(file_) is str
    assert Path(file_).is_file(), f'Cannot find file {file_} when reading settings'

    with open(file_) as f:
        lines = f.read().splitlines()

    lines = [line.strip() for line in lines if line.strip()]

    settingKey = ''
    inBlock = False
    blockLines = []

    settings = []

    for line in lines:

        # Check for comment.
        comment = line.find('!')

        # Remove it if need be.
        if comment != -1:
            line = line[:comment].strip()

        if inBlock:
            # Don't lower() line before as we may want capitalisation.
            if line.lower().startswith('%'):

                # Get rid of the '%' - don't need capitalisation now
                line = line[1:].strip().lower()

                # Check 'endblock' comes after.
                if line.startswith('endblock'):
                    line = line[8:].strip()

                    # Check that there is only one string after 'endblock'.
                    settingKeys = line.split()
                    if len(settingKeys) == 1:
                        settingKeyOther = settingKeys[0]
                    else:
                        raise ValueError(f'Error in block in line \'{line}\' of file {file_}')

                    assert settingKey == settingKeyOther, f'Entered block {settingKey} but found endblock {settingKeyOther}'

                    arguments = {'lines': blockLines}

                    newSetting = getSetting(key=settingKey, **arguments)

                    settings.append(newSetting)

                    # We have now exited a block.
                    inBlock = False
                    blockLines = []

                else:
                    raise ValueError(f'Error in block in line \'{line}\' of file {file_}')
            else:
                blockLines.append(line)

        else:
            # Don't lower() line before as we may want capitalisation if it is not a block.
            if line.lower().startswith('%'):

                # Get rid of the '%' - don't need capitalisation now
                line = line[1:].strip().lower()

                # Check 'block' comes after.
                if line.startswith('block'):
                    line = line[5:].strip()

                    # We have now entered a block.
                    inBlock = True
                    blockLines = []

                    # Check that there is only one string after 'block'.
                    settingKeys = line.split()
                    if len(settingKeys) == 1:
                        settingKey = settingKeys[0]
                    else:
                        raise ValueError(f'Error in block in line \'{line}\' of file {file_}')

                else:
                    raise ValueError(f'Error in block in line \'{line}\' of file {file_}')

            else:
                # If we're here then we have a keyword.

                parts = line.split()
                parts = [part.strip() for part in parts if part.strip() not in [':', '=']]

                if len(parts) == 1:
                    # e.g. symmetry_generate
                    key = parts[0].lower()
                    value = True

                    arguments = {'value': value}

                elif len(parts) == 2:
                    key = parts[0].lower()
                    value = stringToValue(parts[1])

                    arguments = {'value': value}

                elif len(parts) == 3:
                    key = parts[0].lower()
                    value = stringToValue(parts[1])
                    unit = parts[2]

                    arguments = {'value': value, 'unit': unit}

                elif len(parts) == 4:
                    # e.g. kpoints_mp_grid : 1.0 1.0 1.0
                    key = parts[0].lower()
                    value = stringToValue(' '.join(parts[1:3]))

                    arguments = {'value': value}

                else:
                    raise ValueError(f'Error in keyword {line} of file {file_}')

                newSetting = getSetting(key=key, **arguments)

                settings.append(newSetting)

    return settings


def createSettings(*settings):
    """ This function takes in a list of strings and settings
        and converts the strings to the settings that they are
        shortcuts to """

    # Split the settings up into settings and shortcuts
    settings, shortcuts = parseArgs(*settings)

    # Check that we have one of each string.
    assertCount([shortcut.strip().lower() for shortcut in shortcuts])

    # The shortcuts point to one or more params/cells.
    # E.g. 'soc' is spin_treatment=vector and spin_orbit_coupling=true.
    settingsFromShortcuts = shortcutsToSettings(*shortcuts)

    for setting in settingsFromShortcuts:
        if isinstance(setting, Setting):
            settings.append(setting)
        else:
            raise TypeError(f'{type(setting)} type not recognised in shortcut')

    # Check that none of the shortcuts themselves have now duplicated any cells/params.
    assertCount([setting.key for setting in settings])

    return settings


def createVariableSettings(*variableSettings):
    """ This functions takes in a list of strings/lists/tuples.
        The strings are treated as shortcuts and converted
        appropriately. The tuples are turned to lists. The
        output is a list of lists of settings. The list
        would then typically be outer producted to generate
        all the possible variations of the settings.
        E.g. [[HF, HCl], [soc=false, soc=true]]
        would be outer producted to
        [HF+soc=false, HF+soc=true, HCl+soc=false, HCl+soc=true] """

    variableSettingsProcessed = []

    for variable in variableSettings:
        assert type(variable) in [str, list, tuple],\
            f'Specify only shortcut strings, lists or tuples for variable cells/params, not {type(variable)}'

        # Strings are shortcuts, but shortcuts to specific combinations of cells/params.
        # E.g. 'soc' is a tuple of three different settings:
        # 1 -> spin_treatment=scalar and spin_orbit_coupling=false
        # 2 -> spin_treatment=vector and spin_orbit_coupling=false
        # 3 -> spin_treatment=vector and spin_orbit_coupling=true
        # So let's turn the shortcut string (if needed) into its list combination.
        variable = getVariableSetting(variable.strip().lower()) if type(variable) is str else variable

        # Create a list to store this combination.
        lst = []

        for strListSetting in variable:
            type_ = type(strListSetting)

            # Shortcut string.
            if type_ is str:
                variableSettings = shortcutsToSettings(strListSetting.strip().lower())
                lst.append(variableSettings)

            # User defined.
            elif type_ in [list, tuple]:
                assert all(isinstance(setting, Setting) for setting in strListSetting), 'Settings should only be cells or params'
                lst.append(list(strListSetting))

            elif isinstance(strListSetting, Setting):
                lst.append([strListSetting])

            else:
                raise TypeError('A specific setting of several cells/params must be given as a shortcut or tuple')

        variableSettingsProcessed.append(lst)

    return variableSettingsProcessed


def shortcutsToSettings(*shortcuts):
    """ This function gets a specific shortcut from a string.
        A string maps to a list of cells/params and is simply
        an easy way to generate common settings in calculations. """

    settings = []

    for shortcut in shortcuts:
        assert type(shortcut) is str

        settingOrList = stringToSettings.get(shortcut.lower(), None)

        newSettings = [settingOrList] if isinstance(settingOrList, Setting) else settingOrList

        assert newSettings is not None, f'Shortcut string {shortcut} not recognised'

        settings += newSettings

    return settings


def getVariableSetting(string=None):
    """ This function gets a specific shortcut from a string.
        The string will map to a list that contains lists of
        cells/params, each to be used as a different setting. """

    assert type(string) is str

    variableSetting = stringToVariableSettings.get(string.lower(), None)

    assert variableSetting is not None, f'Shortcut to variable settings {string} not recognised'

    return variableSetting


def getCellsParams(settings=None):
    """ This functions takes a list of settings and
        splits them up into two sorted lists of
        cells and params"""

    if settings is None:
        return None

    assert type(settings) is list
    assert all(isinstance(setting, Setting) for setting in settings)

    cells = []
    params = []

    for setting in settings:
        if setting.file == 'cell':
            cells.append(setting)
        elif setting.file == 'param':
            params.append(setting)
        else:
            raise ValueError(f'File {setting.file} not recognised')

    cells = sorted(cells, key=lambda cell: cell.priority)
    params = sorted(params, key=lambda param: param.priority)

    return cells, params


def parseArgs(*stringsAndSettings):
    """ This function takes in a list of settings
        and strings and splits them up into two
        lists """

    settings = []
    strings = []

    for arg in stringsAndSettings:
        t = type(arg)

        if t is str:
            strings.append(arg)

        elif isinstance(arg, Setting):
            settings.append(arg)

        elif t is tuple:
            for arg2 in arg:
                t2 = type(arg2)

                if t2 is str:
                    strings.append(arg2)

                elif isinstance(t2, Setting):
                    settings.append(arg2)

                else:
                    raise TypeError(f'Cannot have type {t2} in tuple')

        elif t is list:
            for arg2 in arg:
                t2 = type(arg2)

                if t2 is str:
                    strings.append(arg2)

                elif isinstance(t2, Setting):
                    settings.append(arg2)

                else:
                    raise TypeError(f'Cannot have type {t2} in list')

        else:
            raise TypeError(f'Cannot have type {t}')

    return settings, strings
