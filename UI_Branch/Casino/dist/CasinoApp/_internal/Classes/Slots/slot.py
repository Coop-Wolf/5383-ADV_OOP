"""
 
Slot machines for the Casino App.
 
    SlotMachine  - shared base class: spins a grid, settles the bet, estimates RTP.
    Slots        - Classic Fruit: 3 reels, one payline (the original machine).
 
    Every machine keeps name = "Slots" so all slot games share one stats entry in
    the database. Each machine has its own title for the screen.
 
    A machine only fills in its settings and overrides resolve():
 
        ROWS, COLS   - size of the grid (each row is one payline)
        SYMBOLS      - symbol -> weight (higher = more common)
        resolve()    - turn a grid into a total multiplier (plus any features)
 
    The bet is settled once per spin. Free spins and bonus prizes are decided inside
    resolve(), so the screen only reveals a result that is already final and saved.
 
"""
 
import random
from itertools import product
from ..game import Game
from ..player import Player
 
 
class Slot(Game):
 
    # Shared database key for every slot machine
    name = "Slots"
    title = "Slots"
    player_class = Player
 
    # Subclasses override these
    ROWS = 1
    COLS = 3
    SYMBOLS = {}
 
    def __init__(self, player, db=None, rng=None):
        super().__init__(player, db)
        self.rng = rng or random.Random()
        self.bet = 0
        self.grid = []
 
    # Pick a random symbol for every cell, using the symbol weights
    @classmethod
    def spin_grid(cls, rng):
        names = list(cls.SYMBOLS)
        weights = list(cls.SYMBOLS.values())
        return [rng.choices(names, weights=weights, k=cls.COLS) for _ in range(cls.ROWS)]
 
    # Turn a grid into {"multiplier": total, "wins": [...], "features": {...}}
    # The multiplier is the total profit as a multiple of the bet (0 = loss).
    @classmethod
    def resolve(cls, grid, rng):
        raise NotImplementedError
 
    # Take the bet and spin; the screen animates toward self.grid
    def deal(self, bet):
        self.collect_bet(self.game_player, bet)
        self.bet = bet
        self.grid = self.spin_grid(self.rng)
        return self.grid
 
    # Resolve the spin, settle the bet, return a result for the screen
    def determine_winner(self):
        outcome_data = self.resolve(self.grid, self.rng)
        multiplier = outcome_data["multiplier"]
        outcome = "win" if multiplier > 0 else "loss"
        net_change = self.settle(self.game_player, self.bet, outcome, multiplier)
 
        result = {
            "grid": self.grid,
            "outcome": outcome,
            "multiplier": multiplier,
            "net_change": net_change,
            "wins": outcome_data.get("wins", []),
            "features": outcome_data.get("features", {}),
        }
 
        # Single-row machines also expose the row as a flat list (original format)
        if self.ROWS == 1:
            result["reels"] = self.grid[0]
 
        return result
 
    # Return-to-player for a $1 bet. Exact for single-row machines, estimated otherwise.
    @classmethod
    def rtp(cls, spins=500_000, seed=1):
        if cls.ROWS > 1:
            return cls.simulate(spins, seed)["rtp"]
 
        total = sum(cls.SYMBOLS.values())
        result = 0
        for combo in product(cls.SYMBOLS, repeat=cls.COLS):
            prob = 1
            for s in combo:
                prob *= cls.SYMBOLS[s] / total
            m = cls.resolve([list(combo)], None)["multiplier"]
            if m > 0:
                result += prob * (m + 1)   # stake comes back plus the win
        return result
 
    # Play many spins with no player or database; returns RTP, hit rate, feature rates
    @classmethod
    def simulate(cls, spins=500_000, seed=1):
        rng = random.Random(seed)
        returned = 0
        hits = 0
        feature_counts = {}
 
        for _ in range(spins):
            data = cls.resolve(cls.spin_grid(rng), rng)
            m = data["multiplier"]
            if m > 0:
                returned += m + 1
                hits += 1
            for key in data.get("features", {}):
                feature_counts[key] = feature_counts.get(key, 0) + 1
 
        return {
            "rtp": returned / spins,
            "hit_rate": hits / spins,
            "features": {k: v / spins for k, v in feature_counts.items()},
        }