from ..player import Player
from .blackjackhand import BlackjackHand


class BlackjackPlayer(Player):

    def __init__(self, name, chips=100):
        super().__init__(name, chips)

        # A player can have several hands after splitting.
        # Each hand tracks its own bet and whether it has finished.
        self.hands = []
        self.reset_hands()

    def reset_hands(self):
        self.hands = [BlackjackHand()]
        self.set_active_hand(0)

    # self.hand is always the hand currently being played
    def set_active_hand(self, index):
        self.active_index = index
        self.hand = self.hands[index]

    def hand_label(self, index):
        if len(self.hands) == 1:
            return self.name

        return f"{self.name} Hand {index + 1}"

    # Actions currently available for the active hand
    def available_actions(self):
        actions = ["hit", "stand"]

        if self.can_double_down():
            actions.append("double")

        if self.can_split():
            actions.append("split")

        return actions

    def can_double_down(self):
        # Must have exactly two cards and enough chips to match the bet
        return len(self.hand.cards) == 2 and self.chips >= self.hand.bet

    def can_split(self):
        # Must have exactly two cards and enough chips for a second bet
        if len(self.hand.cards) != 2 or self.chips < self.hand.bet:
            return False

        # Same rank = can split
        return self.hand.cards[0].rank == self.hand.cards[1].rank

    # Double the bet, take exactly one more card, then finish the hand
    def double_down(self, deck):
        self.wager(self.hand.bet)
        self.hand.bet *= 2
        self.hit(deck)
        self.hand.stood = True

    # Split the active hand into two, each with the original bet
    def split(self, deck):
        original = self.hand
        bet = original.bet

        # Pay the additional bet
        self.wager(bet)

        # Neither split hand can count as a blackjack
        original.from_split = True

        # The second card moves to a new hand next to the original
        second = BlackjackHand(bet, from_split=True)
        second.add_card(original.cards.pop())
        self.hands.insert(self.active_index + 1, second)

        # Each split hand gets one more card
        original.add_card(deck.deal_card())
        second.add_card(deck.deal_card())

    def is_bust(self):
        return self.hand.is_bust()

    def is_blackjack(self):
        return self.hand.is_blackjack()

    def get_hand_value(self):
        return self.hand.get_value()