import threading
import time
import queue
import copy

from src.checker import *
from src.gui import Interface
from src.player import Player
from src.objects import Objects
from src.timer import Timer


class Log:
    def __init__(self, who, first, second):
        self.who = 'W' if who.number % 2 == 1 else 'B'
        self.first = first
        self.second = second

    @staticmethod
    def conv(x):
        return chr(10 - x - 1 + ord('a'))

    def __str__(self):
        return '{}: {}{} {}{}'.format(self.who, self.conv(self.first[0]), self.first[1] + 1,
                                      self.conv(self.second[0]), self.second[1] + 1)

    def __repr__(self):
        return '{}:{}, {}'.format(self.who, self.first, self.second)


class Logger:
    def __init__(self):
        self.log = []
        self.ind = -1

    def get_ind(self):
        return self.ind

    def get_log(self):
        return self.log

    def add(self, state):
        while len(self.log) > self.ind + 1:
            self.log.pop()
        self.log.append(state)
        self.ind = len(self.log) - 1

    def undo(self):
        if self.ind >= 0:
            self.ind -= 1

    def empty(self):
        return self.ind > -1

    def get_cur(self):
        return self.log[self.ind]

    def redo(self):
        if self.ind + 1 < len(self.log):
            self.ind += 1


class Game:
    def __init__(self, config=None):
        self.field_width = 10
        self.field_height = 10
        self.field_objects = []
        for j in range(self.field_height):
            self.field_objects.append([Objects.empty_field for i in range(self.field_width)])
        self.checker = Checker(self)
        self.player1 = Player(config.white, 1)
        self.player2 = Player(config.black, 2)
        self.timer1 = Timer(config.timer, config.duration)
        self.timer2 = Timer(config.timer, config.duration)
        self.cur_timer = None
        self.new_game = False
        self.is_first_move = True
        self.is_over = False
        self.cur_figure = None
        self.cur_player = self.player1
        self.cur_move = None
        self.init_field()
        self.was_taken = False
        self.logger = Logger()
        self.dump_logger = Logger()
        self.moves_quantity = 0
        self.game_file = config.game_file
        self.pause = 0.2
        self.load = config.load_game
        self.loaded_moves = queue.Queue()
        self.loaded_moves_amount = 0
        if self.load:
            self.load_moves()
        self.interface = Interface(self)
        # self.interface = ConsoleInterface(self)

    def init_field(self):
        for i in range(self.field_height):
            for j in range(self.field_width):
                color = 'black' if ((i + j) & 1) == 1 else 'white'
                if color == 'black':
                    if i <= 3:
                        self.field_objects[i][j] = Objects.white_draught
                    elif i >= 6:
                        self.field_objects[i][j] = Objects.black_draught

    def read_field(self, file_name):
        text = open(file_name).read().split()
        for i, line in enumerate(text):
            for j, c in enumerate(line):
                cur = int(c)
                if cur == 0:
                    self.field_objects[i][j] = Objects.empty_field
                elif cur == 1:
                    self.field_objects[i][j] = Objects.white_draught
                elif cur == 2:
                    self.field_objects[i][j] = Objects.black_draught
                elif cur == 3:
                    self.field_objects[i][j] = Objects.white_king
                else:
                    self.field_objects[i][j] = Objects.black_king

    def run(self):
        self.dump_logger.add(self.get_dump())
        updating_thread = threading.Thread(name='updating_thread', target=self.update)
        updating_thread.start()
        self.interface.start()
        return self.new_game

    def load_moves(self):
        try:
            with open(self.game_file, 'r') as f:
                self.pause = 0
                white = eval(f.readline().split()[1])
                black = eval(f.readline().split()[1])
                self.player1.person = white
                self.player2.person = black
                lines = []
                for line in f:
                    lines.append(line)
                for line in lines[:-2]:
                    move = line.split(':')
                    move = eval(move[1])
                    self.loaded_moves.put(move)
                    self.loaded_moves_amount += 1
                enable_timer = eval(lines[-2])
                duration = list(map(int, lines[-1].split()))
                self.timer1 = Timer(enable_timer, duration[0])
                self.timer2 = Timer(enable_timer, duration[1])
        except:
            raise Exception('Something wrong with file')

    def next_move(self, player):
        if self.loaded_moves.empty():
            self.finish_loading()
        if self.load:
            return self.loaded_moves.get()
        if player.person:
            return player.make_person_move(self)
        return player.make_bot_move(self)

    def finish_loading(self):
        self.load = False
        self.pause = 0.2
        self.interface.loading.close_loading()

    def update_elements(self, move):
        x1, y1 = move[0][0], move[0][1]
        x2, y2 = move[1][0], move[1][1]
        self.was_taken = False
        self.field_objects[y2][x2] = self.field_objects[y1][x1]
        self.interface.elements_for_update.append((y2, x2))
        self.field_objects[y1][x1] = Objects.empty_field
        self.interface.elements_for_update.append((y1, x1))
        if abs(x2 - x1) >= 2:
            cur_x = x1
            cur_y = y1
            while cur_x + sgn(x2 - x1) != x2:
                cur_x += sgn(x2 - x1)
                cur_y += sgn(y2 - y1)
                if self.field_objects[cur_y][cur_x] != Objects.empty_field:
                    self.was_taken = True
                    self.interface.elements_for_update.append((cur_y, cur_x))
                self.field_objects[cur_y][cur_x] = Objects.empty_field
        if (y2 == 0 and self.field_objects[y2][x2] == Objects.black_draught and
                not self.checker.can_continue(move, self.cur_player)):
            self.field_objects[y2][x2] = Objects.black_king
        if (y2 == self.field_height - 1 and self.field_objects[y2][x2] == Objects.white_draught and
                not self.checker.can_continue(move, self.cur_player)):
            self.field_objects[y2][x2] = Objects.white_king

    def complete_move(self, move):
        self.is_first_move = False
        self.update_elements(move)
        self.cur_figure = move[1]
        self.logger.add(Log(self.cur_player, *move))
        if not self.checker.can_continue(self.cur_move, self.cur_player):
            self.is_first_move = True
            self.was_taken = False
            self.moves_quantity += 1
            if self.moves_quantity % 2 == 0:
                self.cur_player = self.player1
            else:
                self.cur_player = self.player2
        self.dump_logger.add(self.get_dump())
        self.interface.update()

    class State:
        def __init__(self):
            self.field_objects = None
            self.is_first_move = None
            self.is_over = None
            self.cur_figure = None
            self.cur_player = None
            self.cur_move = None
            self.was_taken = None
            self.moves_quantity = None
            self.logger = None

    def get_dump(self):
        dump = self.State()
        dump.field_objects = copy.deepcopy(self.field_objects)
        dump.is_first_move = self.is_first_move
        dump.is_over = self.is_over
        dump.cur_figure = copy.deepcopy(self.cur_figure)
        dump.cur_player = self.cur_player
        dump.cur_move = self.cur_move
        dump.was_taken = self.was_taken
        dump.moves_quantity = self.moves_quantity
        dump.logger = copy.deepcopy(self.logger)
        return dump

    def init_by_dump(self, config):
        self.field_objects = copy.deepcopy(config.field_objects)
        self.is_first_move = config.is_first_move
        self.is_over = config.is_over
        self.cur_figure = copy.deepcopy(config.cur_figure)
        self.cur_player = config.cur_player
        self.cur_move = config.cur_move
        self.was_taken = config.was_taken
        self.moves_quantity = config.moves_quantity
        self.logger = copy.deepcopy(config.logger)

    def undo(self):
        if self.player1.person and self.player2.person:
            if self.dump_logger.get_ind() > 0:
                self.dump_logger.undo()
                self.init_by_dump(self.dump_logger.get_cur())
        elif self.cur_player.person:
            dump = self.dump_logger.get_log()
            ind = self.dump_logger.get_ind() - 1
            while ind > 0 and dump[ind].cur_player != self.cur_player:
                ind -= 1
            if ind >= 0 and dump[ind].cur_player == self.cur_player:
                self.dump_logger.undo()
                while self.dump_logger.get_cur().cur_player != self.cur_player:
                    self.dump_logger.undo()
                self.init_by_dump(self.dump_logger.get_cur())
        self.interface.redraw_field()

    def redo(self):
        if self.player1.person and self.player2.person:
            self.dump_logger.redo()
            self.init_by_dump(self.dump_logger.get_cur())
        else:
            dump = self.dump_logger.get_log()
            ind = self.dump_logger.get_ind() + 1
            while ind + 1 < len(dump) and dump[ind].cur_player != self.cur_player:
                ind += 1
            if ind < len(dump) and dump[ind].cur_player == self.cur_player:
                self.dump_logger.redo()
                while self.dump_logger.get_cur().cur_player != self.cur_player:
                    self.dump_logger.redo()
                self.init_by_dump(self.dump_logger.get_cur())
        self.interface.redraw_field()

    def update(self):
        self.moves_quantity = 0
        self.is_first_move = True
        while True:
            if self.load:
                if self.loaded_moves_amount != 0:
                    self.interface.loading.show_loading(
                        int(self.moves_quantity / self.loaded_moves_amount * 100)
                    )
                else:
                    self.interface.loading.show_loading(100)
            time.sleep(self.pause)
            if self.is_over:
                break
            if not self.cur_player.person:
                self.interface.waiting_bar.show(True)
            else:
                self.interface.waiting_bar.show(False)
            self.checker.make_graph(self.cur_player)
            if self.cur_player.number == 1:
                self.cur_timer = self.timer1
            else:
                self.cur_timer = self.timer2
            self.cur_timer.start()
            self.cur_move = self.cur_player.make_move(self)
            if self.checker.is_move_correct(self.cur_move, self.cur_player):
                self.cur_timer.stop()
                self.complete_move(self.cur_move)
            else:
                if self.load:
                    self.interface.loading.loading_failed()  # show message, that downloading is incorrect
                    break
                self.interface.incorrect_move()
            self.cur_timer = None
            if self.checker.state(self.cur_player) != '':
                self.timer1.stop()
                self.timer2.stop()
                self.interface.waiting_bar.show(False)
                self.is_over = True
                self.interface.update()
                break

    def save_game(self, file=None):
        if file is None:
            file = self.game_file
        else:
            self.game_file = file
        try:
            f = open(file, 'w')
        except FileNotFoundError:
            return
        f.write('white ' + str(self.player1.person) + '\n')
        f.write('black ' + str(self.player2.person) + '\n')
        for i in self.logger.get_log()[:self.logger.get_ind()]:
            f.write(repr(i) + '\n')
        f.write(str(self.timer1.is_on) + '\n')
        f.write('{} {}\n'.format(str(self.timer1.get()), str(self.timer2.get())))
        f.close()
