"""
Cows Gone Wild: a 4 x 3 slot machine with Hold & Respin Barnyard Bonus.

    - Base grid is 4 columns x 3 rows (3 horizontal paylines of 4 matching symbols).
    - Golden Jug is the bonus coin symbol carrying random multiplier cash values.
    - 4 or more Golden Jugs anywhere on the grid trigger the Barnyard Respin feature.
    - The bonus expands the grid dynamically:
        * Starts at 5 columns x 3 rows (15 cells) with 3 respins.
        * Collecting 4 additional jugs (+4) unlocks the 6th column (6 cols x 3 rows = 18 cells)
          and resets the respin counter back to 3.
        * Boss Cow can land during respins to fire target beams multiplying all currently
          locked jug values by 2x, 3x, or 5x, then vanishes (does not lock).
    - Clearing all 18 cells awards the Grand Moo-lah Jackpot (+500x bet).
"""

from .slot import Slot


class CowsGoneWild(Slot):

    title = "Cows Gone Wild"
    ROWS = 3
    COLS = 4

    BONUS = "golden_jug"

    # Base game symbols and weights
    SYMBOLS = {
        "milk_carton": 28,
        "barn": 22,
        "tractor": 16,
        "farmer": 10,
        "ufo": 4,
        BONUS: 6,
    }

    # 4 matching symbols across a 4-symbol row
    PAYTABLE = {
        "milk_carton": 2,
        "barn": 4,
        "tractor": 8,
        "farmer": 15,
        "ufo": 50,
    }

    JUGS_NEEDED = 4
    INITIAL_RESPINS = 3
    EXPANSION_THRESHOLD = 4  # +4 new jugs during bonus unlocks 6th column
    GRAND_JACKPOT = 500      # Awarded for full 18-cell grid fill

    # Base jug multiplier weights (Cash values on jugs)
    JUG_PRIZES = {1: 40, 2: 30, 3: 15, 5: 10, 10: 4, 25: 1}

    # Boss Cow multiplier boosts and weights
    BOSS_MULTIPLIERS = {2: 60, 3: 30, 5: 10}

    @classmethod
    def row_pay(cls, row):
        """A row pays if all 4 symbols match and contain no bonus symbols."""
        if cls.BONUS in row:
            return 0
        if row[0] == row[1] == row[2] == row[3]:
            return cls.PAYTABLE.get(row[0], 0)
        return 0

    @classmethod
    def grid_pay(cls, grid):
        """Calculate line pay across all 3 rows."""
        wins = []
        for i, row in enumerate(grid):
            pay = cls.row_pay(row)
            if pay:
                wins.append({"row": i, "multiplier": pay})
        return sum(w["multiplier"] for w in wins), wins

    @classmethod
    def find_initial_jugs(cls, grid, rng):
        """Collect all triggering jugs and assign them initial multiplier values."""
        prizes = list(cls.JUG_PRIZES)
        weights = list(cls.JUG_PRIZES.values())
        jugs = {}

        for r in range(cls.ROWS):
            for c in range(cls.COLS):
                if grid[r][c] == cls.BONUS:
                    jugs[(r, c)] = rng.choices(prizes, weights=weights)[0]
        return jugs

    @classmethod
    def _simulate_respins(cls, initial_jugs, rng):
        """
        Simulate the entire Hold & Respin game from 5x3 up to 6x3.
        Returns total feature payout and a step-by-step event log for the UI.
        """
        cols = 5
        rows = 3
        respins_left = cls.INITIAL_RESPINS
        locked_jugs = dict(initial_jugs)
        new_jugs_collected = 0
        expanded_to_6 = False
        events = []

        # Record initial trigger setup
        events.append({
            "type": "INIT_BONUS",
            "cols": cols,
            "rows": rows,
            "locked_jugs": {f"{r},{c}": val for (r, c), val in locked_jugs.items()},
            "respins_left": respins_left,
        })

        prizes = list(cls.JUG_PRIZES)
        prize_weights = list(cls.JUG_PRIZES.values())
        boss_mults = list(cls.BOSS_MULTIPLIERS)
        boss_weights = list(cls.BOSS_MULTIPLIERS.values())

        # Main Respin Loop
        while respins_left > 0 and len(locked_jugs) < (cols * rows):
            respins_left -= 1
            spin_landed_new_jug = False
            boss_spawned = False
            boss_pos = None
            boss_mult = 1
            new_spins = {}

            # All unlocked open cells spin
            empty_cells = [(r, c) for r in range(rows) for c in range(cols) if (r, c) not in locked_jugs]

            # 1. Check for Boss Cow landing (single chance per respin, ~12% probability)
            if rng.random() < 0.12 and empty_cells:
                boss_pos = rng.choice(empty_cells)
                boss_mult = rng.choices(boss_mults, weights=boss_weights)[0]
                boss_spawned = True
                empty_cells.remove(boss_pos)

            # 2. Spin remaining empty cells (~16% chance to land a new Golden Jug)
            for pos in empty_cells:
                if rng.random() < 0.16:
                    val = rng.choices(prizes, weights=prize_weights)[0]
                    new_spins[pos] = val

            # Process Boss Cow multiplier strike event first if spawned
            if boss_spawned:
                # Multiply all currently existing locked jugs
                for pos in locked_jugs:
                    locked_jugs[pos] *= boss_mult

                events.append({
                    "type": "BOSS_COW_STRIKE",
                    "boss_pos": boss_pos,
                    "multiplier": boss_mult,
                    "targets": [
                        {"pos": list(pos), "new_val": locked_jugs[pos]}
                        for pos in locked_jugs
                    ],
                })
                respins_left = cls.INITIAL_RESPINS

            # Process New Jugs landing
            if new_spins:
                spin_landed_new_jug = True
                respins_left = cls.INITIAL_RESPINS
                for pos, val in new_spins.items():
                    locked_jugs[pos] = val
                    new_jugs_collected += 1

                events.append({
                    "type": "NEW_JUGS_LOCKED",
                    "new_jugs": [{ "pos": list(pos), "val": val } for pos, val in new_spins.items()],
                    "respins_left": respins_left,
                    "total_locked": len(locked_jugs),
                })

            # Check for grid expansion (+4 jugs collected from bonus spins)
            if not expanded_to_6 and new_jugs_collected >= cls.EXPANSION_THRESHOLD:
                cols = 6
                expanded_to_6 = True
                respins_left = cls.INITIAL_RESPINS  # Bonus reset reward on column unlock
                events.append({
                    "type": "EXPAND_GRID",
                    "cols": cols,
                    "rows": rows,
                    "respins_left": respins_left,
                })

            # If blank spin, log the decrement
            if not spin_landed_new_jug and not boss_spawned:
                events.append({
                    "type": "BLANK_RESPIN",
                    "respins_left": respins_left,
                })

        # Calculate final payouts
        bonus_total = sum(locked_jugs.values())
        grand_won = len(locked_jugs) >= (cols * rows)
        if grand_won:
            bonus_total += cls.GRAND_JACKPOT
            events.append({"type": "GRAND_JACKPOT", "amount": cls.GRAND_JACKPOT})

        events.append({
            "type": "BONUS_COMPLETE",
            "total_multiplier": bonus_total,
            "grand_won": grand_won,
        })

        return bonus_total, events

    @classmethod
    def resolve(cls, grid, rng):
        base_pay, wins = cls.grid_pay(grid)
        total_payout = base_pay
        features = {}

        initial_jugs = cls.find_initial_jugs(grid, rng)
        if len(initial_jugs) >= cls.JUGS_NEEDED:
            bonus_multiplier, respin_events = cls._simulate_respins(initial_jugs, rng)
            total_payout += bonus_multiplier
            features["respins"] = {
                "initial_count": len(initial_jugs),
                "bonus_multiplier": bonus_multiplier,
                "events": respin_events,
            }

        return {"multiplier": total_payout, "wins": wins, "features": features}