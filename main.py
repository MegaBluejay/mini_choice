import argparse as ap
from glob import iglob

from toolz.curried import *

from fileHandler import handle_file
from test import IO

parser = ap.ArgumentParser()
parser.add_argument('dir', type=str, nargs='?', default='../scenes')
scenes_location = parser.parse_args().dir
if scenes_location[-1]=='/':
    scenes_location=scenes_location[:-1]

for path in iglob(scenes_location+'/*'):
    with open(path, 'r+') as scene:
        if scene.read()[-1]!='\n':
            scene.write('\n')

global_vars = {}
achs = {}
io = IO(curry(handle_file)('choicescript_stats.txt', global_vars, achs))
scene_list, end = handle_file('startup.txt', global_vars, achs, io)
if not end:
    for scene in scene_list[1:]:
        _, end = handle_file(scene+'.txt', global_vars, achs, io)
        if end:
            break
