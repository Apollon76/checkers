import unittest

from ..checker import *
from ..game import Game
from ..gameconfig import GameConfig


class TestChecker(unittest.TestCase):
    def setUp(self):
        config = GameConfig()
        test_game = Game(config)
        self.checker = Checker(test_game)
        self.player1 = self.checker._game.player1
        self.player2 = self.checker._game.player2

    def tearDown(self):
        self.checker._game.interface.quit_program()

    def test_sgn(self):
        self.assertEqual(sgn(1002), 1)
        self.assertEqual(sgn(0), 0)
        self.assertEqual(sgn(-88998), -1)

    def test_is_in_field(self):
        checker = self.checker
        self.assertTrue(checker.is_in_field((1, 2)))
        self.assertTrue(checker.is_in_field((0, 0)))
        self.assertFalse(checker.is_in_field((-1, 2)))
        self.assertFalse(checker.is_in_field((1, 10)))

    def test_state(self):
        checker = self.checker
        checker.make_graph(self.player1)
        self.assertEqual(checker.state(self.player1), '')
        checker._game.read_field('src/tests/field.txt')
        checker.make_graph(self.player2)
        self.assertEqual(checker.state(self.player2), '')
        checker._game.read_field('src/tests/field5.txt')
        checker.make_graph(self.player1)
        self.assertEqual(checker.state(self.player1), 'White win!')
        checker._game.read_field('src/tests/field7.txt')
        checker.make_graph(self.player1)
        self.assertEqual(checker.state(self.player1), 'Black win!')

    def test_get_global_max_len(self):
        checker = self.checker
        player1 = self.player1
        checker._game.read_field('src/tests/field4.txt')
        checker.make_graph(player1)
        self.assertEqual(checker.get_global_max_len(player1), 4)
        checker._game.read_field('src/tests/field3.txt')
        checker.make_graph(player1)
        self.assertEqual(checker.get_global_max_len(player1), 0)

    def test_get_king_max_len(self):
        checker = self.checker
        player1 = self.player1
        player2 = self.player2
        checker._game.read_field('src/tests/field4.txt')
        checker.make_graph(player1)
        self.assertEqual(checker.get_king_max_len(4, 5, 4, 5, player1, 0), 4)
        checker._game.read_field('src/tests/field3.txt')
        checker.make_graph(player2)
        self.assertEqual(checker.get_king_max_len(3, 0, 3, 0, player2, 0), 0)

    def test_get_max_len(self):
        checker = self.checker
        checker._game.read_field('src/tests/field4.txt')
        checker.make_graph(self.player1)
        self.assertEqual(checker.get_max_len(4, 3, 4, 3, self.player1), 1)
        checker.make_graph(self.player2)
        self.assertEqual(checker.get_max_len(5, 6, 5, 6, self.player2), 1)
        self.assertEqual(checker.get_max_len(1, 1, 1, 1, self.player2), 0)

    def test_can_make_move(self):
        checker = self.checker
        checker._game.read_field('src/tests/field4.txt')
        checker.make_graph(self.player1)
        self.assertTrue(checker.can_make_move(checker._game.player1))
        checker.make_graph(self.player2)
        self.assertTrue(checker.can_make_move(checker._game.player2))
        checker._game.read_field('src/tests/field6.txt')
        checker.make_graph(self.player1)
        self.assertFalse(checker.can_make_move(checker._game.player1))
        checker.make_graph(self.player2)
        self.assertTrue(checker.can_make_move(checker._game.player2))

    def test_can_take_draught_by_this(self):
        checker = self.checker
        checker._game.read_field('src/tests/field4.txt')
        checker.make_graph(self.player1)
        self.assertTrue(checker.can_take_draught_by_this(4, 5, checker._game.player1))
        checker.make_graph(self.player2)
        self.assertFalse(checker.can_take_draught_by_this(4, 5, checker._game.player2))
        self.assertTrue(checker.can_take_draught_by_this(5, 6, checker._game.player2))

    def test_can_take_draught(self):
        checker = self.checker
        checker._game.read_field('src/tests/field4.txt')
        player1 = checker._game.player1
        player2 = checker._game.player2
        checker.make_graph(player1)
        self.assertTrue(checker.can_take_draught(player1))
        checker.make_graph(player2)
        self.assertTrue(checker.can_take_draught(player2))
        checker._game.read_field('src/tests/field2.txt')
        checker.make_graph(player1)
        self.assertFalse(checker.can_take_draught(player1))
        checker.make_graph(player2)
        self.assertTrue(checker.can_take_draught(player2))

    def test_is_move_correct(self):
        checker = self.checker
        player1 = checker._game.player1
        checker._game.read_field('src/tests/field4.txt')
        checker.make_graph(player1)
        self.assertTrue(checker.is_move_correct(((4, 5), (6, 7)), checker._game.player1))
        self.assertFalse(checker.is_move_correct(((4, 1), (6, 3)), checker._game.player1))
        self.assertFalse(checker.is_move_correct(((4, 3), (6, 7)), checker._game.player1))

    def test_is_king_move_correct(self):
        checker = self.checker
        checker._game.read_field('src/tests/field4.txt')
        player1 = checker._game.player1
        player2 = checker._game.player2
        checker.make_graph(player1)
        self.assertTrue(checker.is_king_move_correct(4, 5, 6, 7, player1, 4))
        self.assertFalse(checker.is_king_move_correct(4, 5, 6, 3, player1, 4))

    def test_is_draught_move_correct(self):
        checker = self.checker
        checker._game.read_field('src/tests/field4.txt')
        player1 = checker._game.player1
        player2 = checker._game.player2
        checker.make_graph(player2)
        self.assertTrue(checker.is_draught_move_correct(5, 2, 3, 0, player2, 1))
        self.assertFalse(checker.is_draught_move_correct(5, 2, 6, 1, player2, 1))
        checker.make_graph(player1)
        self.assertTrue(checker.is_draught_move_correct(4, 1, 6, 3, player1, 1))

    def test_can_continue(self):
        checker = self.checker
        checker._game.read_field('src/tests/field2.txt')
        player1 = self.player1
        player2 = self.player2
        checker.make_graph(self.player2)
        self.assertFalse(checker.can_continue(((7, 7,), (6, 6)), player2))
        self.assertFalse(checker.can_continue(((7, 7,), (6, 6)), player2))


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestChecker))
    return test_suite
