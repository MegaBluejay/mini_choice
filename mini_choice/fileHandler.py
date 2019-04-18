from itertools import repeat
from random import randint

from termcolor import colored
from toolz.curried import *

from .curried_mods import re
from .lexer import command_detect, parse_file


def padnone(seq):
    return concatv(seq, repeat(None))

def domax(f, v):
    nv = f(v)
    while nv!=v:
        nv = f(v)
    return nv

def handle_file(file, all_vars, achs, io, start_label=None, start_is_sub=None):

    root,\
    labels,\
    hide_reuse\
        = parse_file(file)

    temps = set()
    used = set()

    goto_scene = []
    ret = [[],0]

    def style_printer(match):
        style_type, text = match.groups()
        return colored(text, attrs=['bold' if style_type=='b' else 'dark'])

    def var_printer(match):
        cap, name, index = match.groups()
        var = all_vars[name]
        if cap == '!':
            var = var.capitalize()
        elif cap == '!!':
            var = var.upper()
        if isinstance(var, bool):
            var = 'true' if var else 'false'
        var = str(var)
        if index:
            index = expression_handler(index)
            var = var[index-1]
        return var

    def multi_replacer(match):
        name, choices = match.groups()
        choices = list(map(text_handler, re.split(r'"\|"', choices[1:-1])))
        return choices[all_vars[name]]

    var_detect = re.sub(r'\$(!*){(\w+)(?:#(\d+))?}', var_printer)
    style = re.sub(r'\[([ib])\](.+)\[/\1\]', style_printer)
    multi = re.sub(r'@\{(\w+)\s(.+)\}', multi_replacer)

    extract_vars = re.sub(r'\b(?!(?:length\(|true|false|and|or|not)\b)\w*[a-zA-Z]\w*\b(?=(?:[^"]*"[^"]*")*[^"]*$)',
                          comp(str, lambda v: '"' + v + '"' if isinstance(v, str) else v, all_vars.get, get(0)))

    text_handler = comp(style, multi, var_detect)

    def step(tree, start=0):
        for (line,hsh), children in drop(start, tree.items()):
            if command_detect(line):
                if handle_command(line.split(), children):
                    break
            else:
                io.print_text(text_handler(line))

    def get_value(new):
        if '"' in new or '&' in new:
            new = extract_vars(new)
            new = domax(re.sub(r'\(?(".+)"&"(.+")\)?', r'\1\2'), new)
            return new[1:-1]
        if new.isdigit():
            return int(new)
        if new.lower() in ['true', 'false']:
            return new == 'true'
        return all_vars[new]

    def expression_handler(condition):
        fix_eq = re.sub(r'(?<=\s)=(?=\s)', r'==')
        fix_length = re.sub(r'length\((.+)\)', r'len(\1)')
        fix_truth = re.sub(r'(?i)true|false', comp(str.capitalize, get(0)))
        return eval(pipe(condition, extract_vars, fix_eq, fix_length, fix_truth))

    def handle_command(command_line, args=None):
        command= command_line[0][1:]

        if command in ['choice', 'fake_choice']:
            print_index=0
            relate = {}
            table = []
            for i, sub in enumerate(args):
                choice_line, hsh = sub
                inner=args
                while '#' not in choice_line:
                    inner = inner[sub]
                    sub = list(inner)[0]
                    choice_line += ' '+sub[0]
                opts, choice = choice_line.split('#')
                opts = map(comp(take(2), padnone, curry(str.split)(maxsplit=1)), opts.split('*')[1:])
                choice = text_handler(choice)

                show=1
                grey=0
                for opt, params in opts:
                    if opt=='if':
                        if not expression_handler(params):
                            show = 0
                            break
                    elif opt=='selectable_if':
                        if not expression_handler(params):
                            grey = 1
                    elif opt in ['hide_reuse', 'disable_reuse'] or hide_reuse:
                        if sub in used:
                            if opt=='hide_reuse':
                                show = 0
                            elif opt=='disable_reuse':
                                grey=1
                            break
                        used.add(sub)
                    elif opt=='allow_reuse':
                        used.discard(sub)

                if show:
                    if grey:
                        table.append(['x', choice])
                    else:
                        table.append([print_index, choice])
                        relate[print_index]=i
                        print_index+=1
            io.print_choices(table)
            player_choice=io.get_choice(len(relate))
            step(list(args.items())[relate[player_choice]][1])
            if command=='choice':
                return 1

        elif command in ['goto', 'gosub', 'gotoref']:
            label = command_line[1]
            if command=='gotoref':
                label = get_value(command_line[1])
            step(*labels[label])
            if command=='goto':
                return 1

        elif command=='return':
            return 1

        elif command=='page_break':
            next_text = 'Next'
            if len(command_line)>1:
                next_text=command_line[1]
            io.print_next(next_text)

        elif command in ['set', 'temp', 'create', 'setref']:
            var_name = command_line[1]
            if command=='setref':
                var_name = get_value(var_name)
            if command=='temp':
                temps.add(var_name)
            operator_gex=re.match(r'(%?[+\-*/])(\w+)', ''.join(command_line[2:]))
            if not operator_gex:
                all_vars[var_name] = get_value(' '.join(command_line[2:]))
            else:
                op = operator_gex[1]
                new = get_value(operator_gex[2])
                if len(op)==1:
                    if op=='/':
                        op = '//'
                    exec('all_vars["'+var_name+'"]'+op+'='+str(new))
                else:
                    x=all_vars[var_name]
                    all_vars[var_name] = round(x + (100 - x) * (new / 100))

        elif command=='finish':
            next_chapter_text = 'Next Chapter'
            if len(command_line)>1:
                next_chapter_text = command_line[1]
            io.print_next(next_chapter_text)
            return 1
        elif command in ['if', 'elseif', 'elsif']:
            if expression_handler(' '.join(command_line[1:])):
                step(args)
                return 1

        elif command=='else':
            step(args)
            return 1

        elif command=='rand':
            all_vars[command_line[1]] = randint(*map(int, command_line[-2:]))

        elif command=='delete':
            del all_vars[command_line[1]]

        elif command=='input_text':
            all_vars[command_line[1]] = io.get_text()

        elif command=='input_number':
            all_vars[command_line[1]] = io.get_num(map(int, command_line[-2:]))

        elif command=='link':
            if len(command_line)==2:
                io.print_text(command_line[1])
            else:
                io.print_text(command_line[-1] + '(' + command_line[1] + ')')

        # startup commands

        elif command=='title':
            io.print_text(' '.join(command_line[1:]))

        elif command=='author':
            io.print_text('by ' + ' '.join(command_line[1:]))

        elif command=='scene_list':
            ret[0] = list(args)[0][0].strip().split()

        elif command=='achievement':
            achs[command_line[1]] = command_line[2:5]+[' '.join(command_line[5:])]+list(pluck(0, args))+[0]

        elif command=='achieve':
            achs[command_line[1]][-1]=1
            io.print_achieve(achs[command_line[1]][2], achs[command_line[1]][-2])

        elif command=='goto_scene':
            goto_scene.extend(command_line[1:])
            return 1
        elif command=='gosub_scene':
            _,ret[1] = handle_file(command_line[1], all_vars, achs, io, command_line[1], 1)

        elif command=='ending':
            ret[1]=1
            io.force_print_buffer()
            return 1

        elif command=='stat_chart':
            for i, (type, *stat) in enumerate(map(str.split, pluck(0, args))):
                if type=='text':
                    io.print_stat_text(stat[-1], all_vars[stat[0].lower()])
                elif type=='percent':
                    io.print_stat_bar(stat[-1], all_vars[stat[0].lower()])
                elif type=='opposed_pair':
                    stat2 = pluck(0, args[i])
                    io.print_stat_bar(stat[0] if len(stat2)==1 else stat2[0], all_vars[stat[0].lower()], stat2[-1])

        return 0

    if start_label:
        if start_is_sub:
            handle_command('gosub '+start_label)
        else:
            handle_command('goto '+start_label)
    else:
        step(root)
    for temp in temps:
        del all_vars[temp]

    if goto_scene:
        _,ret[1] = handle_file(goto_scene[0], all_vars, achs, io, *goto_scene[1:])

    return tuple(ret)


if __name__ == '__main__':
    handle_file('scene.txt',{}, {}, None)
