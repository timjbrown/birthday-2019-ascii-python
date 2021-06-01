#!/usr/bin/env python

import os
import time
import sys
from collections import deque

# Windows
if os.name == 'nt':
    import msvcrt

# Posix (Linux, OS X)
else:
    import sys
    import termios
    import atexit
    from select import select

WATER= '░░░░░░░░░░░░▒▓'
FIRE = '░░░▒▒▒▓▓▓'

class Game:
    def __init__(self):
        self.tick = 0
        self.last_tick = 0
        self.name = ''
        self.player = None
        self.level = None

        self.levels = []
        self.companions = []
        self.banners = []

        self.level_index = -1
        self.companion_index = -1
        self.banner_index = -1

        self.num_levels = 8

    def start(self):
        clear()
        self.load_companions()
        self.load_banners()
        self.load_player()
        self.load_levels()
        self.next_level()

        start = time.time()
        kb = KBHit()
        self.print_level()
        while True:
            if kb.kbhit():
                key = kb.getch()
                if ord(key) == 27: # ESC
                    break
                if key == 'n':
                    self.next_level()
                self.move_by_key(key)
                # If the game is over, end the game
                if self.level_index == len(self.levels):
                    break

            # Print the current level every so often
            current = time.time()
            self.tick = int((current - start) / .1) 
            if self.tick > self.last_tick:
                self.print_level()
                self.last_tick = self.tick

        kb.set_normal_term()

    def load_player(self):
        self.name = input('What is your name? ')
        self.player = Player(self.name[0].upper(),0)

    def load_levels(self):
        for i in range(1, self.num_levels + 1):
            board = Level('level' + str(i) + '.txt', i, self)
            self.levels.append(board)

    def load_companions(self):
        filename = resource_path('companions.txt')
        with open(filename, 'r') as f:
            self.companions = f.read().split('\n')

    def load_banners(self):
        filename = resource_path('banners.txt')
        with open(filename, 'r') as f:
            self.banners = f.read().split('\n')
        msg = '       Happy Birthday ' + self.name + '!!!       Use w, a, s, d to move to the Exit E'
        self.banners.insert(0, msg)

    def next_level(self):
        self.last_tick = 0
        self.tick = 0
        self.level_index += 1
        if self.level_index < len(self.levels):
            self.level = self.levels[self.level_index]
            self.player.next_level(self.level.start_row, self.level.start_col)

    def move_by_key(self, key):
        new_row = self.player.row
        new_col = self.player.col
        if key == 'w':
            new_row -= 1
        elif key == 'a':
            new_col -= 1
        elif key == 's':
            new_row += 1
        elif key == 'd':
            new_col += 1
            
        if self.level.board[new_row][new_col] == None:
            self.player.move(new_row, new_col)
        elif type(self.level.board[new_row][new_col]) == Exit:
            self.next_level()
        elif self.level.board[new_row][new_col].can_player_pass(self.player, self.level):
            self.player.move(new_row, new_col)

    def print_level(self):
        clear()
        output = ''
        companion = 0
        for i in range(len(self.level.board)):
            for j in range(len(self.level.board[i])):
                if i == self.player.row and j == self.player.col:
                    output += self.player.get_symbol(self.tick)
                    continue
                
                found = False
                if len(self.player.companions) > 0:
                    for location in self.player.past_locations:
                        if i == location[0] and j == location[1]:
                            output += self.player.companions[companion].symbols[0]
                            companion += 1
                            found = True
                            break

                if not found:
                    if self.level.board[i][j] != None:
                        output += self.level.board[i][j].get_symbol(self.tick)
                    else:
                        output += ' '
            output += '\n'
        print(output)

# Fixes filepaths for development and pyinstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Clear the console
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

class KBHit:
    def __init__(self):
        '''Creates a KBHit object that you can call to do various keyboard things.
        '''

        if os.name == 'nt':
            pass

        else:

            # Save the terminal settings
            self.fd = sys.stdin.fileno()
            self.new_term = termios.tcgetattr(self.fd)
            self.old_term = termios.tcgetattr(self.fd)

            # New terminal setting unbuffered
            self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

            # Support normal-terminal reset at exit
            atexit.register(self.set_normal_term)

    def set_normal_term(self):
        ''' Resets to normal terminal.  On Windows this is a no-op.
        '''

        if os.name == 'nt':
            pass

        else:
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def getch(self):
        ''' Returns a keyboard character after kbhit() has been called.
            Should not be called in the same program as getarrow().
        '''

        if os.name == 'nt':
            return msvcrt.getch().decode('utf-8')

        else:
            return sys.stdin.read(1)

    def getarrow(self):
        ''' Returns an arrow-key code after kbhit() has been called. Codes are
        0 : up
        1 : right
        2 : down
        3 : left
        Should not be called in the same program as getch().
        '''

        if os.name == 'nt':
            msvcrt.getch() # skip 0xE0
            c = msvcrt.getch()
            vals = [72, 77, 80, 75]

        else:
            c = sys.stdin.read(3)[2]
            vals = [65, 67, 66, 68]

        return vals.index(ord(c.decode('utf-8')))

    def kbhit(self):
        ''' Returns True if keyboard character was hit, False otherwise.
        '''
        if os.name == 'nt':
            return msvcrt.kbhit()

        else:
            dr,dw,de = select([sys.stdin], [], [], 0)
            return dr != []

