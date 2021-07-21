from calc import Model, setupCalculations, Setting


calculations = setupCalculations(['HF', 'HCl'], 'zbfield',
                                 globalSettings=['shielding', 'soc',
                                                 Setting('iprint', 3)],
                                 directories=[['HF', 'HCl'],
                                              'zbfield'])
# TODO: fix directories
# see this failure: calculations = setupCalculations(['HF'], generalSettings='HF')


model = Model(calculations)
