class ConsoleInterface:
    def __init__(self, cur_game):
        self.game = cur_game
        self.field_height = cur_game.field_height
        self.field_width = cur_game.field_width
        self.touches = 2
        self.cur_move = None
        self.elements_for_update = []
        for i in range(self.field_height):
            print(i + 1, end=' ')
            if i < 9:
                print(' ', end='')
            for j in range(self.field_width):
                print(self.game.field_objects[i][j].value, end='')
            print()
        print('   ', end='')
        for i in range(self.field_width):
            print(chr(i + ord('a')), end='')
        print()

    def start(self):
        pass

    @staticmethod
    def show_wait(flag):
        if flag:
            print('Подождите...')

    @staticmethod
    def conv(pair):
        return chr(pair[0] + ord('a')) + str(pair[1] + 1)

    def update(self):
        print(self.conv(self.game.cur_move[0]), self.conv(self.game.cur_move[1]))
        for i in range(self.field_height):
            print(i + 1, end=' ')
            if i < 9:
                print(' ', end='')
            for j in range(self.field_width):
                print(self.game.field_objects[i][j].value, end='')
            print()
        print('   ', end='')
        for i in range(self.field_width):
            print(chr(i + ord('a')), end='')
        print()
        self.elements_for_update.clear()

    @staticmethod
    def conv_to_num(pos):
        return ord(pos[0]) - ord('a'), int(pos[1]) - 1

    def get_cur_move(self):
        try:
            move = input().split()
            if len(move) != 2:
                return None
            return list(map(self.conv_to_num, move))
        except Exception:
            return None

    @staticmethod
    def incorrect_move():
        print('Неправильный ход')