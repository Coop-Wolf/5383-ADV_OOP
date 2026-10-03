import sqlite3


SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT NOT NULL UNIQUE COLLATE NOCASE
               CHECK (length(username) BETWEEN 2 AND 10
                      AND username GLOB '[A-Za-z]*'
                      AND username NOT GLOB '*[^A-Za-z0-9_ ]*'
                      AND username = trim(username)
                      AND length(username) - length(replace(username, ' ', '')) <= 1),
    chips      INTEGER NOT NULL DEFAULT 100,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
 
CREATE TABLE IF NOT EXISTS player_stats (
    player_id     INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    game          TEXT NOT NULL,
    rounds_played INTEGER NOT NULL DEFAULT 0,
    wins          INTEGER NOT NULL DEFAULT 0,
    losses        INTEGER NOT NULL DEFAULT 0,
    biggest_win   INTEGER NOT NULL DEFAULT 0,
    net_profit    INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (player_id, game)
);
"""


DB_PATH = "casino.db"

def create_database(path=DB_PATH):
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    conn.close()


if __name__ == "__main__":
    create_database()
    print(f"Database ready: {DB_PATH}")