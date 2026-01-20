"""CLI interaction helpers."""
def prompt_name():
    return input("Enter your name: ").strip() or "player"

def prompt_move():
    while True:
        choice = input("Choose [rock/paper/scissors]: ").strip().lower()
        if choice in ("rock", "paper", "scissors"):
            return choice
        print("Invalid choice.")
