from .blackjackhand import BlackjackHand
from .blackjackplayer import BlackjackPlayer


class BlackjackDealer(BlackjackPlayer):

    def __init__(self):
        self.hand = BlackjackHand()

    # Must hit until 17 or higher
    def decide_action(self):
        return "hit" if self.hand.get_value() < 17 else "stand"

    def get_visible_hand(self, reveal=False):
        if not self.hand.cards:
            return ""

        if reveal:
            return str(self.hand)

        return f"{self.hand.cards[0]} and [hidden]"