"""Shared protocol helpers."""
import json
import threading


class ProtocolStream:
    def __init__(self, sock):
        self.sock = sock
        self.file = sock.makefile("rwb")
        self.lock = threading.Lock()

    def send(self, data: dict):
        payload = (json.dumps(data) + "\n").encode("utf-8")
        with self.lock:
            self.file.write(payload)
            self.file.flush()

    def recv(self):
        line = self.file.readline()
        if not line:
            return None
        return json.loads(line.decode("utf-8").strip())