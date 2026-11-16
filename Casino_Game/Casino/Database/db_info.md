# Coop's Casino: Database Tables

The database is a single SQLite file (`casino.db`) with two tables. The schema is defined in `createDB.py`, and all reads and writes go through the `Database` class in `database.py`.

## How the tables relate

```
players (1) ────────< player_stats (up to 3 rows per player)
   id  ◄──────────────  player_id
```

Each player has one row in `players` and up to three rows in `player_stats`, one per game. Deleting a player deletes their stats too (`ON DELETE CASCADE`).

---

## `players`

One row per player account.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | Primary key, auto-assigned | Unique player ID |
| `username` | TEXT | Not null, unique, case-insensitive, validated (see below) | Name used to log in |
| `chips` | INTEGER | Not null, default 1000 | Current chip balance |
| `created_at` | TEXT | Not null, defaults to the current timestamp | When the account was created |

### Username rules

| Rule | Detail |
|---|---|
| Length | 2 to 10 characters, counting the space |
| Allowed characters | Letters, digits, and underscores, plus at most one space |
| First character | Must be a letter |
| Spaces | Only one, and not at the start or end |
| Case | `Trevor` and `trevor` are the same player; the first spelling used is kept |
| Reserved names | `dealer`, `house`, `casino`, `admin`, `guest`, `player`, `players` (any capitalization) |

The database enforces everything above except the reserved names, which are checked in Python.

---

## `player_stats`

One row per player per game. A row is created the first time a player finishes a round of that game.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `player_id` | INTEGER | Not null, foreign key to `players.id` | Which player the stats belong to |
| `game` | TEXT | Not null | `VideoPoker`, `Blackjack`, or `War` |
| `rounds_played` | INTEGER | Not null, default 0 | Total finished rounds, including pushes |
| `wins` | INTEGER | Not null, default 0 | Rounds won |
| `losses` | INTEGER | Not null, default 0 | Rounds lost |
| `biggest_win` | INTEGER | Not null, default 0 | Largest net gain from a single winning round |
| `net_profit` | INTEGER | Not null, default 0 | Total winnings minus total losses (can be negative) |

**Primary key:** (`player_id`, `game`), so each player has at most one row per game.

Pushes (ties) have no column of their own. They are counted in `rounds_played` and change nothing else, so:

```
pushes = rounds_played - wins - losses
```

The game name is validated in Python (`GAMES` in `database.py`), not by the database.

---

## Example data

**players**

| id | username | chips | created_at |
|---|---|---|---|
| 1 | Trevor | 1100 | 2026-10-01 14:30:00 |
| 2 | Ty | 850 | 2026-10-01 15:02:11 |

**player_stats**

| player_id | game | rounds_played | wins | losses | biggest_win | net_profit |
|---|---|---|---|---|---|---|
| 1 | Blackjack | 2 | 1 | 0 | 150 | 150 |
| 1 | War | 1 | 0 | 1 | 0 | -50 |
| 2 | VideoPoker | 5 | 2 | 3 | 300 | -150 |

Trevor has no `VideoPoker` row because he hasn't played it. The `get_stats()` method fills in zeros for any game a player hasn't played.