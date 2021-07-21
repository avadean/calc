from calc.data import getAllowedUnits, getNiceUnit, Block, VectorInt, VectorFloat


def getType(key=None, strict=True):
    assert type(key) is str
    assert type(strict) is bool

    type_ = cellTypes.get(key, None)

    if type_ is None and strict:
        raise ValueError('Cell key {} does not have a type'.format(key))

    return type_


def getUnitType(key=None, strict=True):
    assert type(key) is str
    assert type(strict) is bool

    unit = cellUnits.get(key, None)

    if unit is None and strict:
        raise ValueError('Cell key {} does not have a unit type'.format(key))

    return unit


def getPriority(key=None, strict=False):
    assert type(key) is str
    assert type(strict) is bool

    priority = cellPriorities.get(key, None)

    if priority is None and strict:
        raise ValueError('Cell key {} does not have a priority'.format(key))

    return priority


class Cell:
    def __init__(self, key=None, value=None, unit=None, lines=None):
        assert type(key) is str
        key = key.lower()
        assert key in cellKnown, '{} not a known cell'.format(key)
        self.key = key

        self.type = getType(key)

        if self.type is Block:
            assert type(lines) is list
            assert all(type(line) == str for line in lines)
            self.lines = lines

        else:
            if type(value) is int and self.type is float:
                value = float(value)

            assert type(value) is self.type, 'Value {} not acceptable for {}, should be {}'.format(value,
                                                                                                   self.key,
                                                                                                   self.type)

            if self.type is str:
                value = value.lower()
                assert value in cellValues.get(self.key)

            elif self.type is bool:
                assert value in [True, False]

            elif self.type in [float, int]:
                assert min(cellValues.get(self.key)) <= value <= max(cellValues.get(self.key))

            elif self.type in [VectorInt, VectorFloat]:
                minimum = min(cellValues.get(self.key))
                maximum = max(cellValues.get(self.key))
                assert minimum <= value.x <= maximum
                assert minimum <= value.y <= maximum
                assert minimum <= value.z <= maximum

            self.value = value

            if unit is not None:
                self.unitType = getUnitType(key)

                assert type(unit) is str
                assert unit in getAllowedUnits(self.unitType),\
                    'Unit {} is not an acceptable type for {}'.format(unit, self.unitType)

                self.unit = getNiceUnit(unit)

        self.priority = getPriority(key)



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
    'kpoint_mp_spacing': 7.1,
    'kpoints_mp_spacing': 7.1,
    'kpoint_mp_grid': 7.2,
    'kpoints_mp_grid': 7.2,
    'kpoint_mp_offset': 7.3,
    'kpoints_mp_offset': 7.3,
    'fix_all_cell': 7.4,
    'fix_com': 7.5,
    'symmetry_tol': 7.6,
    'symmetry_generate': 7.7,
}


#cellDefaults = {}

cellTypes = {
# Lattice.
    'lattice_abc' : Block,
    'lattice_cart' : Block,

    # Positions.
    'positions_abs' : Block,
    'positions_frac' : Block,

    # Constraints.
    'cell_constraints' : Block,

    # Pseudopotentials.
    'species_pot' : Block,

    # Symmetry.
    'symmetry_ops' : Block,

    # Fields.
    'external_bfield' : Block,

    # Kpoints.
    'kpoint_list' : Block,
    'kpoints_list' : Block,
    'bs_kpoint_list' : Block,
    'bs_kpoints_list' : Block,
    'phonon_kpoint_list' : Block,
    'phonon_kpoints_list' : Block,
    'phonon_fine_kpoint_list' : Block,
    'optics_kpoint_list' : Block,
    'optics_kpoints_list' : Block,
    'magres_kpoint_list' : Block,
    'supercell_kpoint_list' : Block,
    'supercell_kpoints_list' : Block,
    'spectral_kpoint_list' : Block,
    'spectral_kpoints_list' : Block,

    # Keywords.
    'kpoint_mp_spacing' : float,
    'kpoints_mp_spacing' : float,
    'kpoint_mp_grid' : VectorInt,
    'kpoints_mp_grid' : VectorInt,
    'kpoint_mp_offset' : VectorFloat,
    'kpoints_mp_offset' : VectorFloat,
    'fix_all_cell' : bool,
    'fix_com' : bool,
    'symmetry_tol' : float,
    'symmetry_generate' : bool
}


cellValues = {
     'kpoint_mp_spacing' : [0.0, float('inf')],
     'kpoints_mp_spacing' : [0.0, float('inf')],
     'kpoint_mp_grid' : [0, float('inf')],
     'kpoints_mp_grid' : [0, float('inf')],
     'kpoint_mp_offset' : [-float('inf'), float('inf')],
     'kpoints_mp_offset' : [-float('inf'), float('inf')],
     'symmetry_tol' : [0.0, float('inf')]
}


cellUnits = {
    'kpoint_mp_spacing' : 'inverseLength',
    'kpoints_mp_spacing' : 'inverseLength',
    'symmetry_tol' : 'length'
}


shortcutToCells = {}
