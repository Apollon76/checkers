import unittest

from ..gameconfig import GameConfig
from ..game import Game


class TestInterface(unittest.TestCase):
    def setUp(self):
        config = GameConfig()
        test_game = Game(config)
        self.game_interface = test_game.interface

    def tearDown(self):
        self.game_interface.quit_program()

    def test_is_inverted(self):
        self.assertFalse(self.game_interface.is_inverted())


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestInterface))
    return test_suite
