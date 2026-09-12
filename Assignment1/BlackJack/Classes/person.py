from .hand import Hand

# Person is a parent class to players and the dealer
class Person:

    def __init__(self, name, chips=100):
        self.name = name
        self.hand = Hand()
        self.chips = chips

    def hit(self, deck):
        card = deck.deal_card()
        self.hand.add_card(card)
        return card

    # Do nothing here
    def stand(self):
        pass

    def get_hand_value(self):
        return self.hand.get_value()

    def is_bust(self):
        return self.hand.is_bust()
    
    def is_blackjack(self):
        return self.hand.is_blackjack()

    # Child class will override
    def decide_action(self, dealer_visible_card=None):
        return "stand"