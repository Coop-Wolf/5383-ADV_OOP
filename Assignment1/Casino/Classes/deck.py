import random
from .card import Card

# Deck is a list of unique cards
class Deck:
    SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
    RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10",
              "Jack", "Queen", "King", "Ace"]

    # Put every possible card in the "cards" list
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in self.SUITS for rank in self.RANKS]

    def shuffle(self):
        random.shuffle(self.cards)

    # Get a card off the list of cards
    def deal_card(self):
        return self.cards.pop()