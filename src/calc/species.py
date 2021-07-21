from calc.cells import Cell

shortcutToSpecies = {'hf': [Cell(key='lattice_cart', lines=[' ANG',
                                                            '  10.0   0.0   0.0',
                                                            '   0.0  10.0   0.0',
                                                            '   0.0   0.0  10.0']),

                            Cell(key='cell_constraints', lines=['  0  0  0',
                                                                '  0  0  0']),

                            Cell(key='positions_frac',
                                 lines=['  H   0.1   0.1   0.099380480724825',
                                        '  F   0.1   0.1   0.192319519275175']),

                            Cell(key='fix_com', value=True),

                            Cell(key='species_pot', lines=['SOC19']),

                            Cell(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])
                            ],

                     'hcl': [Cell(key='lattice_cart', lines=[' ANG',
                                                             '  10.0   0.0   0.0',
                                                             '   0.0  10.0   0.0',
                                                             '   0.0   0.0  10.0']),

                             Cell(key='cell_constraints', lines=['  0  0  0',
                                                                 '  0  0  0']),

                             Cell(key='positions_frac',
                                  lines=['  H    0.009999871806914   0.009999872045901   0.009226072370290',
                                         '  Cl   0.010000128193086   0.010000127954099   0.138173927629710']),

                             Cell(key='fix_com', value=True),

                             Cell(key='species_pot', lines=['SOC19']),

                             Cell(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])
                             ],

                     'hbr': [Cell(key='lattice_cart', lines=[' ANG',
                                                             '  12.0   0.0   0.0',
                                                             '   0.0  12.0   0.0',
                                                             '   0.0   0.0  12.0']),

                             Cell(key='cell_constraints', lines=['  0  0  0',
                                                                 '  0  0  0']),

                             Cell(key='positions_frac',
                                  lines=['  H    -0.000002946190640  -0.000003049675148   0.011117199951347',
                                         '  Br    0.000002946190640   0.000003049675148   0.130282800048653']),

                             Cell(key='fix_com', value=True),

                             Cell(key='species_pot', lines=['SOC19']),

                             Cell(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])
                             ],

                     'hi': [Cell(key='lattice_cart', lines=[' ANG',
                                                            '  12.0   0.0   0.0',
                                                            '   0.0  12.0   0.0',
                                                            '   0.0   0.0  12.0']),

                            Cell(key='cell_constraints', lines=['  0  0  0',
                                                                '  0  0  0']),

                            Cell(key='positions_frac',
                                 lines=['  H   0.000000000013618   0.000000000163156  -0.000952894767401',
                                        '  I  -0.000000000013618  -0.000000000163156   0.135036228100734']),

                            Cell(key='fix_com', value=True),

                            Cell(key='species_pot', lines=['SOC19']),

                            Cell(key='kpoints_list', lines=['0.25 0.25 0.25 1.0'])
                            ],
                     }
