from ..player import Player
from .videopokerhand import VideoPokerHand


class VideoPokerPlayer(Player):

    def __init__(self, name, chips=100):
        super().__init__(name, chips)
        self.hand = VideoPokerHand()

    # Keep the held cards and replace the rest, once
    def draw_replacements(self, deck, held):

        new_hand = VideoPokerHand()

        for index, card in enumerate(self.hand.cards):
            if index in held:
                new_hand.add_card(card)
            else:
                new_hand.add_card(deck.deal_card())

        self.hand = new_hand