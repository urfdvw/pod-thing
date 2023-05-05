import builtins
builtins.print('{coi-script-start}', end='')
def input(arg):
    result = builtins.input(arg + '{coi-serial-input-start}')
    builtins.print('{coi-serial-input-end}', end='')
    return result