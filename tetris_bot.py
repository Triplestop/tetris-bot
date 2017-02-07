#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# NOTE FOR WINDOWS USERS:
# You can download a "exefied" version of this game at:
# http://kch42.de/progs/tetris_py_exefied.zip
# If a DLL is missing or something like this, write an E-Mail (kevin@kch42.de)
# or leave a comment on this gist.

# Bot built to play tetris. Tetris version slightly modified from original.

# Copyright (c) 2010 "Kevin Chabowski"<kevin@kch42.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from random import randrange as rand
import pygame, sys, copy, random

# The configuration -- if changed, the bot will not run effectively
cell_size = 18
cols =      10
rows =      22
maxfps =    1000000000

# Parameter weights
p = [0.540741463,	0.772309762,	0.138407042,	0.123304519,	0.160072183,	0.235053171,	0.215006496]

colors = [
(0,   0,   0  ),
(255, 85,  85 ),
(100, 200, 115),
(120, 108, 245),
(255, 140, 50 ),
(50,  120, 52 ),
(146, 202, 73 ),
(150, 161, 218),
(35,  35,  35 ) # Helper color for background grid
]

# Define the shapes of the single parts
tetris_shapes = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

    [[7, 7],
     [7, 7]]
]

printed = False

def rotate_clockwise(shape):
    return [[ shape[y][x] for y in range(len(shape))] for x in range(len(shape[0]) - 1, -1, -1)]

def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[ cy + off_y ][ cx + off_x ]:
                    return True
            except IndexError:
                return True
    return False

def remove_row(board, row):
    del board[row]
    return [[0 for i in range(cols)]] + board

def join_matrices(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy + off_y - 1][cx + off_x] += val
    return mat1

def new_board():
    board = [[ 0 for x in range(cols)] for y in range(rows)]
    board += [[ 1 for x in range(cols)]]
    return board

