from collections import Counter
from itertools import takewhile, tee, starmap

from toolz.curried import *
from toolz.curried.operator import sub, ne


def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def leadspace(line):
    return len(list(takewhile(str.isspace, line)))

def tabdetect(file):
    top = list(filter(ne(0), pluck(0, Counter(starmap(comp(abs, sub),
                                                        pairwise(cons(0, map(leadspace, filter(str.strip, file)))))).most_common(2))))
    return top[0] if top else 1

if __name__ == '__main__':
    with open('./scenes/startup.txt') as file:
        print(tabdetect(file))
