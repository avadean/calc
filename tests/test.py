from calc import Model, createCalculations, Setting, createDirectories, createSettings, createVariableSettings

directories = createDirectories(['HF', 'HCl'], 'zbfield')
settings = createSettings('shielding', Setting('iprint', 3), 'usp', 'soc')
variableSettings = createVariableSettings(['HF', 'HCl'], 'zbfield')

calculations = createCalculations(*variableSettings,
                                  globalSettings=settings,
                                  directoryNames=directories)

model = Model(calculations)
print(model)
