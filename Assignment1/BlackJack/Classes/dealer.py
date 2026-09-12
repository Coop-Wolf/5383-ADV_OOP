from .person import Person

# Dealer
class Dealer(Person):
    
    # Must hit until 17 or higher
    def decide_action(self, dealer_visible_card=None):
        return "hit" if self.get_hand_value() < 17 else "stand"

    def get_visible_hand(self):
        # Only show the first card; hide the rest ("hole card")
        if not self.hand.cards:
            return ""
        return f"{self.hand.cards[0]} and [hidden]"