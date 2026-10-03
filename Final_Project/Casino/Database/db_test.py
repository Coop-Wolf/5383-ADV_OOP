"""
Checkpoint test for Milestone 3
===============================

Goal: a player can leave the application, restart it, log back in, and
still have their information.

What this test simulates
------------------------
Session 1 (first time playing)
    - "Trevor" logs in for the first time, so a new player is created with
      STARTING_CHIPS.
    - Trevor plays three rounds:
        1. Blackjack win    +150 chips
        2. Blackjack push      0 chips (bet returned)
        3. War loss          -50 chips
    - The application closes (db.close()).

Session 2 (coming back later)
    - The application restarts and opens the same database file.
    - Trevor logs in as "trevor" (different capitalization).

What we expect to find
----------------------
    - Same player, not a new one, and the name is still stored as "Trevor".
    - Chips: STARTING_CHIPS + 150 + 0 - 50 = STARTING_CHIPS + 100.
    - Blackjack: 2 rounds played, 1 win, biggest win 150, net profit +150.
    - War: 1 loss, net profit -50.
    - VideoPoker: never played, so everything is zero.

How the checks work
-------------------
`assert` is a Python keyword that checks a statement is true. If it is,
the test moves on silently. If not, Python stops with an AssertionError
on that line, so you know which check failed.
"""
 
import os
import tempfile
 
from Final_Project.Casino.Database.database import Database, STARTING_CHIPS
 
 
def test_data_survives_restart():
    path = os.path.join(tempfile.mkdtemp(), "test_casino.db")
 
    # First "session": create a player and play some rounds.
    db = Database(path)
    player, is_new = db.get_or_create_player("Trevor")
    assert is_new
    db.record_result(player["id"], "Blackjack", "win", 150)
    db.record_result(player["id"], "Blackjack", "push", 0)
    db.record_result(player["id"], "War", "loss", -50)
    db.close()
 
    # Second "session": reopen the same file and log back in.
    db = Database(path)
    player, is_new = db.get_or_create_player("trevor")  # different case, same player
    assert not is_new
    assert player["username"] == "Trevor"  # original spelling is kept
    assert player["chips"] == STARTING_CHIPS + 100
 
    stats = db.get_stats(player["id"])
    assert stats["Blackjack"]["rounds_played"] == 2
    assert stats["Blackjack"]["wins"] == 1
    assert stats["Blackjack"]["biggest_win"] == 150
    assert stats["Blackjack"]["net_profit"] == 150
    assert stats["War"]["losses"] == 1
    assert stats["War"]["net_profit"] == -50
    assert stats["VideoPoker"]["rounds_played"] == 0
    db.close()
 
 
if __name__ == "__main__":
    test_data_survives_restart()
    print("All checkpoint tests passed.")
 
