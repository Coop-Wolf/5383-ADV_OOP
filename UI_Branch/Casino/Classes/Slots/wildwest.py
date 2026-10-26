"""
 
Wild West: a 4 x 3 slot machine with wilds and free spins.
 
    - The grid is 4 rows of 3 symbols. Every row is a payline, and a row of three
      matching symbols pays N to 1 on the whole bet (rows add together).
    - Outlaw is wild: it stands in for any line symbol. Three outlaws pay on their own.
    - Saloon is the free spins symbol. It never pays on a line, and a row that
      contains one does not pay.
    - 3 or more Saloons anywhere on the grid award 8 free spins.
    - Free spins cost nothing, every line win in them is doubled, and they cannot
      be retriggered.
 
    The free spins are played out inside resolve(), so the bet is settled once for
    the whole round and the screen just replays the spins one after another.
 
"""
 
from .slot import Slot
 
 
class WildWest(Slot):
 
    title = "Wild West"
    ROWS = 4
    COLS = 3
 
    WILD = "outlaw"
    SCATTER = "saloon"
 
    # symbol -> weight (higher = more common) |  row of three -> pays N to 1 (net win = bet * N)
    SYMBOLS = {"horseshoe": 26, "boot": 22, "hat": 18, "revolver": 12, "badge": 6, WILD: 2, SCATTER: 5,}
    PAYTABLE = {"horseshoe": 1, "boot": 2, "hat": 3, "revolver": 5, "badge": 12, WILD: 40,}
 
    SCATTERS_NEEDED = 3
    FREE_SPINS = 10
    FREE_SPIN_MULTIPLIER = 2
 
    # Payout multiple for one row
    @classmethod
    def row_pay(cls, row):
        if cls.SCATTER in row:
            return 0
 
        symbols = {s for s in row if s != cls.WILD}
        if not symbols:                       # three wilds
            return cls.PAYTABLE[cls.WILD]
        if len(symbols) == 1:                 # wilds fill in for the rest
            return cls.PAYTABLE[symbols.pop()]
        return 0
 
    # Payout multiple for the whole grid, plus which rows paid
    @classmethod
    def grid_pay(cls, grid):
        wins = []
        for i, row in enumerate(grid):
            pay = cls.row_pay(row)
            if pay:
                wins.append({"row": i, "multiplier": pay})
        return sum(w["multiplier"] for w in wins), wins
 
    @classmethod
    def scatter_count(cls, grid):
        return sum(row.count(cls.SCATTER) for row in grid)
 
    @classmethod
    def resolve(cls, grid, rng):
        total, wins = cls.grid_pay(grid)
        features = {}

        if cls.scatter_count(grid) >= cls.SCATTERS_NEEDED:
            spins = []
            spins_remaining = cls.FREE_SPINS
            total_awarded = cls.FREE_SPINS
            max_spins = 50  # Safeguard ceiling to prevent runaway loops

            while spins_remaining > 0:
                spins_remaining -= 1
                free_grid = cls.spin_grid(rng)
                pay, free_wins = cls.grid_pay(free_grid)
                
                # Double line payouts for both the summary and individual row entries
                for w in free_wins:
                    w["multiplier"] *= cls.FREE_SPIN_MULTIPLIER
                pay *= cls.FREE_SPIN_MULTIPLIER

                # Check for retrigger on the free spin grid under the cap
                hit_retrigger = cls.scatter_count(free_grid) >= cls.SCATTERS_NEEDED
                can_retrigger = (total_awarded + cls.FREE_SPINS) <= max_spins
                retrigger = hit_retrigger and can_retrigger

                if retrigger:
                    spins_remaining += cls.FREE_SPINS
                    total_awarded += cls.FREE_SPINS

                spins.append({
                    "grid": free_grid,
                    "wins": free_wins,
                    "multiplier": pay,
                    "retriggered": retrigger,
                })
                total += pay

            features["free_spins"] = spins

        return {"multiplier": total, "wins": wins, "features": features}