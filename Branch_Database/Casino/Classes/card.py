class Card:

    SUIT_SYMBOLS = {
        "Spades": "♠",
        "Hearts": "♥",
        "Diamonds": "♦",
        "Clubs": "♣"
    }

    POKER_VALUES = {
        "Jack": 11,
        "Queen": 12,
        "King": 13,
        "Ace": 14
    }

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    # Blackjack value of card
    def get_value(self):
        if self.rank in ["Jack", "Queen", "King"]:
            return 10
        if self.rank == "Ace":
            # Hand class will adjust this down if needed
            return 11
        return int(self.rank)

    # Poker value of card (Ace is high)
    def get_poker_value(self):
        if self.rank in self.POKER_VALUES:
            return self.POKER_VALUES[self.rank]

        return int(self.rank)

    # Return value and suit of card
    def __str__(self):
        return f"{self.rank} {self.SUIT_SYMBOLS[self.suit]}"