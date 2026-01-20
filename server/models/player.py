"""Player model."""
import threading
import time


class Player:
    def __init__(self, name, token, stream):
        self.name = name
        self.token = token
        self.stream = stream
        self.connected = True
        self.disconnected_at = None
        self.score = 0
        self.choice = None

        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)

    def set_choice(self, choice):
        with self.cond:
            self.choice = choice
            self.cond.notify_all()

    def wait_for_choice(self, timeout):
        with self.cond:
            if self.choice is None:
                self.cond.wait(timeout=timeout)
            return self.choice

    def clear_choice(self):
        with self.cond:
            self.choice = None

    def mark_disconnected(self):
        self.connected = False
        self.disconnected_at = time.time()

    def can_reconnect(self, timeout):
        if self.disconnected_at is None:
            return False
        return (time.time() - self.disconnected_at) <= timeout

    def reconnect(self, stream):
        self.stream = stream
        self.connected = True
        self.disconnected_at = None