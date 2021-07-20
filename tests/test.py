from calc import Cell, Param, Calculation, setupCalculations

'''
cells = [Cell('lattice_cart', ['0.5 0.5 0.5', '0.4 0.4 0.4', '0.9 0.9 0.4'])]

params = [Param('task', 'magres'),
          Param('cut_off_energy', 500)]

t = Calculation(cells=cells, params=params)

print(t)
'''



setupCalculations(['HF', 'HCl'],
                  [Param('spin_treatment', 'scalar'), Param('spin_treatment', 'vector')],
                  [Param('cut_off_energy', 500), Param('cut_off_energy', 700)])
