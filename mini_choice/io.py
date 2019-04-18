from textwrap import fill

from tabulate import tabulate


class IO:
    
    def __init__(self, stats_call):
        self.buffer = []
        self.button_text = 'stats'
        self.stats_call = stats_call

    def print_text(self, text):
        self.buffer.append(fill(text))

    def print_choices(self, choice_table):
        self.buffer.append(tabulate(choice_table, tablefmt='presto'))

    def print_next(self, next_text):
        self.buffer.append(next_text)
        print('\n'.join(self.buffer))
        inp = input()
        while inp==self.button_text:
            self.button()
            print('\n'.join(self.buffer))
            inp = input()
        self.buffer = []
    
    def button(self):
        if self.button_text=='stats':
            buf = self.buffer
            self.buffer = []
            self.button_text = 'back'
            self.stats_call(self)
            self.buffer = buf
            self.button_text = 'stats'

    def print_stat_bar(self, name_l, val, name_r=None):
        self.buffer.append(name_l+' '+'+'*(val//2)+'-'*(50-val//2)+(name_r if name_r else ''))

    def print_stat_text(self, name, val):
        self.buffer.append(name+': '+str(val))

    def print_achieve(self, name, text):
        print(name+': '+text)

    def get_choice(self, mx):
        print('\n'.join(self.buffer))
        t=''
        while not t.isdigit() or int(t) not in range(mx):
            t = input()
            if t==self.button_text:
                self.button()
                print('\n'.join(self.buffer))
        self.buffer = []
        return int(t)

    def get_text(self):
        print('\n'.join(self.buffer))
        inp = input()
        while inp==self.button_text:
            self.button()
            print('\n'.join(self.buffer))
        self.buffer = []
        return inp

    def get_num(self, bounds):
        print('\n'.join(self.buffer))
        t=''
        while not t.isdigit() or int(t) not in range(*bounds):
            t = input()
            if t==self.button_text:
                self.button()
                print('\n'.join(self.buffer))
        self.buffer = []
        return int(t)

    def force_print_buffer(self):
        print('\n'.join(self.buffer))
        self.buffer = []
