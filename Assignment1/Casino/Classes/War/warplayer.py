from ..player import Player
from ..hand import Hand

class WarPlayer(Player):
    def __init__(self, name, chips=100):
        super().__init__(name, chips)
        self.earnings = 0
        self.hand = Hand()