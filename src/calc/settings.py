from calc.data import getAllowedUnits, getNiceUnit, getFromDict, Block, VectorInt, VectorFloat


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
    'lattice_abc': Block,
    'lattice_cart': Block,

    # Positions.
    'positions_abs': Block,
    'positions_frac': Block,

    # Constraints.
    'cell_constraints': Block,

    # Pseudopotentials.
    'species_pot': Block,

    # Symmetry.
    'symmetry_ops': Block,

    # Fields.
    'external_bfield': Block,

    # Kpoints.
    'kpoint_list': Block,
    'kpoints_list': Block,
    'bs_kpoint_list': Block,
    'bs_kpoints_list': Block,
    'phonon_kpoint_list': Block,
    'phonon_kpoints_list': Block,
    'phonon_fine_kpoint_list': Block,
    'optics_kpoint_list': Block,
    'optics_kpoints_list': Block,
    'magres_kpoint_list': Block,
    'supercell_kpoint_list': Block,
    'supercell_kpoints_list': Block,
    'spectral_kpoint_list': Block,
    'spectral_kpoints_list': Block,

    # Keywords.
    'kpoint_mp_spacing': float,
    'kpoints_mp_spacing': float,
    'kpoint_mp_grid': VectorInt,
    'kpoints_mp_grid': VectorInt,
    'kpoint_mp_offset': VectorFloat,
    'kpoints_mp_offset': VectorFloat,
    'fix_all_cell': bool,
    'fix_com': bool,
    'symmetry_tol': float,
    'symmetry_generate': bool
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
    'kpoint_mp_spacing': 'inverseLength',
    'kpoints_mp_spacing': 'inverseLength',
    'symmetry_tol': 'length'
}

shortcutToCells = {}

shortcutToCellsAliases = {}










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
    'comment': str,

    # blocks
    'devel_code': Block
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











settingKnown = cellKnown + paramKnown
settingPriorities = cellPriorities | paramPriorities
settingTypes = cellTypes | paramTypes
settingValues = cellValues | paramValues
settingUnits = cellUnits | paramUnits





class Setting:
    def __init__(self, key=None, value=None, unit=None, lines=None):
        assert type(key) is str
        key = key.lower()

        # See if we can find the key in cells, then params, if not then we don't know what it is.
        if key in cellKnown:
            self.file = 'cell'
        elif key in paramKnown:
            self.file = 'param'
        else:
            raise ValueError('{} not a known setting'.format(key))

        self.key = key
        self.type = getFromDict(key, settingTypes)

        if self.type is Block:
            assert type(lines) is list
            assert all(type(line) is str for line in lines)
            self.lines = [line.strip() for line in lines]

        else:
            if type(value) is int and self.type is float:
                value = float(value)

            assert type(value) is self.type, 'Value {} not acceptable for {}, should be {}'.format(value,
                                                                                                   self.key,
                                                                                                   self.type)

            if self.type is str:
                value = value.strip().lower()
                assert value in settingValues.get(self.key)

            elif self.type is bool:
                assert value in [True, False]

            elif self.type in [float, int]:
                assert min(settingValues.get(self.key)) <= value <= max(settingValues.get(self.key))

            elif self.type in [VectorInt, VectorFloat]:
                minimum = min(settingValues.get(self.key))
                maximum = max(settingValues.get(self.key))
                assert minimum <= value.x <= maximum
                assert minimum <= value.y <= maximum
                assert minimum <= value.z <= maximum

            self.value = value

            if unit is not None:
                self.unitType = getFromDict(key, settingUnits)

                assert type(unit) is str
                unit = unit.lower()
                assert unit in getAllowedUnits(self.unitType),\
                    'Unit {} is not an acceptable type for {}'.format(unit, self.unitType)

                self.unit = getNiceUnit(unit)

        self.priority = getFromDict(key, settingPriorities)

    def __str__(self):
        if self.type is Block:
            return '; '.join(self.lines)

        elif self.type is float:
            return '{:<12.4f}'.format(self.value)

        else:
            return str(self.value)


















