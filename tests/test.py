from calc import setupCalculations


calculations = setupCalculations('soc', generalSettings='HF')
# TODO: fix directories
# see this failure: calculations = setupCalculations(['HF'], generalSettings='HF')

for calculation in calculations:
    print(calculation)
