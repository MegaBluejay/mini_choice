import argparse as ap
from glob import iglob
import signal
import sys

from toolz.curried import *

from .fileHandler import handle_file
from .mio import IO

def main():
    parser = ap.ArgumentParser()
    parser.add_argument('dir', type=str, nargs='?', default='./scenes')
    scenes_location = parser.parse_args().dir
    if scenes_location[-1]=='/':
        scenes_location=scenes_location[:-1]

    for path in iglob(scenes_location+'/*'):
        with open(path, 'r+') as scene:
            if scene.read()[-1]!='\n':
                scene.write('\n')

    signal.signal(signal.SIGINT, lambda _0,_1: sys.exit(1))

    global_vars = {}
    achs = {}
    io = IO(curry(handle_file)('choicescript_stats.txt', global_vars, achs))
    scene_list, end = handle_file('startup.txt', global_vars, achs, io,scenes_location)
    if not end:
        for scene in scene_list[1:]:
            _, end = handle_file(scene+'.txt', global_vars, achs, io,scenes_location)
            if end:
                break

if __name__ == '__main__':
    main()
