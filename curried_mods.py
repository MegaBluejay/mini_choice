import re
import types

from toolz import curry

mods=[re]

for mod in mods:
    for attr in mod.__dict__:
        obj = getattr(re, attr)
        if isinstance(obj, types.FunctionType):
            setattr(re, attr, curry(obj))
