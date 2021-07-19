from calc import Cell, Param, Model

cells = [Cell('lattice_cart', ['0.5 0.5 0.5', '0.4 0.4 0.4', '0.9 0.9 0.4'])]

params = [Param('task', 'singlepoint'),
          Param('cut_off_energy', 500)]


t = Model(cells=cells, params=params)

print(t)
