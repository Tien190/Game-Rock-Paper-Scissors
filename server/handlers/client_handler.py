"""Handle per-client socket communication."""
import threading
import uuid
from server.models.player import Player
from server.config import RECONNECT_TIMEOUT


class ClientHandler(threading.Thread):
    def __init__(self, sock, match_maker, token_map):
        super().__init__(daemon=True)
        self.sock = sock
        self.match_maker = match_maker
        self.token_map = token_map

    def run(self):
        from server.utils.protocol import ProtocolStream
        stream = ProtocolStream(self.sock)

        try:
            hello = stream.recv()
            if not hello or hello.get("type") != "HELLO":
                stream.send({"type": "ERROR", "message": "Invalid HELLO"})
                return

            name = hello.get("name") or "player"
            token = hello.get("token")

            if token and token in self.token_map:
                player = self.token_map[token]
                if player.can_reconnect(RECONNECT_TIMEOUT):
                    player.reconnect(stream)
                    stream.send({"type": "WELCOME", "token": token, "message": "reconnected"})
                    self.listen(player)
                    return

            token = str(uuid.uuid4())
            player = Player(name, token, stream)
            self.token_map[token] = player
            stream.send({"type": "WELCOME", "token": token, "message": "ok"})
            self.match_maker.add_player(player)
            self.listen(player)

        except Exception:
            pass

    def listen(self, player):
        try:
            while True:
                msg = player.stream.recv()
                if msg is None:
                    break
                if msg.get("type") == "MOVE":
                    player.set_choice(msg.get("choice"))
        except Exception:
            pass
        finally:
            player.mark_disconnected()