class TetrisBot(object):
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(250, 25)
        printed = False
        self.piece_counter = 1
        self.piece_count = 0
        self.piece_lst = [0, 1, 2, 3, 4, 5, 6]
        random.shuffle(self.piece_lst)
        self.width = cell_size * (cols + 6)
        self.height = cell_size * rows
        self.rlim = cell_size * cols
        self.bground_grid = [[8 if x % 2 == y % 2 else 0 for x in range(cols)] for y in range(rows)]

        self.default_font = pygame.font.Font(pygame.font.get_default_font(), 12)

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.event.set_blocked(pygame.MOUSEMOTION) # We do not need mouse movement
                                                     # events, so we block them.
        self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
        self.init_game()

    def run_test(self, lateral, rotation):
        Test = TetrisEval(tetris_shapes.index(self.stone), self.board, lateral, rotation, self.level)
        return Test.run()

    def new_stone(self):
        self.stone = self.next_stone[:]
        self.next_stone = tetris_shapes[self.piece_lst[self.piece_count]]
        self.piece_counter += 1
        self.piece_count += 1
        if self.piece_count > 6:
            random.shuffle(self.piece_lst)
            self.piece_count = 0
        self.stone_x = int(cols / 2 - len(self.stone[0]) / 2)
        self.stone_y = 0

        if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
            self.gameover = True

    def init_game(self):
        self.board = new_board()
        self.new_stone()
        self.need_eval = True
        self.level = 1
        self.score = 0
        self.lines = 0
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)

    def disp_msg(self, msg, topleft):
        x, y = topleft
        for line in msg.splitlines():
            self.screen.blit(self.default_font.render(line, False, (255, 255, 255), (0, 0, 0)), (x, y))
            y += 14

    def center_msg(self, msg):
        for i, line in enumerate(msg.splitlines()):
            msg_image =  self.default_font.render(line, False, (255, 255, 255), (0, 0, 0))

            msgim_center_x, msgim_center_y = msg_image.get_size()
            msgim_center_x //= 2
            msgim_center_y //= 2

            self.screen.blit(msg_image, (self.width // 2 - msgim_center_x, self.height // 2 - msgim_center_y + i * 22))

    def draw_matrix(self, matrix, offset):
        off_x, off_y = offset
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(
                        self.screen,
                        colors[val],
                        pygame.Rect(
                            (off_x+x) *
                              cell_size,
                            (off_y+y) *
                              cell_size,
                            cell_size,
                            cell_size),0)

    def add_cl_lines(self, n):
        linescores = [0, 40, 100, 300, 1200]
        self.lines += n
        self.score += linescores[n] * self.level
        if self.lines >= self.level*6:
            self.level += 1
            newdelay = 1000-50*(self.level-1)
            newdelay = 100 if newdelay < 100 else newdelay
            pygame.time.set_timer(pygame.USEREVENT+1, newdelay)

    def move(self, delta_x):
        if not self.gameover and not self.paused:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > cols - len(self.stone[0]):
                new_x = cols - len(self.stone[0])
            if not check_collision(self.board, self.stone, (new_x, self.stone_y)):
                self.stone_x = new_x
    def quit(self):
        self.center_msg("Exiting...")
        pygame.display.update()
        sys.exit()

    def drop(self, manual):
        if not self.gameover and not self.paused:
            self.score += 1 if manual else 0
            self.stone_y += 1
            if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
                self.board = join_matrices(self.board, self.stone, (self.stone_x, self.stone_y))
                self.new_stone()
                self.need_eval = True
                cleared_rows = 0
                while True:
                    for i, row in enumerate(self.board[:-1]):
                        if 0 not in row:
                            self.board = remove_row(
                              self.board, i)
                            cleared_rows += 1
                            break
                    else:
                        break
                self.add_cl_lines(cleared_rows)
                return True
        return False

    def insta_drop(self):
        if not self.gameover and not self.paused:
            while(not self.drop(True)):
                pass

    def rotate_stone(self):
        if not self.gameover and not self.paused:
            new_stone = rotate_clockwise(self.stone)
            if not check_collision(self.board,
                                   new_stone,
                                   (self.stone_x, self.stone_y)):
                self.stone = new_stone

    def toggle_pause(self):
        self.paused = not self.paused

    def start_game(self):
        if self.gameover:
            self.init_game()
            self.gameover = False

    def run(self):
        key_actions = {
            'ESCAPE':   self.quit,
            'LEFT':     lambda:self.move(-1),
            'RIGHT':    lambda:self.move(+1),
            'DOWN':     lambda:self.drop(True),
            'UP':       self.rotate_stone,
            'p':        self.toggle_pause,
            'SPACE':    self.start_game,
            'RETURN':   self.insta_drop
        }

        self.gameover = False
        self.paused = False
        self.need_eval = True

        dont_burn_my_cpu = pygame.time.Clock()
        while 1:
            self.screen.fill((0,0,0)) #screen is a Surface, created in __init__
            if self.gameover:
                if not printed:
                    print("Final score: ", self.score,"\nLines cleared:", self.lines)
                    self.printed = True
                self.center_msg("""Game Over!\nYour score: %d
Press space to continue""" % self.score)
            else:
                if self.paused:
                    self.center_msg("Paused")
                else:
                    pygame.draw.line(self.screen,
                        (255,255,255),
                        (self.rlim+1, 0),
                        (self.rlim+1, self.height-1))
                    self.disp_msg("Next:", (
                        self.rlim+cell_size,
                        2))
                    self.disp_msg("Score: %d\n\nLevel: %d\
\nLines: %d" % (self.score, self.level, self.lines),
                        (self.rlim+cell_size, cell_size*5))
                    self.draw_matrix(self.bground_grid, (0,0))
                    self.draw_matrix(self.board, (0,0))
                    self.draw_matrix(self.stone,
                        (self.stone_x, self.stone_y))
                    self.draw_matrix(self.next_stone,
                        (cols+1,2))
            pygame.display.update()

            if self.need_eval:
                self.need_eval = False
                test_score = -9999999
                lateral = 0
                rotation = 0
                for i in range(-4, 7):
                    for j in range(4):
                        temp = self.run_test(i, j)
                        if temp > test_score:
                            test_score = temp
                            lateral = i
                            rotation = j

                for k in range(0, rotation):
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key = pygame.K_UP))
                if lateral < 0:
                    for m in range(0, -lateral):
                        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key = pygame.K_LEFT))
                elif lateral > 0:
                    for m in range(0, lateral):
                        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key = pygame.K_RIGHT))
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key = pygame.K_RETURN))

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT+1:
                    self.drop(False)
                elif event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    for key in key_actions:
                        if event.key == eval("pygame.K_"
                        +key):
                            key_actions[key]()

            dont_burn_my_cpu.tick(maxfps)

