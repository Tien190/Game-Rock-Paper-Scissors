"""Game logic coordination for matches."""
import threading
import time
from server.config import BEST_OF, RECONNECT_TIMEOUT

WIN_MAP = {
    ("rock", "scissors"),
    ("scissors", "paper"),
    ("paper", "rock"),
}


class Match(threading.Thread):
    def __init__(self, player_a, player_b):
        super().__init__(daemon=True)
        self.a = player_a
        self.b = player_b
        self.round = 0
        self.active = True

    def run(self):
        self.send_both({"type": "MATCH_FOUND", "opponent": self.b.name, "best_of": BEST_OF}, self.a)
        self.send_both({"type": "MATCH_FOUND", "opponent": self.a.name, "best_of": BEST_OF}, self.b)

        while self.active and max(self.a.score, self.b.score) < BEST_OF:
            self.round += 1
            self.a.clear_choice()
            self.b.clear_choice()

            self.send_both({
                "type": "ROUND_START",
                "round": self.round,
                "scores": {"you": self.a.score, "opponent": self.b.score}
            }, self.a)
            self.send_both({
                "type": "ROUND_START",
                "round": self.round,
                "scores": {"you": self.b.score, "opponent": self.a.score}
            }, self.b)

            a_choice = self.wait_for_move(self.a)
            b_choice = self.wait_for_move(self.b)

            if a_choice is None or b_choice is None:
                self.handle_disconnect()
                return

            winner = self.resolve_round(a_choice, b_choice)
            if winner == "a":
                self.a.score += 1
            elif winner == "b":
                self.b.score += 1

            self.send_both({
                "type": "ROUND_RESULT",
                "round": self.round,
                "you": a_choice,
                "opponent": b_choice,
                "winner": "you" if winner == "a" else ("opponent" if winner == "b" else "draw")
            }, self.a)

            self.send_both({
                "type": "ROUND_RESULT",
                "round": self.round,
                "you": b_choice,
                "opponent": a_choice,
                "winner": "you" if winner == "b" else ("opponent" if winner == "a" else "draw")
            }, self.b)

        match_winner = "a" if self.a.score > self.b.score else "b"
        self.send_both({
            "type": "MATCH_RESULT",
            "winner": "you" if match_winner == "a" else "opponent",
            "scores": {"you": self.a.score, "opponent": self.b.score}
        }, self.a)
        self.send_both({
            "type": "MATCH_RESULT",
            "winner": "you" if match_winner == "b" else "opponent",
            "scores": {"you": self.b.score, "opponent": self.a.score}
        }, self.b)

    def resolve_round(self, a, b):
        if a == b:
            return "draw"
        if (a, b) in WIN_MAP:
            return "a"
        return "b"

    def wait_for_move(self, player):
        deadline = time.time() + RECONNECT_TIMEOUT
        while time.time() < deadline:
            if not player.connected and not player.can_reconnect(RECONNECT_TIMEOUT):
                return None
            choice = player.wait_for_choice(timeout=1)
            if choice:
                return choice
        return None

    def handle_disconnect(self):
        self.send_both({"type": "OPPONENT_LEFT", "message": "Opponent disconnected"}, self.a)
        self.send_both({"type": "OPPONENT_LEFT", "message": "Opponent disconnected"}, self.b)

    def send_both(self, msg, player):
        try:
            player.stream.send(msg)
        except Exception:
            pass


class MatchMaker:
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()

    def add_player(self, player):
        with self.lock:
            self.queue.append(player)
            if len(self.queue) >= 2:
                a = self.queue.pop(0)
                b = self.queue.pop(0)
                Match(a, b).start()