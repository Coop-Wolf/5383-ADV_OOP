"""
Cows Gone Wild: a 4 x 3 slot machine with Hold & Respin Barnyard Bonus.

    - Base grid is 4 columns x 3 rows (3 horizontal paylines of 4 matching symbols).
    - Golden Jug is the bonus coin symbol carrying random multiplier cash values.
    - Golden Jugs trigger the Barnyard Respin feature when reaching JUGS_NEEDED.
    - The bonus expands the grid vertically:
        * Starts at 4 columns x 3 rows with 3 respins.
        * Collecting +4 new jugs unlocks the 4th row (4x4) and resets respins to 3.
        * Collecting +8 total new jugs (+4 more) unlocks the 5th row (4x5) and resets respins to 3.
        * Boss Cow lands during respins, reveals its multiplier boost (2x, 3x, or 5x),
          and fires sequential target bolts multiplying existing locked jugs.
    - Clearing all 20 cells awards the Grand Moo-lah Jackpot (+500x bet).
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

    # Standard farm symbols available to land on unlocked bonus cells
    NON_BONUS_SYMBOLS = ["milk_carton", "barn", "tractor", "farmer", "ufo"]

    # 4 matching symbols across a 4-symbol row
    PAYTABLE = {
        "milk_carton": 2,
        "barn": 4,
        "tractor": 8,
        "farmer": 15,
        "ufo": 50,
    }

    JUGS_NEEDED = 1
    INITIAL_RESPINS = 3
    EXPANSION_THRESHOLD = 4  # +4 new jugs per expansion stage
    GRAND_JACKPOT = 500      # Awarded for full 20-cell grid fill

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
        """Calculate line pay across all rows."""
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
        Simulate the Hold & Respin feature expanding from 4x3 to 4x4, then to 4x5.
        Returns total feature payout and a step-by-step event log for the UI.
        """
        cols = 4
        rows = 3
        respins_left = cls.INITIAL_RESPINS
        locked_jugs = dict(initial_jugs)
        new_jugs_collected = 0
        events = []

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
            unlocked_symbol_display = {}

            # All unlocked open cells spin
            empty_cells = [(r, c) for r in range(rows) for c in range(cols) if (r, c) not in locked_jugs]

            # 1. Check for Boss Cow landing (single chance per respin, ~12% probability)
            if rng.random() < 0.12 and empty_cells:
                boss_pos = rng.choice(empty_cells)
                boss_mult = rng.choices(boss_mults, weights=boss_weights)[0]
                boss_spawned = True
                empty_cells.remove(boss_pos)

            # 2. Spin remaining empty cells
            for pos in empty_cells:
                if rng.random() < 0.18:
                    val = rng.choices(prizes, weights=prize_weights)[0]
                    new_spins[pos] = val
                else:
                    unlocked_symbol_display[pos] = rng.choice(cls.NON_BONUS_SYMBOLS)

            # Record landing event for UI reel stop
            events.append({
                "type": "RESPIN_RESULT",
                "rows": rows,
                "cols": cols,
                "respins_left": respins_left,
                "new_jugs": [{"pos": list(pos), "val": val} for pos, val in new_spins.items()],
                "unlocked_symbols": {f"{r},{c}": sym for (r, c), sym in unlocked_symbol_display.items()},
                "boss_pos": list(boss_pos) if boss_spawned else None,
                "boss_mult": boss_mult if boss_spawned else None,
            })

            # LOCK NEW JUGS FIRST so Boss Cow can target them if spawned on the same spin
            if new_spins:
                spin_landed_new_jug = True
                respins_left = cls.INITIAL_RESPINS
                for pos, val in new_spins.items():
                    locked_jugs[pos] = val
                    new_jugs_collected += 1

            # PROCESS BOSS COW STRIKE (now targeting ALL locked jugs, including newly landed ones)
            if boss_spawned:
                for pos in locked_jugs:
                    locked_jugs[pos] *= boss_mult

                sorted_targets = sorted(
                    locked_jugs.keys(),
                    key=lambda p: (p[1], p[0])
                )

                events.append({
                    "type": "BOSS_COW_STRIKE",
                    "boss_pos": boss_pos,
                    "multiplier": boss_mult,
                    "targets": [
                        {"pos": list(pos), "new_val": locked_jugs[pos]}
                        for pos in sorted_targets
                    ],
                })
                respins_left = cls.INITIAL_RESPINS

            # Check for vertical grid expansion (Stage 1: +4 -> 4 rows; Stage 2: +8 -> 5 rows)
            if rows == 3 and new_jugs_collected >= cls.EXPANSION_THRESHOLD:
                rows = 4
                respins_left = cls.INITIAL_RESPINS
                events.append({
                    "type": "EXPAND_GRID",
                    "cols": cols,
                    "rows": rows,
                    "respins_left": respins_left,
                })
            elif rows == 4 and new_jugs_collected >= (cls.EXPANSION_THRESHOLD * 2):
                rows = 5
                respins_left = cls.INITIAL_RESPINS
                events.append({
                    "type": "EXPAND_GRID",
                    "cols": cols,
                    "rows": rows,
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
        # Store initial jug values so base spins always render their multipliers
        features["initial_jugs"] = {f"{r},{c}": val for (r, c), val in initial_jugs.items()}

        if len(initial_jugs) >= cls.JUGS_NEEDED:
            bonus_multiplier, respin_events = cls._simulate_respins(initial_jugs, rng)
            total_payout += bonus_multiplier
            features["respins"] = {
                "initial_count": len(initial_jugs),
                "bonus_multiplier": bonus_multiplier,
                "events": respin_events,
            }

        return {"multiplier": total_payout, "wins": wins, "features": features}