"""Server entrypoint."""
import socket
from server.config import HOST, PORT
from server.handlers.client_handler import ClientHandler
from server.handlers.game_handler import MatchMaker


def main():
    token_map = {}
    match_maker = MatchMaker()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(100)

    print(f"[SERVER] Listening on {HOST}:{PORT}")

    while True:
        client_sock, _ = server.accept()
        handler = ClientHandler(client_sock, match_maker, token_map)
        handler.start()


if __name__ == "__main__":
    main()