import time
import threading


class Timer:
    def __init__(self, is_on, value):
        self._value = value
        self._stopped = True
        self._start_time = None
        self._lock = threading.Lock()
        self.is_on = is_on

    def start(self):
        if not self.is_on:
            return
        self._lock.acquire()
        if self._stopped:
            self._stopped = False
            self._start_time = time.monotonic()
        self._lock.release()

    def stop(self):
        if not self.is_on:
            return
        self._lock.acquire()
        if self._start_time is not None:
            self._value -= time.monotonic() - self._start_time
        self._stopped = True
        self._start_time = None
        self._lock.release()

    def get(self):
        if not self.is_on:
            return 0
        if self._start_time is None:
            return round(self._value)
        delta = time.monotonic() - self._start_time
        return round(self._value - delta)