shortcutToParams = {'singlepoint': Setting('task', 'singlepoint'),
                    'geometryoptimisation': Setting('task', 'geometryoptimisation'),

                    'lda': Setting('xcfunctional', 'lda'),
                    'pbe': Setting('xcfunctional', 'pbe'),
                    'pw91': Setting('xcfunctional', 'pw91'),
                    'b3lyp': Setting('xcfunctional', 'b3lyp'),

                    'lowcutoff': Setting('cut_off_energy', 300, 'eV'),
                    'cutoff': Setting('cut_off_energy', 500, 'eV'),
                    'highcutoff': Setting('cut_off_energy', 700, 'eV'),

                    'schroedinger': Setting('relativistic_treatment', 'schroedinger'),
                    'dirac': Setting('relativistic_treatment', 'dirac'),

                    'spin_polarised': Setting('spin_polarised', True),

                    'efg': [Setting('task', 'magres'),
                            Setting('magres_task', 'efg')],

                    'shielding': [Setting('task', 'magres'),
                                  Setting('magres_task', 'shielding')],

                    'nmr': [Setting('task', 'magres'),
                            Setting('magres_task', 'nmr')],

                    'hyperfine': [Setting('task', 'magres'),
                                  Setting('magres_task', 'hyperfine')],

                    # 'jcoupling': NotImplementedError,

                    'soc': [Setting('spin_treatment', 'vector'),
                            Setting('spin_orbit_coupling', True)],

                    'xdensity': Setting('devel_code', lines=['density_in_x=true']),
                    'ydensity': Setting('devel_code', lines=['density_in_y=true']),
                    'zdensity': Setting('devel_code', lines=['density_in_z=true'])
                    }

shortcutToParamsAliases = {'geom': shortcutToParams.get('geometryoptimisation'),
                           'geometry': shortcutToParams.get('geometryoptimisation'),
                           'optimise': shortcutToParams.get('geometryoptimisation'),
                           'optimize': shortcutToParams.get('geometryoptimisation'),
                           'optimisation': shortcutToParams.get('geometryoptimisation'),
                           'optimization': shortcutToParams.get('geometryoptimisation'),
                           'geometryoptimization': shortcutToParams.get('geometryoptimisation'),

                           'normalcutoff': shortcutToParams.get('cutoff'),
                           'averagecutoff': shortcutToParams.get('cutoff'),
                           'middlecutoff': shortcutToParams.get('cutoff'),
                           'mediumcutoff': shortcutToParams.get('cutoff'),

                           'schrod': shortcutToParams.get('schroedinger'),
                           'schrodinger': shortcutToParams.get('schroedinger'),
                           'schroed': shortcutToParams.get('schroedinger'),

                           'polarised': shortcutToParams.get('spin_polarised'),
                           'polarized': shortcutToParams.get('spin_polarised'),
                           'spin_polarized': shortcutToParams.get('spin_polarised'),
                           }








