# Hand per player and dealer
class Hand:
    def __init__(self):
        # List of cards
        self.cards = []

    # Add a card to hand
    def add_card(self, card):
        self.cards.append(card)

    # Get total value of hand
    def get_value(self):
        total = sum(card.get_value() for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == "Ace")

        # Downgrade Aces from 11 to 1 as needed to avoid busting
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        return total

    def is_bust(self):
        return self.get_value() > 21

    # Blackjack can only happen with opening hand
    def is_blackjack(self):
        return len(self.cards) == 2 and self.get_value() == 21

    def __str__(self):
        return ", ".join(str(card) for card in self.cards)