import unittest

import src.tests.test_interface
import src.tests.test_timer
import src.tests.test_checker
import src.tests.test_player


if __name__ == '__main__':
    print('Testing interface')
    interface_suit = src.tests.test_interface.suite()
    runner = unittest.TextTestRunner()
    runner.run(interface_suit)

    print('Testing timer')
    timer_suite = src.tests.test_timer.suite()
    runner = unittest.TextTestRunner()
    runner.run(timer_suite)

    print('Testing checker')
    checker_suite = src.tests.test_checker.suite()
    runner = unittest.TextTestRunner()
    runner.run(checker_suite)

    print('Testing player')
    player_suite = src.tests.test_player.suite()
    runner = unittest.TextTestRunner()
    runner.run(player_suite)
