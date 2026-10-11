"""
 
Gold Rush: a 4 x 3 slot machine with a pick-a-mine-cart bonus game.
 
    - The grid is 4 rows of 3 symbols. Every row is a payline, and a row of three
      matching symbols pays N to 1 on the whole bet (rows add together).
    - Mine Cart is the bonus symbol. It never pays on a line, and a row that
      contains one does not pay.
    - 3 or more Mine Carts anywhere on the grid open the bonus: the player picks
      one of 5 mine carts and wins the prize inside it.
 
    The prize is decided inside resolve(), so the bet is settled once for the whole
    round. The pick is for show: the result carries the prize plus the other carts'
    contents, and the screen puts the prize in whichever cart the player clicks and
    fills the remaining carts from "others".
 
"""

from .slot import Slot


class GoldRush(Slot):
 
    title = "Gold Rush"
    ROWS = 4
    COLS = 3
 
    BONUS = "mine_cart"
 
    # symbol -> weight (higher = more common) | symbol -> pays N to 1 (net win = bet * N)
    SYMBOLS = {"pickaxe": 26, "lantern": 22, "nugget": 18, "dynamite": 12, "gold_bar": 6, BONUS: 4,}
    PAYTABLE = {"pickaxe": 1, "lantern": 2, "nugget": 3, "dynamite": 6, "gold_bar": 20,}
 
    CARTS_NEEDED = 3
    BONUS_CARTS = 5
 
    # bonus prize (pays N to 1) -> weight
    BONUS_PRIZES = {5: 35, 10: 30, 20: 20, 50: 10, 100: 4, 250: 1}
 
    @classmethod
    def row_pay(cls, row):
        if cls.BONUS in row:
            return 0
        if row[0] == row[1] == row[2]:
            return cls.PAYTABLE[row[0]]
        return 0
 
    @classmethod
    def grid_pay(cls, grid):
        wins = []
        for i, row in enumerate(grid):
            pay = cls.row_pay(row)
            if pay:
                wins.append({"row": i, "multiplier": pay})
        return sum(w["multiplier"] for w in wins), wins
 
    @classmethod
    def cart_count(cls, grid):
        return sum(row.count(cls.BONUS) for row in grid)
 
    @classmethod
    def resolve(cls, grid, rng):
        total, wins = cls.grid_pay(grid)
        features = {}
 
        if cls.cart_count(grid) >= cls.CARTS_NEEDED:
            prizes = list(cls.BONUS_PRIZES)
            weights = list(cls.BONUS_PRIZES.values())
            prize = rng.choices(prizes, weights=weights)[0]
            others = rng.choices(prizes, weights=weights, k=cls.BONUS_CARTS - 1)
            features["bonus"] = {"carts": cls.BONUS_CARTS, "prize": prize, "others": others}
            total += prize
 
        return {"multiplier": total, "wins": wins, "features": features}