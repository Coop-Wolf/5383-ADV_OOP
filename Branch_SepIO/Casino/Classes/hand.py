# Base hand for games
class Hand:
    def __init__(self):
        # List of cards
        self.cards = []

    # Add a card to hand
    def add_card(self, card):
        self.cards.append(card)

    def __str__(self):
        return ", ".join(str(card) for card in self.cards)