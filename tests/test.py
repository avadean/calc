from casbot import Model, Setting,\
    createCalculations, createDirectories, createSettings, createVariableSettings,\
    processCalculations


directories = createDirectories(['HF', 'HCl'])
settings = createSettings('hyperfine', 'soc')
variableSettings = createVariableSettings(['HF', 'HCl'])

calculations = createCalculations(*variableSettings,
                                  #globalSettings=settings,
                                  directoryNames=directories,
                                  withDefaults=True)


# TODO: add in additionalSettings to processCalculations to get the settings but add new ones

#calculations = processCalculations(['HF', 'HCl'], 'soc')

model = Model(calculations)
print(model)


#model.create(force=True)

#model.sub(test=True)
#model.sub()
