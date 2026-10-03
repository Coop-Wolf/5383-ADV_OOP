# Casino Project Development Milestones (Pygame + SQLite)

| Week | Concrete Implementation | Completion Indicator |
|---|---|---|
| 1 | Design the SQLite schema (players, chips, statistics tables), create the database, and build a data access layer (create, read, update player records) | A script creates the database, inserts a player, updates their chips, and reads the record back correctly. |
| 2 | Implement player accounts (create account, login) and persist chips and statistics | A player can be created, quit the program, restart, log back in, and still have their chips and stats. |
| 3 | Connect the database to the casino engine so results save after each round, and add error handling (invalid login, duplicate accounts) | Playing rounds in the terminal changes the saved chips and stats, and they persist after a restart. Invalid logins and duplicate accounts are rejected cleanly. |
| 4 | Build the Pygame foundation: window, main game loop, screen/state manager, and reusable UI components (buttons, text, input boxes) | The app launches, and clickable buttons switch between placeholder screens. |
| 5 | Build the login screen, casino lobby, and player info display (name, chips), connected to the database | A user can create an account or log in through the GUI and see their saved chip total in the lobby. |
| 6 | Build card rendering and betting controls (card drawing helpers, chip/bet buttons) | A test screen displays any card or hand correctly, and bet controls adjust a bet without exceeding the player's chips. |
| 7 | Build the Blackjack screen with action buttons (hit, stand, double) connected to the game engine | Blackjack is fully playable with the mouse, and chips update and save after each round. |
| 8 | Build the Video Poker screen (card selection/holding, draw, payout display) | Video Poker is fully playable with the mouse, and results and chips are saved to the database. |
| 9 | Build the War screen and add basic styling across all screens (consistent layout, colors, fonts) | War is fully playable, and all three games share a consistent look and return to the lobby. |
| 10 | Build the statistics screen, fix bugs, handle edge cases (out of chips, invalid bets), refactor, and finalize documentation | A full demo run works without crashes: log in, play all three games, view stats, exit, return, and see the data persisted. |
