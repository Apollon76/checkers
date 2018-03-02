from tkinter import Tk, Label, Button, PhotoImage, Frame, ttk, Menu, TclError
import tkinter.filedialog
import threading

from src.objects import Objects


class Timer(threading.Thread):
    def __init__(self, interval, func):
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        self.interval = interval
        self.func = func

    def run(self):
        while not self.stopped.wait(self.interval):
            self.func()

    def stop(self):
        self.stopped.set()


class Interface:
    def make_pair(self, pair):
        return lambda: self.make_move(pair)

    @staticmethod
    def make_draught(cur_ceil, color, command, image=None):
        if image is None:
            return Button(cur_ceil, width=70, height=70,
                          bg=color, command=command)
        return Button(cur_ceil, width=70, height=70, image=image,
                      bg=color, command=command)

    class TimerBar:
        def __init__(self, frame, field_width, field_height, game):
            self.timer_update = Timer(0.5, self.show)
            self.timer_bar_frame = Frame(frame, width=190, height=30)
            self.timer_bar_frame.grid(row=0, column=field_width + 1,
                                      columnspan=3)
            self.timer_bar = None
            self.game = game

        def show(self):
            if not self.game.timer1.is_on and not self.game.timer2.is_on:
                return
            text = str(self.game.timer1.get()) + ' ' + str(self.game.timer2.get())
            if self.timer_bar is not None:
                self.timer_bar.destroy()
            self.timer_bar = Label(self.timer_bar_frame, text=text, font=4)
            self.timer_bar.pack()

        def start(self):
            threading.Thread(name='updating_timer', target=self.timer_update.run).start()

        def stop(self):
            self.timer_update.stop()

    class LogBar:
        def __init__(self, frame, field_width, field_height):
            self.log_frame = Frame(frame, width=190, height=30)
            self.log_frame.grid(row=1, column=field_width + 1,
                                columnspan=3, rowspan=field_height)
            self.log_frame.pack_propagate(True)
            self.log = None

        def show(self, lbound, rbound, log):
            text = ''
            for i in range(lbound, rbound + 1):  # something is wrong
                text += str(log[i]) + '\n'
            if self.log is not None:
                self.log.destroy()
            self.log = Label(self.log_frame, text=text, font=4)
            self.log.pack()

    class WaitingBar:
        def __init__(self, frame, field_width, field_height):
            self.val = True
            self.waiting_frame = Frame(frame, width=70, height=30)
            self.waiting_frame.grid(row=field_height + 1, column=4, columnspan=3)
            self.waiting_frame.grid_remove()
            self.waiting_frame.pack_propagate(True)
            self.waiting_message = Label(self.waiting_frame, text='Подождите...', font=8)
            self.waiting_message.pack()

        def show(self, flag):
            if flag:
                self.waiting_frame.grid()
            else:
                self.waiting_frame.grid_remove()

    def __init__(self, cur_game):
        self.root = Tk()
        self.root.title('Шашки')
        self.root.protocol('WM_DELETE_WINDOW', self.quit_program)
        self.width = 900
        self.height = 800
        self.root.minsize(width=self.width, height=self.height)
        self.root.maxsize(width=self.width, height=self.height)
        self.game = cur_game
        self.main_frame = Frame(self.root,
                                width=self.width, height=self.height)
        self.main_frame.grid()
        self.waiting_frame = None
        self.waiting_message = None
        try:
            self.black_draught = PhotoImage(file="img/black_draught.png")
            self.white_draught = PhotoImage(file="img/white_draught.png")
            self.big_black_draught = PhotoImage(file="img/black_draught2.png")
            self.big_white_draught = PhotoImage(file="img/white_draught2.png")
            self.black_king = PhotoImage(file="img/black_king.png")
            self.big_black_king = PhotoImage(file="img/black_king2.png")
            self.white_king = PhotoImage(file="img/white_king.png")
            self.big_white_king = PhotoImage(file="img/white_king2.png")
            self.pictures = {Objects.empty_field: None,
                             Objects.black_draught: self.black_draught,
                             Objects.white_draught: self.white_draught,
                             Objects.black_king: self.black_king,
                             Objects.white_king: self.white_king}
            self.big_pictures = {Objects.empty_field: None,
                                 Objects.black_draught: self.big_black_draught,
                                 Objects.white_draught: self.big_white_draught,
                                 Objects.black_king: self.big_black_king,
                                 Objects.white_king: self.big_white_king}
            self.back_img = PhotoImage(file="img/back.png")
            self.forward_img = PhotoImage(file="img/forward.png")
            self.turn_on_img = PhotoImage(file="img/turn.png")
            self.turn_off_img = PhotoImage(file="img/turning_off.png")
        except IOError:
            message_frame = Frame(self.main_frame,
                                  width=70, height=70)
            message_frame.pack()
            message = Label(message_frame, text='Не получилось загрузить картинки.')
            message.pack()
            self.game.is_over = True
            return
        self.field_height = cur_game.field_height
        self.field_width = cur_game.field_width
        self.field = [[] for i in range(self.field_height)]
        self.touches = 0
        self.cur_move = ()
        self.log_bar = self.LogBar(self.main_frame, self.field_width, self.field_height)
        self.timer_bar = self.TimerBar(self.main_frame, self.field_width,
                                       self.field_height, self.game)
        self.draughts = [[None for j in range(self.field_width)] for i in range(self.field_height)]
        self.elements_for_update = []
        self.turn_mode = True
        self.inverted = self.is_inverted()
        self.init_field()
        self.menu = self.init_menu()
        self.undo_button_frame = self.make_button(self.game.undo, None,
                                                  1, self.field_height + 1, image=self.back_img)
        self.redo_button_frame = self.make_button(self.game.redo, None,
                                                  2, self.field_height + 1, image=self.forward_img)
        self.turn_field_frame = self.make_button(self.change_turn_mode, None,
                                                 3, self.field_height + 1, image=self.turn_on_img)
        self.waiting_bar = self.WaitingBar(self.main_frame, self.field_width, self.field_height)
        self.loading = self.Loading(self.root, self.main_frame, self.width, self.height)

    def init_menu(self):
        menu = Menu(self.root)
        self.root.config(menu=menu)
        game = Menu(menu)
        menu.add_cascade(label='Игра', menu=game)
        game.add_command(label='Новая игра', command=self.new_game)
        game.add_command(label='Загрузить', command=self.new_game)
        if self.game.game_file is None:
            game.add_command(label='Сохранить', command=self.save_game_as)
        else:
            game.add_command(label='Сохранить', command=self.game.save_game)
        game.add_command(label='Сохранить как...', command=self.save_game_as)
        game.add_command(label='Выход', command=self.quit_program)
        return menu

    def save_game_as(self):
        file_name = tkinter.filedialog.asksaveasfilename()
        self.game.save_game(file=file_name)
        if not self.game.game_file is None:
            self.menu.destroy()
            self.menu = self.init_menu()

    def make_button(self, func, text, x, y, image=None):
        cur_frame = Frame(self.main_frame,
                          width=70, height=32)
        cur_frame.grid(row=y, column=x)
        cur_frame.pack_propagate(False)
        if image is None:
            Button(cur_frame, text=text, width=70, command=func).pack()
        else:
            Button(cur_frame, image=image, command=func).pack()
        return cur_frame

    def start(self):
        self.timer_bar.start()
        self.root.mainloop()

    def init_field(self):
        self.draw_field(False)

    def redraw_field(self):
        self.draw_field(True)
        log = self.game.logger.get_log()
        ind = self.game.logger.get_ind()
        self.log_bar.show(max(0, ind - 10), ind, log)
        if self.game.dump_logger.get_ind() + 1 >= len(self.game.dump_logger.get_log()):
            self.redo_button_frame.grid_remove()
        else:
            self.redo_button_frame.grid()

    def draw_field(self, redraw):
        inverted = self.is_inverted()
        for i in range(self.field_height):
            cur_ceil = Frame(self.main_frame,
                             width=30, height=70)
            cur_ceil.grid(row=i, column=0)
            cur_ceil.pack_propagate(False)
            num = i + 1 if inverted else self.field_height - i
            Label(cur_ceil, text=num, font=8).pack()
        for i in range(self.field_width):
            cur_ceil = Frame(self.main_frame,
                             width=70, height=30)
            cur_ceil.grid(row=self.field_height, column=i + 1)
            cur_ceil.pack_propagate(False)
            if not inverted:
                letter = chr(i + ord('a'))
            else:
                letter = chr(self.field_width - i - 1 + ord('a'))
            Label(cur_ceil, text=letter, font=8).pack()
        for i in range(self.field_height):
            for j in range(self.field_width):
                color = 'black' if ((i + j) & 1) == 1 else 'white'
                if inverted:
                    pair = (j, i)
                else:
                    pair = (self.field_width - j - 1, self.field_height - i - 1)
                cur_object = self.game.field_objects[pair[1]][pair[0]]
                if not redraw:
                    cur_ceil = Frame(self.main_frame, bg=color,
                                     width=70, height=70)
                    cur_ceil.grid(row=i, column=j + 1)
                    cur_ceil.pack_propagate(False)
                    self.field[i].append(cur_ceil)
                else:
                    self.draughts[i][j].destroy()
                self.draughts[i][j] = self.make_draught(self.field[i][j], color,
                                                        self.make_pair(pair),
                                                        self.pictures[cur_object])
                self.draughts[i][j].pack()

    def change_turn_mode(self):
        player1 = self.game.player1
        player2 = self.game.player2
        if player1.person and player2.person:
            self.turn_mode = not self.turn_mode
        else:
            self.turn_mode = not self.turn_mode
        self.turn_field_frame.destroy()
        if self.turn_mode:
            self.turn_field_frame = self.make_button(self.change_turn_mode, None,
                                                     3, self.field_height + 1, image=self.turn_on_img)
        else:
            self.turn_field_frame = self.make_button(self.change_turn_mode, None,
                                                     3, self.field_height + 1, image=self.turn_off_img)
        self.redraw_field()

    def is_inverted(self):
        inverted = False
        player1 = self.game.player1
        player2 = self.game.player2
        cur_player = self.game.cur_player
        if player1.person and player2.person:
            if cur_player is player2 and self.turn_mode:
                inverted = True
        elif player2.person:
            if self.turn_mode:
                inverted = True
        return inverted

    def update(self):
        inverted = self.is_inverted()
        if inverted != self.inverted:
            self.redraw_field()
        self.inverted = inverted
        for i in self.elements_for_update:
            y, x = i[0], i[1]
            real_x, real_y = x, y
            if not inverted:
                y = self.field_height - y - 1
                x = self.field_width - x - 1
            pair = (real_x, real_y)
            color = 'black' if (real_y + real_x) % 2 == 1 else 'white'
            cur_object = self.game.field_objects[real_y][real_x]
            if self.draughts[y][x] is not None:
                self.draughts[y][x].destroy()
            self.draughts[y][x] = self.make_draught(self.field[y][x], color,
                                                    self.make_pair(pair),
                                                    self.pictures[cur_object])
            self.draughts[y][x].pack()
        self.elements_for_update.clear()
        self.log_bar.show(max(0, self.game.logger.get_ind() - 10), self.game.logger.get_ind(),
                          self.game.logger.get_log())
        if self.game.dump_logger.get_ind() + 1 >= len(self.game.dump_logger.get_log()):
            self.redo_button_frame.grid_remove()
        else:
            self.redo_button_frame.grid()
        if self.game.is_over:
            message_frame = Frame(self.main_frame, width=70, height=30)
            message_frame.grid(row=self.field_height + 1, column=3, columnspan=3)
            message_frame.pack_propagate(True)
            message = Label(message_frame,
                            text=self.game.checker.state(self.game.cur_player), font=8)
            message.pack()
            self.undo_button_frame.grid_remove()
            self.redo_button_frame.grid_remove()

    def chosen(self, ceil):
        real_x, real_y = ceil
        chosen_object = self.game.field_objects[real_y][real_x]
        if chosen_object.value % 2 != self.game.cur_player.number % 2 \
                or chosen_object == Objects.empty_field:
            return
        self.elements_for_update.append(ceil[::-1])
        inverted = self.is_inverted()
        x, y = real_x, real_y
        if not inverted:
            x = self.field_width - x - 1
            y = self.field_height - y - 1
        color = 'white' if (x + y) % 2 == 0 else 'black'
        self.draughts[y][x].destroy()
        self.draughts[y][x] = self.make_draught(self.field[y][x], color, self.make_pair(ceil),
                                                self.big_pictures[chosen_object])
        self.draughts[y][x].pack()

    def make_move(self, ceil):
        if self.touches >= 2:
            self.touches = 0
            self.cur_move = ()
        self.touches += 1
        if self.touches == 1:
            cur_object = self.game.field_objects[ceil[1]][ceil[0]]
            if cur_object == Objects.empty_field or \
                    cur_object.value % 2 != self.game.cur_player.number % 2:
                self.touches = 0
                return
            self.chosen(ceil)
            self.cur_move = ceil
        if self.touches == 2:
            self.cur_move = (self.cur_move, ceil)
            self.update()

    def get_cur_move(self):
        if self.touches == 2:
            temp = self.cur_move
            self.cur_move = ()
            self.touches = 0
            return temp
        return None

    def quit_program(self):
        self.timer_bar.stop()
        self.game.is_over = True
        self.root.destroy()

    def new_game(self):
        self.quit_program()
        self.game.new_game = True

    class Loading:
        def __init__(self, root, main_frame, width, height):
            self.root = root
            self.main_frame = main_frame
            self.loading_frame = Frame(self.root,
                                       width=width, height=height)
            self.text = Label(self.loading_frame, text='Идёт загрузка...', font=8)
            self.text.pack(padx=width // 2 - 100)
            self.progress_bar = ttk.Progressbar(self.loading_frame, orient="horizontal",
                                                length=200, mode="determinate")
            self.progress_bar.pack(padx=width // 2 - 100)
            self.progress_bar['value'] = 0
            self.progress_bar['maximum'] = 100
            self.showed = False

        def show_loading(self, percent):
            if not self.showed:
                self.main_frame.grid_remove()
                self.loading_frame.grid()
                self.showed = True
            self.progress_bar['value'] = percent

        def loading_failed(self):
            self.text.destroy()
            self.text = Label(self.loading_frame, text='Файл загрузки повреждён!', font=8)
            self.text.pack()
            self.progress_bar.destroy()

        def close_loading(self):
            self.showed = False
            try:
                self.loading_frame.destroy()
            except TclError:
                pass
            self.main_frame.grid()

    @staticmethod
    def incorrect_move():
        '''if self.touches >= 2:
            self.cur_move = self.cur_move[0]
        self.touches = min(self.touches, 1)'''
        pass
