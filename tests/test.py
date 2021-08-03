from calc import Model, createCalculations, createDirectories, createSettings, createVariableSettings, Setting

'''
directories = createDirectories('halides', 'hyperfinebfield')
settings = createSettings('hyperfine', 'soc')
variableSettings = createVariableSettings('halides', 'hyperfinebfield')

calculations = createCalculations(*variableSettings,
                                  globalSettings=settings,
                                  directoryNames=directories,
                                  withDefaults=True)
'''

#model = Model(calculations)
#print(model)

model = Model()

model.create(force=True)

model.sub(test=True)
#model.sub()
