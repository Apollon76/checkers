import unittest
import time

from ..timer import Timer


class TestTimer(unittest.TestCase):
    def test_get(self):
        timer = Timer(True, 1000)
        start_time = time.monotonic()
        timer.start()
        time.sleep(5)
        cur_time = time.monotonic()
        self.assertEqual(timer.get(), round(1000 - cur_time + start_time))


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestTimer))
    return test_suite
