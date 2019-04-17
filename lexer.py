from collections import OrderedDict, deque
from functools import reduce
from itertools import groupby as sequencial_groupby, dropwhile

from toolz.curried import *

from curried_mods import re
from tabdetect import tabdetect


def file_loc(filename):
    return './scenes/'+filename

re.match = curry(re.match)
re.sub = curry(re.sub)

class Tree(OrderedDict):
    pass

def start_space(line):
    return re.match(r'^\s*', line)[0]

def tablen(line, n=2):
    return len(start_space(line))//n

command_detect = re.match(r'^\s*[*#](?!line_break)')

def parse_file(file):
    if isinstance(file, str):
        if not file.endswith('.txt'):
            file+='.txt'
        file = open(file_loc(file))

    f = list(file)
    file.close()
    file = f
    stuff=[]

    n = tabdetect(file)

    def joined_text_lines():
        for is_command, group in sequencial_groupby(file, key=command_detect):
            if is_command:
                for line in group:
                    if line.lstrip().split()[0]!='*comment':
                        yield line[:-1]
            else:
                def line_breaker(b):
                    return b[:-1].lstrip() in ['*line_break','']
                group = list(dropwhile(line_breaker, group))
                if group:
                    q = group[0]
                    def combiner(a, b):
                        if line_breaker(b):
                            return a+'\n'
                        b = b[:-1].lstrip()
                        if not a or a.endswith('\n'):
                            return a+b
                        return a+' '+b
                    big_line = reduce(combiner, group, '')
                    if big_line.strip():
                        yield start_space(q)+big_line

    for line in joined_text_lines():
        stuff.append((line.lstrip(), tablen(line, n)))

    root = Tree()
    labels = {}
    c_tree = root
    temp_queue = deque()
    hide_reuse=0
    for i, (q, tab) in enumerate(stuff):
        if q.split()[0]=='*label':
            labels[q.split()[1]] = (c_tree, len(c_tree))
        elif q=='*hide_reuse':
            hide_reuse=1
        else:
            c_tree[(q,i)] = Tree()
            if i!=len(stuff)-1 and stuff[i+1][1]>tab:
                temp_queue.append(c_tree)
                c_tree = c_tree[(q,i)]
            elif i!=len(stuff)-1 and stuff[i+1][1]<tab:
                for _ in range((tab-stuff[i+1][1])):
                    c_tree = temp_queue.pop()

    return root, labels, hide_reuse

if __name__ == '__main__':
    from pprint import pprint
    pprint(parse_file('startup.txt'))
