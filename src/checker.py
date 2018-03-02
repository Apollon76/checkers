from src.objects import Objects


def sgn(x):
    if x > 0:
        return 1
    if x == 0:
        return 0
    return -1


class Checker:
    def __init__(self, game):
        self._game = game
        self.edges = set()
        self.vertex = {}
        self.marked = set()
        self.king_vertex = {}
        self.king_edges = set()
        self.ceil_max_len = {}
        self.global_max_len = 0

    def create_edges(self, start_y, start_x, player, is_king):
        dirs = ((1, 1), (1, -1), (-1, -1), (-1, 1))
        game = self._game
        if (start_x + start_y) % 2 == 0:
            return
        if game.field_objects[start_y][start_x] != Objects.empty_field and \
                game.field_objects[start_y][start_x].value % 2 != player.number % 2:
            return
        if not is_king:
            for direction in dirs:
                y = start_y + 2 * direction[1]
                x = start_x + 2 * direction[0]
                if not self.is_in_field((x, y)):
                    break
                move = ((start_x, start_y), (x, y))
                if game.field_objects[y][x] != Objects.empty_field:
                    continue
                mid_ceil = game.field_objects[y - direction[1]][x - direction[0]]
                if mid_ceil == Objects.empty_field or mid_ceil.value % 2 == player.number % 2:
                    continue
                self.edges.add(move)
        else:
            for direction in dirs:
                y = start_y + direction[1]
                x = start_x + direction[0]
                while self.is_in_field((x, y)):
                    if game.field_objects[y][x] != Objects.empty_field and \
                            game.field_objects[y][x].value % 2 != player.number % 2:
                        if self.is_in_field((x + direction[0], y + direction[1])) and \
                                game.field_objects[y + direction[1]][x + direction[0]] == Objects.empty_field:
                            self.king_edges.add((x, y))
                        break
                    x += direction[0]
                    y += direction[1]

    def make_graph(self, player):
        self.edges.clear()
        self.marked.clear()
        self.king_edges.clear()
        self.ceil_max_len = {}
        self.global_max_len = 0
        for i in range(self._game.field_height):
            for j in range(self._game.field_width):
                self.create_edges(i, j, player, False)
                self.create_edges(i, j, player, True)
                self.vertex[(j, i)] = []
                self.king_vertex[(j, i)] = []
        for i in self.edges:
            self.vertex[i[0]] += [i[1]]
        self.global_max_len = self.get_global_max_len(player)

    def get_global_max_len(self, player):
        cur_max = 0
        self.ceil_max_len = {}
        self.global_max_len = 0
        for i in range(self._game.field_height):
            for j in range(self._game.field_width):
                self.ceil_max_len[(j, i)] = 0
                if not (self._game.field_objects[i][j] != Objects.empty_field and
                        self._game.field_objects[i][j].value % 2 == player.number % 2):
                    continue
                self.marked.clear()
                if self._game.field_objects[i][j].value <= 2:
                    self.ceil_max_len[(j, i)] = self.get_max_len(j, i, j, i, player)
                else:
                    self.ceil_max_len[(j, i)] = self.get_king_max_len(j, i, j, i, player, 0)
                cur_max = max(cur_max, self.ceil_max_len[(j, i)])
        return cur_max

    def get_max_len(self, start_x, start_y, x, y, player):
        dirs = ((1, 1), (1, -1), (-1, -1), (-1, 1))
        game = self._game
        cur_max = 0
        for direction in dirs:
            mid_x = x + direction[0]
            mid_y = y + direction[1]
            cur_x = x + 2 * direction[0]
            cur_y = y + 2 * direction[1]
            if not self.is_in_field((mid_x, mid_y)) or \
                    (mid_x, mid_y) in self.marked or \
                    game.field_objects[mid_y][mid_x] == Objects.empty_field or \
                    game.field_objects[mid_y][mid_x].value % 2 == player.number % 2:
                continue
            if not self.is_in_field((cur_x, cur_y)) or \
                    (game.field_objects[cur_y][cur_x] != Objects.empty_field and
                    (cur_x, cur_y) != (start_x, start_y)):
                continue
            self.marked.add((mid_x, mid_y))
            cur_max = max(cur_max, self.get_max_len(start_x, start_y, cur_x, cur_y, player) + 1)
            self.marked.remove((mid_x, mid_y))
        return cur_max

    def is_in_field(self, ceil):
        return 0 <= ceil[0] < self._game.field_width and 0 <= ceil[1] < self._game.field_height

    def get_king_max_len(self, start_x, start_y, x, y, player, cur_len):
        cur_max = cur_len
        dirs = ((1, 1), (1, -1), (-1, -1), (-1, 1))
        for direction in dirs:
            cur_x = x
            cur_y = y
            while self.is_in_field((cur_x + direction[0], cur_y + direction[1])):
                cur_x += direction[0]
                cur_y += direction[1]
                cur_object = self._game.field_objects[cur_y][cur_x]
                if self.is_in_field((cur_x + direction[0], cur_y + direction[1])) \
                        and (self._game.field_objects[cur_y + direction[1]][cur_x + direction[0]] == Objects.empty_field or
                            (cur_y + direction[1], cur_x + direction[0]) == (start_x, start_y)) \
                        and cur_object != Objects.empty_field \
                        and cur_object.value % 2 != player.number % 2 \
                        and (cur_x, cur_y) not in self.marked:
                    self.marked.add((cur_x, cur_y))
                    for i in range(1, self._game.field_width):
                        turn_x = cur_x + i * direction[0]
                        turn_y = cur_y + i * direction[1]
                        if not self.is_in_field((turn_x, turn_y)) or \
                                self._game.field_objects[turn_y][turn_x] != Objects.empty_field:
                            break
                        cur_max = max(cur_max,
                                      self.get_king_max_len(start_x, start_y, turn_x, turn_y,
                                                            player, cur_len + 1))
                    self.marked.remove((cur_x, cur_y))
                    break
                if cur_object != Objects.empty_field:
                    break
        return cur_max

    def can_continue(self, move, player):
        if abs(move[0][0] - move[1][0]) == 1 or not self._game.was_taken:
            return False
        x, y = move[1][0], move[1][1]
        if self.can_take_draught_by_this(x, y, player):
            return True
        return False

    def can_take_draught_by_this(self, start_x, start_y, player):
        dirs = ((1, 1), (1, -1), (-1, -1), (-1, 1))
        game = self._game
        if game.field_objects[start_y][start_x].value == player.number:
            for direction in dirs:
                y = start_y + 2 * direction[1]
                x = start_x + 2 * direction[0]
                move = ((start_x, start_y), (x, y))
                if self.is_move_correct(move, player):
                    return True
        if game.field_objects[start_y][start_x].value == player.number + 2:
            for direction in dirs:
                y = start_y + direction[1]
                x = start_x + direction[0]
                while self.is_in_field((x, y)):
                    if game.field_objects[y][x] != Objects.empty_field:
                        if game.field_objects[y][x].value % 2 != player.number % 2:
                            if self.is_in_field((x + direction[0], y + direction[1])) and \
                                    game.field_objects[y + direction[1]][x + direction[0]] == Objects.empty_field:
                                return True
                            else:
                                break
                        else:
                            break
                    x += direction[0]
                    y += direction[1]
        return False

    def can_make_move(self, player):
        game = self._game
        for x1 in range(game.field_width):
            for y1 in range(game.field_height):
                for x2 in range(game.field_width):
                    for y2 in range(game.field_height):
                        if self.is_move_correct(((x1, y1), (x2, y2)), player):
                            return True
        return False

    def can_take_draught(self, player):
        game = self._game
        for i in range(game.field_height):
            for j in range(game.field_width):
                if self.can_take_draught_by_this(j, i, player):
                    return True
        return False

    def is_king_move_correct(self, x1, y1, x2, y2, player, l):
        if self._game.field_objects[y1][x1].value != player.number + 2:
            return False
        cur_x = x1
        cur_y = y1
        dir_x = sgn(x2 - x1)
        dir_y = sgn(y2 - y1)
        bit = False
        bit_ceil = None
        while cur_x != x2 and cur_y != y2:
            cur_x += dir_x
            cur_y += dir_y
            cur_ceil = self._game.field_objects[cur_y][cur_x]
            if cur_x == x2 and cur_y == y2:
                if cur_ceil == Objects.empty_field:
                    break
                else:
                    return False
            if cur_ceil == Objects.empty_field:
                continue
            if cur_ceil.value % 2 == player.number % 2:
                return False
            if bit:
                return False
            if not self.is_in_field((cur_x + dir_x, cur_y + dir_y)) or \
                    self._game.field_objects[cur_y + dir_y][cur_x + dir_x] != Objects.empty_field:
                return False
            bit = True
            bit_ceil = (cur_x, cur_y)
        if not bit and self.can_take_draught(player):
            return False
        self.marked.clear()
        self.marked.add(bit_ceil)
        new_l = self.get_king_max_len(x1, y1, x2, y2, player, 0)
        self.marked.clear()
        if (bit and new_l < l - 1) or (not bit and new_l < l):
            return False
        return True

    def is_draught_move_correct(self, x1, y1, x2, y2, player, l):
        if self._game.field_objects[y1][x1].value != player.number:
            return False
        type_of_turn = abs(x1 - x2)
        if type_of_turn > 2:
            return False
        cur_object = self._game.field_objects[y2][x2]
        if type_of_turn == 1:
            if player.number == 1 and y2 < y1:
                return False
            if player.number == 2 and y2 > y1:
                return False
            if self.can_take_draught(player):
                return False
            if cur_object != Objects.empty_field:
                return False
            return True
        else:
            if cur_object != Objects.empty_field:
                return False
            mid_x = x1 + (x2 - x1) // 2
            mid_y = y1 + (y2 - y1) // 2
            mid_object = self._game.field_objects[mid_y][mid_x]
            if (mid_object == Objects.empty_field or
                    mid_object.value % 2 == player.number % 2):
                return False
            self.marked.clear()
            self.marked.add((mid_x, mid_y))
            new_l = self.get_max_len(x1, y1, x2, y2, player)
            self.marked.clear()
            if new_l < l - 1:
                return False
            return True

    def is_move_correct(self, move, player):
        if move is None:
            return False
        x1, y1 = move[0][0], move[0][1]
        x2, y2 = move[1][0], move[1][1]
        if not self.is_in_field((x1, y1)):
            return False
        if not self.is_in_field((x2, y2)):
            return False
        if abs(x1 - x2) != abs(y1 - y2) or x1 == x2:
            return False
        if self._game.field_objects[y1][x1] == Objects.empty_field or \
                self._game.field_objects[y2][x2] != Objects.empty_field:
            return False
        if not self._game.is_first_move and self._game.cur_figure != (x1, y1):
            return False
        l = self.get_global_max_len(player)
        if (self._game.field_objects[y1][x1] == Objects.black_king or
                self._game.field_objects[y1][x1] == Objects.white_king):
            return self.is_king_move_correct(x1, y1, x2, y2, player, l)
        return self.is_draught_move_correct(x1, y1, x2, y2, player, l)

    def state(self, player):
        black, white = False, False
        for line in range(self._game.field_height):
            for j in self._game.field_objects[line]:
                if j == Objects.white_draught or j == Objects.white_king:
                    white = True
                if j == Objects.black_draught or j == Objects.black_king:
                    black = True
        if not black or (player.number == 2 and not self.can_make_move(player)):
            return 'White win!'
        elif not white or (player.number == 1 and not self.can_make_move(player)):
            return 'Black win!'
        if self._game.timer1.get() < 0:
            return 'Black win!'
        if self._game.timer2.get() < 0:
            return 'White win!'
        return ''
