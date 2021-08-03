from calc import Model, createCalculations, createDirectories, createSettings, createVariableSettings#, Setting

directories = createDirectories('halides', 'zbfield', 'density')
settings = createSettings('hyperfine', 'soc')
variableSettings = createVariableSettings('halides', 'zbfield', 'density')

calculations = createCalculations(*variableSettings,
                                  globalSettings=settings,
                                  directoryNames=directories,
                                  withDefaults=True)

model = Model(calculations)
#print(model)

model.create(force=True)