class TetrisEval(TetrisBot):
    def __init__(self, shape_num, test_board, test_lat, test_rot, start_level):
        pygame.init()
        self.lateral = copy.copy(test_lat)
        self.rotation = copy.copy(test_rot)
        self.width = cell_size * (cols+6)
        self.height = cell_size * rows
        self.rlim = cell_size * cols
        self.bground_grid = [[8 if x % 2 == y % 2 else 0 for x in range(cols)] for y in range(rows)]

        pygame.event.set_blocked(pygame.MOUSEMOTION) # We do not need
                                                     # mouse movement
                                                     # events, so we
                                                     # block them.
        self.next_stone = tetris_shapes[shape_num]
        self.init_game(test_board, start_level)

    def init_game(self, test_board, start_level):
        self.piece_counter = 1
        self.piece_count = 0
        self.piece_lst = [0, 1, 2, 3, 4, 5, 6]
        self.start_board = test_board
        self.board = copy.deepcopy(test_board)
        self.new_stone()
        self.need_eval = False
        self.level = copy.copy(start_level)
        self.score = 0
        self.lines = 0

    def run(self):
        key_actions = {
            'ESCAPE':   self.quit,
            'LEFT':     lambda:self.move(-1),
            'RIGHT':    lambda:self.move(+1),
            'DOWN':     lambda:self.drop(True),
            'UP':       self.rotate_stone,
            'p':        self.toggle_pause,
            'SPACE':    self.start_game,
            'RETURN':   self.insta_drop
        }

        self.gameover = False
        self.paused = False
        self.need_eval = False

        dont_burn_my_cpu = pygame.time.Clock()
        while 1:
            if self.gameover:
                return -9999999
            if self.need_eval:
                # for y, row in enumerate(self.board):
                #     for x, val in enumerate(row):
                #         print(val, end = "")
                #     print()
                # print()

                #height of highest piece
                for y, row in enumerate(self.board):
                    found = False
                    for x, val in enumerate(row):
                        if val != 0:
                            stack_height = rows - y
                            found = True
                    if found:
                        break

                #edge and bottom touch counter
                edge_counter = 0
                adj_counter = 0
                pos_board = [[self.board[y][x] - self.start_board[y][x] for x in range(cols)] for y in range(rows)]
                for y, row in enumerate(pos_board):
                    for x, val in enumerate(row):
                        if not self.lines:
                            if pos_board[y][x]:
                                if y >= 1 and self.start_board[y - 1][x]:
                                    adj_counter += 1
                                if x >= 1 and self.start_board[y][x - 1]:
                                    adj_counter += 1
                                if x < cols - 1 and self.start_board[y][x + 1]:
                                    adj_counter += 1
                            if x == 0 or x == rows - 1:
                                edge_counter += 1
                            if cols - y == 1:
                                adj_counter = 0

                #height counter
                piece_height = 0
                for y, row in enumerate(self.board):
                    for x, val in enumerate(row):
                        if self.board[y][x]:
                            piece_height += rows - y

                #hole and blockade counter
                counter = [[False, 0, False, 0] for x in range(cols)]
                for y, row in enumerate(self.board):
                    for x, val in enumerate(row):
                        if val:
                            if not counter[x][0]:
                                counter[x][0] = True
                                counter[x][3] = y
                        elif counter[x][0]:
                            counter[x][1] += 1
                            counter[x][2] = True
                hole_count = 0
                blockade_count = 0
                for x in range(cols):
                    hole_count += counter[x][1]
                for x in range(cols):
                    if counter[x][2]:
                        blockade_count = rows - counter[x][3] - counter[x][1]

                final_score = p[0] * self.lines - p[1] * hole_count - p[2] * blockade_count - p[3] * piece_height + p[4] * edge_counter + p[5] * adj_counter + p[6] * self.score
                return final_score

            for k in range(0, self.rotation):
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key = pygame.K_UP))
            if self.lateral < 0:
                for m in range(0, -self.lateral):
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key = pygame.K_LEFT))
            elif self.lateral > 0:
                for m in range(0, self.lateral):
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key = pygame.K_RIGHT))
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key = pygame.K_RETURN))

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT+1:
                    self.drop(False)
                elif event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    for key in key_actions:
                        if event.key == eval("pygame.K_"
                        +key):
                            key_actions[key]()

            dont_burn_my_cpu.tick(maxfps)

if __name__ == '__main__':
    App = TetrisBot()
    App.run()
