import unittest

from ..game import Game
from ..gameconfig import GameConfig


class TestPlayer(unittest.TestCase):
    def setUp(self):
        config = GameConfig()
        self.test_game = Game(config)

    def tearDown(self):
        self.test_game.interface.quit_program()

    def test_make_bot_move(self):
        checker = self.test_game.checker
        player1 = self.test_game.player1
        player2 = self.test_game.player2
        self.test_game.read_field('src/tests/field4.txt')
        checker.make_graph(player1)
        self.assertTrue(checker.is_move_correct(player1.make_bot_move(self.test_game), player1))
        self.assertTrue(checker.is_move_correct(player2.make_bot_move(self.test_game), player2))


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestPlayer))
    return test_suite
