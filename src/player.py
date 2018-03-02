class Player:
    def __init__(self, person, number):
        self.person = person
        self.number = number

    @staticmethod
    def make_person_move(cur_game):
        return cur_game.interface.get_cur_move()

    def make_bot_move(self, cur_game):
        dirs = ((1, 1), (1, -1), (-1, -1), (-1, 1))
        for i in range(cur_game.field_height):
            for j in range(cur_game.field_width):
                for direction in dirs:
                    y = i + 2 * direction[1]
                    x = j + 2 * direction[0]
                    while 0 <= x < cur_game.field_width and 0 <= y < cur_game.field_height:
                        move = ((j, i), (x, y))
                        if cur_game.checker.is_move_correct(move, self):
                            return move
                        x += direction[0]
                        y += direction[1]
        for i in range(cur_game.field_height):
            for j in range(cur_game.field_width):
                for direction in dirs:
                    y = i + direction[1]
                    x = j + direction[0]
                    move = ((j, i), (x, y))
                    if cur_game.checker.is_move_correct(move, self):
                        return move
        return None

    def make_move(self, cur_game):
        return cur_game.next_move(self)
