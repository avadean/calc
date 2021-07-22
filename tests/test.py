from calc import Model, createCalculations, Setting, createDirectories, createSettings

directories = createDirectories([['HF', 'HCl'], 'zbfield'])
settings = createSettings(['shielding', Setting('iprint', 3),
                           Setting('spin_treatment', 'vector'), Setting('spin_orbit_coupling', True)])

calculations = createCalculations(['HF', 'HCl'], 'zbfield',
                                  globalSettings=settings,
                                  directoryNames=directories)

model = Model(calculations)
