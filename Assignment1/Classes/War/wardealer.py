from ..player import Player
from ..hand import Hand

class Wardealer(Player):
    
    def __init__(self):
        self.hand = Hand()