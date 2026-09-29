from ..dealer import Dealer
from .blackjackhand import BlackjackHand


class BlackjackDealer(Dealer):

    hand_class = BlackjackHand

    # Must hit until 17 or higher
    def decide_action(self):
        return "hit" if self.hand.get_value() < 17 else "stand"

    def get_hand_value(self):
        return self.hand.get_value()

    def is_bust(self):
        return self.hand.is_bust()

    def get_visible_hand(self, reveal=False):
        if not self.hand.cards:
            return ""

        if reveal:
            return str(self.hand)

        return f"{self.hand.cards[0]} and [hidden]"