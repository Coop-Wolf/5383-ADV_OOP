import random
from itertools import product
from ..game import Game
from ..player import Player

class Slots(Game):
    
    name = "Slots"
    player_class = Player

    # symbol -> weight (higher = more common)
    SYMBOLS = {"cherry": 30, "lemon": 25, "bar": 20, "bell": 15, "seven": 8, "diamond": 2}

    # three of a kind -> pays N to 1 (net win = bet * N)
    PAYTABLE = {"cherry": 8, "lemon": 12, "bar": 20, "bell": 40, "seven": 100, "diamond": 500}
    TWO_CHERRY_PAYOUT = 1

    def __init__(self, player, db=None, rng=None):
        super().__init__(player, db)
        self.rng = rng or random.Random()
        self.bet = 0
        self.reels = []

    # Take the bet and spin; the screen animates toward self.reels
    def deal(self, bet):
        self.collect_bet(self.game_player, bet)
        self.bet = bet
        names = list(self.SYMBOLS)
        weights = list(self.SYMBOLS.values())
        self.reels = self.rng.choices(names, weights=weights, k=3)
        return self.reels

    # Evaluate the reels, settle the bet, return a result for the screen
    def determine_winner(self):
        multiplier = self.evaluate(self.reels)
        outcome = "win" if multiplier > 0 else "loss"
        net_change = self.settle(self.game_player, self.bet, outcome, multiplier)
        return {"reels": self.reels, "outcome": outcome,
                "multiplier": multiplier, "net_change": net_change}

    @classmethod
    def evaluate(cls, reels):
        if reels[0] == reels[1] == reels[2]:
            return cls.PAYTABLE[reels[0]]
        if reels[0] == reels[1] == "cherry":
            return cls.TWO_CHERRY_PAYOUT
        return 0

    # Exact return-to-player, for tuning weights and paytable
    @classmethod
    def rtp(cls):
        total = sum(cls.SYMBOLS.values())
        result = 0
        for combo in product(cls.SYMBOLS, repeat=3):
            prob = 1
            for s in combo:
                prob *= cls.SYMBOLS[s] / total
            m = cls.evaluate(list(combo))
            if m > 0:
                result += prob * (m + 1)   # stake comes back plus the win
        return result