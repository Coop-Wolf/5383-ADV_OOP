from .hand import Hand

class Dealer:

    # Subclasses set this to use a game-specific hand
    hand_class = Hand

    def __init__(self):
        self.hand = self.hand_class()

    # Start a new round with an empty hand
    def reset_hand(self):
        self.hand = self.hand_class()

    # Draw a card from the deck and add it to the hand
    def hit(self, deck):
        card = deck.deal_card()
        self.hand.add_card(card)
        return card