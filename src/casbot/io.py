from casbot.settings import Keyword, Block,\
    cellKnown, cellTypes, cellValues, cellUnits,\
    paramKnown, paramTypes, paramValues, paramUnits,\
    shortcutToCells, shortcutToCellsAliases, shortcutToParams, shortcutToParamsAliases,\
    stringToVariableSettings

from difflib import SequenceMatcher


def help(*args):
    if not args:
        return

    assert all(type(key) is str and key for key in args), 'Enter a string to find help about'

    def printShortcut(shrtct):
        longestKey = 0
        longestValue = 0

        for s in shrtct:
            if type(s) is tuple:
                for s2 in s:
                    longestKey = max(len(s2.key), longestKey)
                    longestValue = max(len(str(s2)), longestValue)
            else:
                longestKey = max(len(s.key), longestKey)
                longestValue = max(len(str(s)), longestValue)

        for s in shrtct:
            if type(s) is tuple:
                print('')

                leftBorder = ['/'] + ['|'] * (len(s) - 2) + ['\\']
                rightBorder = ['\\'] + ['|'] * (len(s) - 2) + ['/']

                for lB, s2, rB in zip(leftBorder, s, rightBorder):
                    print(f'{lB} {s2.key:>{longestKey}} : {str(s2):<{longestValue}} {rB}')

            else:
                print(f'  {s.key:>{longestKey}} : {s}')

    for key in args:
        key = key.strip().lower()

        print('')

        if key in cellKnown:
            print(f'{key} is a cell ->')
            print(f'    type: {cellTypes.get(key)}')
            print(f'  values: {cellValues.get(key)}')
            print(f'   units: {cellUnits.get(key)}')
            print('')

        if key in paramKnown:
            print(f'{key} is a param ->')
            print(f'    type: {paramTypes.get(key)}')
            print(f'  values: {paramValues.get(key)}')
            print(f'   units: {paramUnits.get(key)}')
            print('')

        if key in shortcutToCells or key in shortcutToCellsAliases or key in shortcutToParams or key in shortcutToParamsAliases:
            shortcut = (shortcutToCells | shortcutToCellsAliases | shortcutToParams | shortcutToParamsAliases).get(key)

            if isinstance(shortcut, Keyword):
                print(f'{key} is a shortcut to the keyword {shortcut.key} ->')
                print(f'  {shortcut}')

            elif isinstance(shortcut, Block):
                print(f'{key} is a shortcut to the block {shortcut.key} ->')
                print(f'%block {shortcut.key}')
                print('\n'.join(shortcut.getLines()))
                print(f'%endblock {shortcut.key}')

            else:
                print(f'{key} is a shortcut to multiple settings ->')

                printShortcut(shrtct=shortcut)

            print('')

        if key in stringToVariableSettings:
            print(f'{key} is a variable shortcut to multiple settings ->')

            printShortcut(shrtct=stringToVariableSettings.get(key))

            print('')


def search(key=None):
    assert type(key) is str and key, 'Enter a string to search for'

    def f(lst, title):
        hits = []

        for var in lst:
            ratio = SequenceMatcher(a=key, b=var).ratio()

            if ratio == 1.0:
                #help(key=key)
                #return

                #hits = [var]
                #break

                hits.append(var)

            elif ratio >= 0.5:
                hits.append(var)

        if len(hits) > 0:
            print(f'{title}:')

            for h in hits:
                print(f'  {h}')

            return True

        else:
            return False

    key = key.strip().lower()

    hit = f(lst=cellKnown, title='cells')

    if hit: print('')

    hit = f(lst=paramKnown, title='params')

    if hit: print('')

    hit = f(lst=(list(shortcutToCells) +
                 list(shortcutToCellsAliases) +
                 list(shortcutToParams) +
                 list(shortcutToParamsAliases)), title='shortcuts')

    if hit: print('')

    hit = f(lst=list(stringToVariableSettings), title='variable settings')

    if hit: pass
