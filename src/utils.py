from functools import reduce


def compose(*funcs):
    return lambda x: reduce(lambda v, f: f(v), reversed(funcs), x)
