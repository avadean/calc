from calc.data import getAllowedUnits, getNiceUnit


def getType(key=None, strict=True):
    assert type(key) is str
    assert type(strict) is bool

    type_ = paramTypes.get(key, None)

    if type_ is None and strict:
        raise ValueError('Param key {} does not have a type'.format(key))

    return type_


def getUnitType(key=None, strict=True):
    assert type(key) is str
    assert type(strict) is bool

    unit = paramUnits.get(key, None)

    if unit is None and strict:
        raise ValueError('Param key {} does not have a unit type'.format(key))

    return unit


def getPriority(key=None, strict=False):
    assert type(key) is str
    assert type(strict) is bool

    priority = paramPriorities.get(key, None)

    if priority is None and strict:
        raise ValueError('Param key {} does not have a priority'.format(key))

    return priority



class Param:
    key = None
    value = None
    unit = None
    unitType = None

    block = False
    blockLines = None

    priority = None

    def __init__(self, key=None, value=None, unit=None,
                 block=False, blockLines=None):

        assert type(key) is str
        assert key in paramKnown, '{} not a known parameter'.format(key)
        self.key = key

        assert type(block) is bool
        self.block = block

        if self.block:
            assert type(blockLines) is list
            assert all(type(line) == str for line in blockLines)
            self.blockLines = blockLines

        else:
            self.type = getType(key)

            if type(value) is int and self.type is float:
                value = float(value)

            assert type(value) is self.type, 'Value {} not acceptable for {}, should be {}'.format(value, self.key, self.type)

            if self.type is str:
                assert value in paramValues.get(self.key)
            elif self.type is bool:
                assert value in [True, False]
            elif self.type in [float, int]:
                assert min(paramValues.get(self.key)) <= value <= max(paramValues.get(self.key))

            self.value = value

            if unit is not None:
                self.unitType = getUnitType(key)

                assert type(unit) is str
                assert unit in getAllowedUnits(self.unitType), 'Unit {} is not an acceptable type for {}'.format(unit,
                                                                                                                 self.unitType)

                self.unit = getNiceUnit(unit)

        self.priority = getPriority(key)

    def __str__(self):
        attributes = [attr for attr in dir(self)
                      if not attr.startswith('__') and
                      self.__getattribute__(attr) not in [None, False]
                      ]

        string = ''

        for attr in attributes:
            value = self.__getattribute__(attr)
            value = str(value) if type(value) is type else value
            string += '  {:>12} : {:<12}\n'.format(attr, value)

        return string



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
    'spin_polarized',
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
    'comment'
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
    'spin_polarized': 3.2,
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
    'comment': 11.4
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
    'spin_polarized': 'true if spin > 0 else false',
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
    'task': str,
    'magres_task': str,
    'magres_method': str,
    'spectral_task': str,

    # general
    'xcfunctional': str,
    'opt_strategy': str,
    'cut_off_energy': float,
    'fix_occupancy': bool,
    'basis_precision': str,
    'relativistic_treatment': str,

    # metals
    'smearing_width': float,
    'metals_method': str,
    'nextra_bands': int,

    # spin
    'spin': float,
    'spin_polarised': bool,
    'spin_polarized': bool,
    'spin_treatment': str,
    'spin_orbit_coupling': bool,

    # bandstructure
    'bs_nbands': int,

    # phonons
    'phonon_method': str,
    'phonon_sum_rule': bool,
    'phonon_fine_cutoff_method': str,

    # charge
    'charge': float,

    # calculate
    'calc_molecular_dipole': bool,
    'popn_calculate': bool,
    'calculate_raman': bool,
    'calculate_densdiff': bool,

    # write
    'write_cell_structure': bool,
    'write_formatted_density': bool,
    'popn_write': bool,

    # units
    'dipole_unit': str,

    # miscellaneous.
    'max_scf_cycles': int,
    'num_dump_cycles': int,
    'elec_energy_tol': float,
    'bs_eigenvalue_tol': float,

    # extra
    'continuation': str,
    'iprint': str,
    'rand_seed': int,
    'comment': str
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


paramValues = {
    # tasks
    'task'                      : ['singlepoint', 'bandstructure', 'geometryoptimisation', 'geometryoptimization', 'moleculardynamics', 'optics', 'transitionstatesearch', 'phonon', 'efield', 'phonon+efield', 'thermodynamics', 'wannier', 'magres', 'elnes', 'spectral', 'epcoupling', 'geneticalgor'],
    'magres_task'               : ['shielding', 'efg', 'nmr', 'gtensor', 'hyperfine', 'epr', 'jcoupling'],
    'magres_method'             : ['crystal', 'molecular', 'molecular3'],
    'spectral_task'             : ['bandstructure', 'dos', 'optics', 'coreloss', 'all'],

    # general
    'xcfunctional'              : ['lda', 'pw91', 'pbe', 'pbesol', 'rpbe', 'wc', 'blyp', 'lda-c', 'lda-x', 'zero', 'hf', 'pbe0', 'b3lyp', 'hse03', 'hse06', 'exx-x', 'hf-lda', 'exx', 'exx-lda', 'shf', 'sx', 'shf-lda', 'sx-lda', 'wda', 'sex', 'sex-lda', 'rscan'],
    'opt_strategy'              : ['default', 'speed', 'memory'],
    'cut_off_energy'            : [0.0, float('inf')],
    'basis_precision'           : ['null', 'coarse', 'medium', 'fine', 'precise', 'extreme'],
    'relativistic_treatment'    : ['koelling-harmon', 'schroedinger', 'zora', 'dirac'],

    # metals
    'smearing_width'            : [0.0, float('inf')],
    'metals_method'             : ['none', 'dm', 'edft'],
    'nextra_bands'              : [0.0, float('inf')],

    # spin
    'spin'                      : [-float('inf'), float('inf')],
    'spin_treatment'            : ['none', 'scalar', 'vector'],

    # bandstructure
    'bs_nbands'                 : [0, float('inf')],

    # phonons
    'phonon_method'             : ['dfpt', 'linearresponse', 'finitedisplacement'],
    'phonon_fine_cutoff_method' : ['cumulant', 'spherical'],

    # charge
    'charge'                    : [-float('inf'), float('inf')],

    # miscellaneous.
    'max_scf_cycles'            : [0, float('inf')],
    'num_dump_cycles'           : [0, float('inf')],
    'elec_energy_tol'           : [0.0, float('inf')],
    'bs_eigenvalue_tol'         : [0.0, float('inf')],

    # extra
    'iprint'                    : [1, 2, 3],
    'rand_seed'                 : [-float('inf'), float('inf')],
}
