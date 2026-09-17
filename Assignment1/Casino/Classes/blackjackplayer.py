from .player import Player
from .blackjackhand import BlackjackHand


class BlackjackPlayer(Player):

    def __init__(self, name, chips=100):
        super().__init__(name, chips)

        # Player can have multiple hands after splitting
        self.hands = [BlackjackHand()]

        # Keep self.hand as the currently active hand
        self.hand = self.hands[0]

        # Bet for each hand
        self.hand_bets = [0]

        # Track whether each hand has finished
        self.hand_stood = [False]
        

    def reset_hands(self):
        self.hands = [BlackjackHand()]
        self.hand = self.hands[0]
        self.hand_bets = [0]
        self.hand_stood = [False]

    def set_active_hand(self, index):
        self.hand = self.hands[index]

    def decide_action(self, dealer_visible_card=None):
        while True:
            print()
            print(f"{self.name}'s turn")
            print("-" * 30)

            print(f"Hand:  {self.hand}")
            print(f"Value: {self.get_hand_value()}")
            print(f"Chips: {self.chips}")
            print(f"Bet:   {self.hand_bets[self.hands.index(self.hand)]}")
            print()

            print("1. Hit")
            print("2. Stand")

            # Double Down
            if self.can_double_down():
                print("3. Double Down")

            # Split
            if self.can_split():
                print("4. Split")

            choice = input("\nChoose an action: ").strip().lower()

            if choice in ("1", "hit"):
                return "hit"

            elif choice in ("2", "stand"):
                return "stand"

            elif choice in ("3", "double", "double down"):
                if self.can_double_down():
                    return "double"

                print("ERROR: You cannot double down right now.")

            elif choice in ("4", "split"):
                if self.can_split():
                    return "split"

                print("ERROR: You cannot split this hand.")

            else:
                print("ERROR: Invalid choice.")

    def can_double_down(self):
        # Must have exactly two cards
        if len(self.hand.cards) != 2:
            return False

        # Must have enough chips to match the current bet
        current_index = self.hands.index(self.hand)
        current_bet = self.hand_bets[current_index]

        return self.chips >= current_bet

    def can_split(self):
        # Must have exactly two cards
        if len(self.hand.cards) != 2:
            return False

        # Need enough chips to place the second bet
        current_index = self.hands.index(self.hand)
        current_bet = self.hand_bets[current_index]

        if self.chips < current_bet:
            return False

        card1 = self.hand.cards[0]
        card2 = self.hand.cards[1]

        # Same rank = can split
        return card1.rank == card2.rank

    def is_bust(self):
        return self.hand.is_bust()

    def is_blackjack(self):
        return self.hand.is_blackjack()

    def stand(self):
        pass

    def get_hand_value(self):
        return self.hand.get_value()