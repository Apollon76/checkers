class GameConfig:
    def __init__(self, start_game=False, black=False, white=False,
                 load_game=False, game_file=None, timer=False, duration=None):
        self.start_game = start_game
        self.black = black
        self.white = white
        self.load_game = load_game
        self.game_file = game_file
        self.timer = timer
        self.duration = duration
