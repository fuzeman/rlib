import code
from rlib import Reddit

if __name__ == '__main__':
    r = Reddit()

    vars = globals().copy()
    vars.update(locals())

    shell = code.InteractiveConsole(vars)
    shell.interact()
