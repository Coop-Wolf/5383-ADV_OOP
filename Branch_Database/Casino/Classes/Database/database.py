import sqlite3

from createDB import DB_PATH, create_database

STARTING_CHIPS = 100
GAMES = ("VideoPoker", "Blackjack", "War")
OUTCOMES = ("win", "loss", "push")


class Database:
    def __init__(self, path=DB_PATH):
        create_database(path)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        

    # Basic operations
    def close(self):
        self.conn.close()
 
    def __enter__(self):
        return self
 
    def __exit__(self, *exc):
        self.close()
 
 
    # Players
    def get_or_create_player(self, username):
        """
        Look up a player by username (case-insensitive), creating one if needed.
        Returns (player, is_new) where player is a dict with id, username, chips.
        """
        
        query = "SELECT id, username, chips FROM players WHERE username = ?"
        row = self.conn.execute(query, (username,)).fetchone()
        is_new = row is None
 
        # Create new player if username was not found
        if is_new:
            with self.conn:
                self.conn.execute("INSERT INTO players (username, chips) VALUES (?, ?)", (username, STARTING_CHIPS),)
            row = self.conn.execute(query, (username,)).fetchone()
 
        return dict(row), is_new
 
 
    def save_chips(self, player_id, chips):
        """
        Set a player's chip balance outright (used for the save-on-exit safety net).
        """
        
        with self.conn:
            self.conn.execute("UPDATE players SET chips = ? WHERE id = ?", (chips, player_id))
 

    # Stats
    def get_stats(self, player_id):
        """
        Return {game: stats_dict} for every game, with zeros for unplayed games.
        """
        
        stats = {
            game: {
                "game": game,
                "rounds_played": 0,
                "wins": 0,
                "losses": 0,
                "biggest_win": 0,
                "net_profit": 0,
            }
            for game in GAMES
        }
        rows = self.conn.execute(
            "SELECT game, rounds_played, wins, losses, biggest_win, net_profit "
            "FROM player_stats WHERE player_id = ?",
            (player_id,),).fetchall()
        
        for row in rows:
            stats[row["game"]] = dict(row)
        return stats
 
 
    def record_result(self, player_id, game, outcome, net_change):
        """
        Record one finished round. Chips and stats update in a single transaction.
 
        outcome:    "win", "loss", or "push"
        net_change: payout minus bet (positive for a win, negative for a loss, 0 for a push)
        Returns the player's new chip balance.
        """
        
        if game not in GAMES:
            raise ValueError(f"Unknown game: {game}")
        if outcome not in OUTCOMES:
            raise ValueError(f"Unknown outcome: {outcome}")
        if (
            (outcome == "win" and net_change <= 0)
            or (outcome == "loss" and net_change >= 0)
            or (outcome == "push" and net_change != 0)
        ):
            raise ValueError(f"net_change {net_change} does not match outcome '{outcome}'")
 
        wins = 1 if outcome == "win" else 0
        losses = 1 if outcome == "loss" else 0
        best_win = net_change if outcome == "win" else 0
 
        with self.conn:
            
            # Update players chips
            self.conn.execute("UPDATE players SET chips = chips + ? WHERE id = ?",(net_change, player_id),)
            
            # Insert (if no stats up) or Update (player played before) with outcome of recent round
            self.conn.execute(
                """
                INSERT INTO player_stats
                    (player_id, game, rounds_played, wins, losses, biggest_win, net_profit)
                VALUES (?, ?, 1, ?, ?, ?, ?)
                ON CONFLICT(player_id, game) DO UPDATE SET
                    rounds_played = rounds_played + 1,
                    wins          = wins + excluded.wins,
                    losses        = losses + excluded.losses,
                    biggest_win   = MAX(biggest_win, excluded.biggest_win),
                    net_profit    = net_profit + excluded.net_profit
                """,
                (player_id, game, wins, losses, best_win, net_change),)

        # Get chip count for player
        row = self.conn.execute("SELECT chips FROM players WHERE id = ?", (player_id,)).fetchone()
        return row["chips"]