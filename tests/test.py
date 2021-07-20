from calc import Cell, Param, Calculation, setupCalculations, parseArgs

'''
cells = [Cell('lattice_cart', ['0.5 0.5 0.5', '0.4 0.4 0.4', '0.9 0.9 0.4'])]

params = [Param('task', 'magres'),
          Param('cut_off_energy', 500)]

t = Calculation(cells=cells, params=params)

print(t)
'''


calculations = setupCalculations([(Param('spin_treatment', 'scalar'),
                                   Param('spin_orbit_coupling', False)),

                                  (Param('spin_treatment', 'vector'),
                                   Param('spin_orbit_coupling', False)),

                                  (Param('spin_treatment', 'vector'),
                                   Param('spin_orbit_coupling', True))],

                                 [Param('spin', 0.3), Param('spin', 0.5), Param('spin', 0.7)],

                                 other=())


for calculation in calculations:
    print(calculation)
