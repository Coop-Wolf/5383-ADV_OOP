from ..player import Player
from .pokerhand import PokerHand


class PokerPlayer(Player):

    def __init__(self, name, chips=100):
        super().__init__(name, chips)
        self.earnings = 0
        self.hand = PokerHand()
        self.folded = False

    def decide_action(self, current_bet, pot):
        print()
        print(f"  {self.name}'s turn")
        print("  " + "-" * 30)

        print(f"  Your hand:   {self.hand}")
        print(f"  Chips:       {self.chips}")
        print(f"  Current bet: {self.bet}")
        print(f"  Total bet:   {self.total_bet}")
        print(f"  Table bet:   {current_bet}")
        print(f"  Pot:         {pot}")
        print()

        while True:
            print("  Choose an action:")

            if self.bet == current_bet:
                print("    1. Check")
            else:
                print("    1. Call")

            print("    2. Raise")
            print("    3. Fold")

            choice = input("\n  Action: ").strip().lower()

            if choice in ("1", "check") and self.bet == current_bet:
                return "check"

            elif choice in ("1", "call") and self.bet < current_bet:
                return "call"

            elif choice in ("2", "raise"):
                return "raise"

            elif choice in ("3", "fold"):
                return "fold"

            else:
                print("\n  ERROR: Invalid action.")