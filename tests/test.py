from calc import Cell, Param, Calculation, setupCalculations, parseArgs

'''
cells = [Cell('lattice_cart', ['0.5 0.5 0.5', '0.4 0.4 0.4', '0.9 0.9 0.4'])]

params = [Param('task', 'magres'),
          Param('cut_off_energy', 500)]

t = Calculation(cells=cells, params=params)

print(t)
'''


calculations = setupCalculations('soc', generalSettings='HF')


for calculation in calculations:
    print(calculation)
