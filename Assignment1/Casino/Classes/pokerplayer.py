from .player import Player
from .pokerhand import PokerHand


class PokerPlayer(Player):

    def __init__(self, name, chips=100):
        super().__init__(name, chips)
        self.hand = PokerHand()