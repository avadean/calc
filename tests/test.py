from calc import setupCalculations, Setting


calculations = setupCalculations('soc', 'density',
                                 generalSettings=['HF', 'shielding', Setting('spin', 0.3)])
# TODO: fix directories
# see this failure: calculations = setupCalculations(['HF'], generalSettings='HF')

for calculation in calculations:
    print(calculation)
