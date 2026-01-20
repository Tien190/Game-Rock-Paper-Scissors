"""Client entrypoint."""
import socket
import time
from client.ui.cli import prompt_name, prompt_move
from client.utils.protocol import ProtocolStream


def main():
    host = input("Server host (default 127.0.0.1): ").strip() or "127.0.0.1"
    port = int(input("Server port (default 5000): ").strip() or "5000")
    name = prompt_name()
    token = None

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            stream = ProtocolStream(sock)

            stream.send({"type": "HELLO", "name": name, "token": token})
            welcome = stream.recv()
            if not welcome or welcome.get("type") != "WELCOME":
                print("Failed to connect.")
                return

            token = welcome.get("token")
            print("[CLIENT]", welcome.get("message"))

            while True:
                msg = stream.recv()
                if msg is None:
                    raise ConnectionError("Disconnected")

                if msg["type"] == "MATCH_FOUND":
                    print(f"Matched with {msg['opponent']} (best of {msg['best_of']})")

                elif msg["type"] == "ROUND_START":
                    print(f"Round {msg['round']} | Scores {msg['scores']}")
                    move = prompt_move()
                    stream.send({"type": "MOVE", "choice": move})

                elif msg["type"] == "ROUND_RESULT":
                    print(f"Round {msg['round']}: you={msg['you']} opponent={msg['opponent']} winner={msg['winner']}")

                elif msg["type"] == "MATCH_RESULT":
                    print(f"Match end. Winner={msg['winner']} Scores={msg['scores']}")
                    return

                elif msg["type"] == "OPPONENT_LEFT":
                    print("Opponent left.")
                    return

                elif msg["type"] == "ERROR":
                    print("Error:", msg["message"])

        except Exception as e:
            print("Disconnected. Trying to reconnect...")
            time.sleep(2)
            continue


if __name__ == "__main__":
    main()