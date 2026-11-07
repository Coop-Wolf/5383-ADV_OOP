from .slot import Slot

class Fruits(Slot):
 
    title = "Classic Fruit"
    ROWS = 1
    COLS = 3
 
    # symbol -> weight (higher = more common)
    SYMBOLS = {"cherry": 30, "lemon": 25, "bar": 20, "bell": 15, "seven": 8, "diamond": 2}
 
    # three of a kind -> pays N to 1 (net win = bet * N)
    PAYTABLE = {"cherry": 8, "lemon": 12, "bar": 20, "bell": 40, "seven": 100, "diamond": 500}
    TWO_CHERRY_PAYOUT = 1
 
    @classmethod
    def evaluate(cls, reels):
        if reels[0] == reels[1] == reels[2]:
            return cls.PAYTABLE[reels[0]]
        if reels[0] == reels[1] == "cherry":
            return cls.TWO_CHERRY_PAYOUT
        return 0
 
    @classmethod
    def resolve(cls, grid, rng=None):
        multiplier = cls.evaluate(grid[0])
        wins = [{"row": 0, "multiplier": multiplier}] if multiplier else []
        return {"multiplier": multiplier, "wins": wins, "features": {}}