class GameObject:
    def __init__(self, row, col, symbols, start_index, allow_pass=False, left=True):
        self.row = row
        self.col = col
        self.symbols = symbols
        self.start_index = start_index
        self.allow_pass = allow_pass
        self.left = left

    def can_player_pass(self, player, level):
        return self.allow_pass

    def get_symbol(self, tick):
        index = tick + self.start_index
        if not self.left:
            index = self.start_index - tick
        return self.symbols[(index) % len(self.symbols)]

class Companion(GameObject):
    def __init__(self, row, col, symbols, start_index):
        super(Companion, self).__init__(row,col,symbols,start_index)

    def can_player_pass(self, player, level):
        player.companions.append(self)
        level.board[self.row][self.col] = None
        return True

    def get_symbol(self, tick):
        return self.symbols[(tick//2 + self.start_index) % len(self.symbols)]

class Key(GameObject):
    def __init__(self, row, col, symbols, start_index):
        super(Key, self).__init__(row,col,symbols,start_index)

    def can_player_pass(self, player, level):
        player.keys.append(self.symbols)
        level.board[self.row][self.col] = None
        return True

class Door(GameObject):
    def __init__(self, row, col, symbols, start_index):
        super(Door, self).__init__(row,col,symbols,start_index)

    def can_player_pass(self, player, level):
        key = self.symbols[0].lower()
        result = key in player.keys
        if result:
            player.keys.remove(key)
            level.board[self.row][self.col] = None
        return result

class Exit(GameObject):
    def __init__(self, row, col, symbols, start_index):
        super(Exit, self).__init__(row,col,symbols,start_index,allow_pass=True)

class Block(GameObject):
    def __init__(self, row, col, symbols, start_index, allow_pass=False, left=True):
        super(Block, self).__init__(row,col,symbols,start_index,allow_pass,left)

class Player(GameObject):
    def __init__(self, symbols, start_index):
        super(Player, self).__init__(0,0,symbols,start_index)
        self.keys = []
        self.companions = []
        self.past_locations = deque([])

    def move(self, row, col):
        numCompanions = len(self.companions)
        if numCompanions > 0:
            if len(self.past_locations) == numCompanions:
                self.past_locations.popleft()
            self.past_locations.append((self.row,self.col))
        self.row = row
        self.col = col
    
    def next_level(self, row, col):
        self.past_locations = deque([])
        self.row = row
        self.col = col

class Level:
    def __init__(self, filename, index, game):
        self.board = []
        self.index = index
        self.banner_start_index = -1
        self.inside_banner = False
        filename = resource_path(filename)
        with open(filename, 'r') as f:
            for row,line in enumerate(f):
                line = line.replace('\n','')
                self.board.append([])
                for col,letter in enumerate(line):
                    if letter == 'P':
                        self.start_row = row
                        self.start_col = col
                    block = self.create_block(letter,row,col,game)
                    self.board[row].append(block)

    def create_block(self, letter, row, col, game):
        if letter == 'H':
            if not self.inside_banner:
                game.banner_index += 1
                self.banner_start_index = col

            self.inside_banner = True
            msg = game.banners[game.banner_index]
            return Block(row, col, msg, col - self.banner_start_index)
        else:
            self.inside_banner = False

        if letter == ' ':
            return None
        elif letter == 'P':
            return None
        elif letter == 'Q':
            game.companion_index += 1
            msg = game.companions[game.companion_index]
            return Companion(row, col, msg, 0)
        elif letter == 'W':
            return Block(row, col, WATER, col, left=False)
        elif letter == 'F':
            return Block(row, col, FIRE, col, left=False)
        elif letter == 'E':
            return Exit(row, col, letter, 0)
        elif letter in 'ABCD':
            return Door(row, col, letter, 0)
        elif letter in 'abcd':
            return Key(row, col, letter, 0)
        else:
            return Block(row, col, letter, 0)

# Test
def main():
    game = Game()
    game.start()

main()