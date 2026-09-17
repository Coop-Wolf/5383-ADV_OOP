class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    # Return value of card
    def get_value(self):
        if self.rank in ["Jack", "Queen", "King"]:
            return 10
        if self.rank == "Ace":
            # Hand class will adjust this down if needed
            return 11
        return int(self.rank)

    # Return value and suit of card
    def __str__(self):
        suit_symbols = {
            "Spades": "♠",
            "Hearts": "♥",
            "Diamonds": "♦",
            "Clubs": "♣"
        }

        return f"{self.rank} {suit_symbols[self.suit]}"
    
    def get_poker_value(self, rank):
        values = {
            "Jack": 11,
            "Queen": 12,
            "King": 13,
            "Ace": 14
        }

        if rank in values:
            return values[rank]

        return int(rank)