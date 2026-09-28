import os
import time


class TerminalUI:

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def pause(self, seconds=2):
        time.sleep(seconds)

    def banner(self, title, width=50):
        print()
        print("=" * width)
        print(title.center(width))
        print("=" * width)
        print()

    # Stands in for a bare print(). Games will call this instead of
    # printing directly, so a future UI can redirect the text elsewhere.
    def show_message(self, text=""):
        print(text)

    def ask_yes_no(self, prompt):
        """Returns True for 'y', False for 'n', None if input was interrupted."""
        while True:
            try:
                choice = input(prompt).strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nInput interrupted. Exiting game.")
                return None

            if choice in ("y", "n"):
                return choice == "y"
            print("ERROR: please enter 'y' or 'n'.")

    def ask_int(self, prompt, minimum=None, maximum=None):
        """Keeps asking until the user enters a whole number in range."""
        while True:
            try:
                value = int(input(prompt))
            except ValueError:
                print("  ERROR: Please enter a valid number.")
                continue

            if minimum is not None and value < minimum:
                print(f"  ERROR: Must be at least {minimum}.")
            elif maximum is not None and value > maximum:
                print(f"  ERROR: Must be at most {maximum}.")
            else:
                return value
            
            
    def ask_bet(self, player_name, chips):
        self.banner("PLACE BET", 45)
        self.show_message(f"  Player:          {player_name}")
        self.show_message(f"  Available Chips: {chips}")
        self.show_message("")
        return self.ask_int("  Enter your bet: ", minimum=1, maximum=chips)
    
    
    ACTION_LABELS = {
        "hit": "Hit",
        "stand": "Stand",
        "double": "Double Down",
        "split": "Split",
    }

    def ask_action(self, player_name, hand, value, chips, bet, options):
        self.show_message("")
        self.show_message(f"{player_name}'s turn")
        self.show_message("-" * 30)
        self.show_message(f"Hand:  {hand}")
        self.show_message(f"Value: {value}")
        self.show_message(f"Chips: {chips}")
        self.show_message(f"Bet:   {bet}")
        self.show_message("")

        for number, action in enumerate(options, start=1):
            self.show_message(f"{number}. {self.ACTION_LABELS[action]}")

        while True:
            choice = input("\nChoose an action: ").strip().lower()

            for number, action in enumerate(options, start=1):
                if choice in (str(number), action, self.ACTION_LABELS[action].lower()):
                    return action

            self.show_message("ERROR: Invalid choice.")
            
            
    def ask_holds(self):
        while True:
            raw = input("\n  Cards to hold (e.g. 1 3 5), or Enter to replace all: ")

            cleaned = raw.replace(",", "").replace(" ", "")

            if cleaned == "":
                return set()

            if any(char not in "12345" for char in cleaned):
                self.show_message("  ERROR: Enter card numbers 1-5, like 1 3 5.")
                continue

            return {int(char) - 1 for char in cleaned}

    def ask_continue(self):
        input("\n  Press Enter to continue...")