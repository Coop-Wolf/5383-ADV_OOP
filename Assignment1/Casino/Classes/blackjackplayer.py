from .player import Player
from .blackjackhand import BlackjackHand


class BlackjackPlayer(Player):

    def __init__(self, name, chips=100):
        super().__init__(name, chips)
        self.hand = BlackjackHand()
        
    def decide_action(self, dealer_visible_card=None):
        choice = input(f"{self.name}, hit or stand? ").strip().lower()

        if choice == "hit" or choice == "stand":
            return choice
        else:
            return self.decide_action(dealer_visible_card)
        
    def is_bust(self):
        return self.hand.is_bust()
    
    def is_blackjack(self):
        return self.hand.is_blackjack()
    
    def hit(self, deck):
        card = deck.deal_card()
        self.hand.add_card(card)
        return card

    # Do nothing here
    def stand(self):
        pass

    def get_hand_value(self):
        return self.hand.get_value()