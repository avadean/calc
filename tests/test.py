from calc import Model, createCalculations, createDirectories, createSettings, createVariableSettings, Setting

directories = createDirectories(['HF', 'HCl'], 'soc')
settings = createSettings('shielding', 'iprint')
variableSettings = createVariableSettings(['HF', 'HCl'], 'soc')

calculations = createCalculations(*variableSettings,
                                  globalSettings=settings,
                                  directoryNames=directories)

model = Model(calculations)
print(model)