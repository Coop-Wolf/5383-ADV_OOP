# Cards
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
        return f"{self.rank} of {self.suit}"