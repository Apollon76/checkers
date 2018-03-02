from tkinter import Tk, Button, Frame
import tkinter.filedialog

from src import gameconfig


class Menu:
    def __init__(self):
        self.root = Tk()
        self.root.title('Шашки')
        self.root.minsize(width=200, height=300)
        self.root.maxsize(width=200, height=300)
        self.config = gameconfig.GameConfig()
        self.buttons = []
        self.make_button('Играть чёрными', 70, self.play_black)
        self.make_button('Играть белыми', 70, self.play_white)
        self.make_button('Два игока', 70, self.two_players)
        self.make_button('Загрузить игру', 70, self.load)
        self.make_button('Выход', 70, self.quit)

    def run(self):
        self.root.mainloop()

    def make_button(self, text, width, command):
        button_frame = Frame(self.root, bg='white',
                             width=100, height=30)
        button_frame.pack()
        button = Button(button_frame, text=text, width=width, command=command)
        button.pack()
        self.buttons.append(button)
        self.buttons.append(button_frame)

    def quit(self):
        self.root.destroy()
        self.config.start_game = False

    def play_black(self):
        self.config.black = True
        self.config.start_game = True
        self.root.destroy()
        self.timer_switch()

    def play_white(self):
        self.config.white = True
        self.config.start_game = True
        self.root.destroy()
        self.timer_switch()

    def two_players(self):
        self.config.black = True
        self.config.white = True
        self.config.start_game = True
        self.root.destroy()
        self.timer_switch()

    def timer_on(self, duration=None):
        if duration is not None:
            duration = duration.get()
        else:
            duration = 60 * 5
        try:
            duration = int(duration)
        except ValueError:
            duration = 60 * 5
        self.config.timer = True
        self.config.duration = duration
        self.root.destroy()

    def timer_off(self):
        self.config.timer = False
        self.root.destroy()

    def timer_switch(self):
        self.root = Tk()
        self.root.title('Играть на время?')
        self.root.minsize(width=200, height=210)
        self.root.maxsize(width=200, height=210)
        question_frame = Frame(self.root,
                               width=200, height=70)
        question_frame.pack()
        message = tkinter.Label(question_frame, text='Do you want to play with timer?')
        message.pack()
        duration = tkinter.Entry(question_frame)
        duration.insert(0, '300')
        duration.pack()
        self.make_button('Yes', 70, lambda: self.timer_on(duration))
        self.make_button('No', 70, self.timer_off)
        self.root.mainloop()

    def load(self):
        self.config.game_file = tkinter.filedialog.askopenfilename()
        if self.config.game_file == '':
            return
        self.config.load_game = True
        self.config.start_game = True
        self.root.destroy()
