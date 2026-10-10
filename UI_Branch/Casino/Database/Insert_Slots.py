"""

One-time script: add a Slots row to player_stats for every existing player.

    Usage:
        python add_slots_stats.py                 (looks for casino.db near this script)
        python add_slots_stats.py path\\to\\casino.db

    Safe to run more than once: players that already have a Slots row are skipped.
    A backup copy of the database is made before anything is changed.

"""

import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

GAME = "Slots"
COLUMNS = ("player_id", "game", "rounds_played", "wins", "losses", "biggest_win", "net_profit")


def find_db(arg):
    if arg:
        return Path(arg)

    here = Path(__file__).resolve().parent
    for folder in (here, here.parent, here / "Database", here.parent / "Database"):
        candidate = folder / "casino.db"
        if candidate.exists():
            return candidate

    sys.exit("Could not find casino.db. Pass the path: python add_slots_stats.py path\\to\\casino.db")


def main():
    db_path = find_db(sys.argv[1] if len(sys.argv) > 1 else None)
    if not db_path.exists():
        sys.exit(f"Database not found: {db_path}")

    # Backup first
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.with_name(f"{db_path.stem}_backup_{stamp}{db_path.suffix}")
    shutil.copy2(db_path, backup)
    print(f"Database: {db_path}")
    print(f"Backup:   {backup}")

    conn = sqlite3.connect(db_path)
    try:
        # Make sure the table looks the way we expect before touching it
        existing = {row[1] for row in conn.execute("PRAGMA table_info(player_stats)")}
        missing = [c for c in COLUMNS if c not in existing]
        if missing:
            sys.exit(f"player_stats is missing columns {missing}. Nothing was changed.")

        with conn:  # one transaction: all rows or none
            cursor = conn.execute(
                """
                INSERT INTO player_stats
                    (player_id, game, rounds_played, wins, losses, biggest_win, net_profit)
                SELECT p.id, ?, 0, 0, 0, 0, 0
                FROM players p
                WHERE NOT EXISTS (
                    SELECT 1 FROM player_stats s
                    WHERE s.player_id = p.id AND s.game = ?
                )
                """,
                (GAME, GAME),
            )
            added = cursor.rowcount

        total = conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]
        with_slots = conn.execute(
            "SELECT COUNT(*) FROM player_stats WHERE game = ?", (GAME,)
        ).fetchone()[0]

        print(f"Added {added} Slots row(s).")
        print(f"{with_slots} of {total} players now have a {GAME} row.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()