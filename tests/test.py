from calc import Model, createCalculations, createDirectories, createSettings, createVariableSettings, Setting


directories = createDirectories(['HF', 'HCl'])
settings = createSettings('hyperfine', 'soc')
variableSettings = createVariableSettings(['HF', 'HCl'])

calculations = createCalculations(*variableSettings,
                                  #globalSettings=settings,
                                  directoryNames=directories,
                                  withDefaults=True)


#model = Model(calculations)
#print(model)

model = Model(calculations)

model.create(force=True)

model.sub(test=True)
#model.sub()