shortcutToSpecies = {'hf': [Setting(key='lattice_cart', lines=[' ANG',
                                                               '  10.0   0.0   0.0',
                                                               '   0.0  10.0   0.0',
                                                               '   0.0   0.0  10.0']),

                            Setting(key='cell_constraints', lines=['  0  0  0',
                                                                   '  0  0  0']),

                            Setting(key='positions_frac',
                                    lines=['  H   0.1   0.1   0.099380480724825',
                                           '  F   0.1   0.1   0.192319519275175']),

                            Setting(key='fix_com', value=True),

                            Setting(key='species_pot', lines=['SOC19']),

                            Setting(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])
                            ],

                     'hcl': [Setting(key='lattice_cart', lines=[' ANG',
                                                                '  10.0   0.0   0.0',
                                                                '   0.0  10.0   0.0',
                                                                '   0.0   0.0  10.0']),

                             Setting(key='cell_constraints', lines=['  0  0  0',
                                                                    '  0  0  0']),

                             Setting(key='positions_frac',
                                     lines=['  H    0.009999871806914   0.009999872045901   0.009226072370290',
                                            '  Cl   0.010000128193086   0.010000127954099   0.138173927629710']),

                             Setting(key='fix_com', value=True),

                             Setting(key='species_pot', lines=['SOC19']),

                             Setting(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])
                             ],

                     'hbr': [Setting(key='lattice_cart', lines=[' ANG',
                                                                '  12.0   0.0   0.0',
                                                                '   0.0  12.0   0.0',
                                                                '   0.0   0.0  12.0']),

                             Setting(key='cell_constraints', lines=['  0  0  0',
                                                                    '  0  0  0']),

                             Setting(key='positions_frac',
                                     lines=['  H    -0.000002946190640  -0.000003049675148   0.011117199951347',
                                            '  Br    0.000002946190640   0.000003049675148   0.130282800048653']),

                             Setting(key='fix_com', value=True),

                             Setting(key='species_pot', lines=['SOC19']),

                             Setting(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])
                             ],

                     'hi': [Setting(key='lattice_cart', lines=[' ANG',
                                                               '  12.0   0.0   0.0',
                                                               '   0.0  12.0   0.0',
                                                               '   0.0   0.0  12.0']),

                            Setting(key='cell_constraints', lines=['  0  0  0',
                                                                   '  0  0  0']),

                            Setting(key='positions_frac',
                                    lines=['  H   0.000000000013618   0.000000000163156  -0.000952894767401',
                                           '  I  -0.000000000013618  -0.000000000163156   0.135036228100734']),

                            Setting(key='fix_com', value=True),

                            Setting(key='species_pot', lines=['SOC19']),

                            Setting(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])
                            ],
                     }







stringToVariableSettings = { 'soc' : [(Setting('spin_treatment', 'scalar'), Setting('spin_orbit_coupling', False)),
                                      (Setting('spin_treatment', 'vector'), Setting('spin_orbit_coupling', False)),
                                      (Setting('spin_treatment', 'vector'), Setting('spin_orbit_coupling', True))],

                             'density' : [Setting('devel_code', lines=['density_in_x=true']),
                                          Setting('devel_code', lines=['density_in_y=true']),
                                          Setting('devel_code', lines=['density_in_z=true'])]
                             }







stringToShortcuts = shortcutToCells | shortcutToCellsAliases | shortcutToParams | shortcutToParamsAliases | shortcutToSpecies



def orderSettings(settings=None):
    assert type(settings) is list
    assert all(type(setting) is Setting for setting in settings)

    cells = []
    params = []

    for setting in settings:
        if setting.file == 'cell':
            cells.append(setting)
        elif setting.file == 'param':
            params.append(setting)
        else:
            raise ValueError('File {} not recognised'.format(setting.file))

    cells = sorted(cells, key=lambda cell: cell.priority)
    params = sorted(params, key=lambda param: param.priority)

    return cells + params



def parseArgs(*args):
    if len(args) == 0:
        return [], [], []

    settings = []
    strings = []

    for arg in args:
        t = type(arg)

        if t is str:
            strings.append(arg)

        elif t is Setting:
            settings.append(arg)

        elif t is tuple:
            for arg2 in arg:
                t2 = type(arg2)

                if t2 is str:
                    strings.append(arg2)

                elif t2 is Setting:
                    settings.append(arg2)

                else:
                    raise TypeError('Cannot have type {} in tuple'.format(t2))

        elif t is list:
            for arg2 in arg:
                t2 = type(arg2)

                if t2 is str:
                    strings.append(arg2)

                elif t2 is Setting:
                    settings.append(arg2)

                else:
                    raise TypeError('Cannot have type {} in list'.format(t2))

        else:
            raise TypeError('Cannot have type {}'.format(t))

    return settings, strings