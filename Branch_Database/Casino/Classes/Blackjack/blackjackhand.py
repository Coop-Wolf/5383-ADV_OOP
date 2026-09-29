from ..hand import Hand


class BlackjackHand(Hand):

    def __init__(self, bet=0, from_split=False):
        super().__init__()
        self.bet = bet
        self.stood = False

        # A 21 on a split hand is just 21, not a blackjack
        self.from_split = from_split

    def get_value(self):
        total = sum(card.get_value() for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == "Ace")

        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        return total

    def is_bust(self):
        return self.get_value() > 21

    def is_blackjack(self):
        return (
            not self.from_split
            and len(self.cards) == 2
            and self.get_value() == 21
        )