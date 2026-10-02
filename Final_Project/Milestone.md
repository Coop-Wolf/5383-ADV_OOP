# Casino Project Milestones (Pygame + SQLite Desktop App)

**Tech stack:** Python, Pygame (GUI), SQLite (database)

---

# Milestone 1 — Finish the Casino Engine [CHECK]
*Week 0*

**Goal:** Make the current terminal casino stable and complete.

### Tasks

- [x] Finish Blackjack
- [x] Finish Video Poker
- [x] Finish War
- [x] Finish player management
- [x] Finish betting/chip management
- [x] Finish player statistics
- [x] Fix known bugs
- [x] Refactor duplicated/unnecessary code
- [x] Make sure game rules work correctly
- [x] Optimize OOP techniques by reusing code

### Checkpoint

> Blackjack, Video Poker, and War can be played reliably through the terminal.

---

# Milestone 1.5 — Video Poker [CHECK]
*Week 0*

- [x] Add Video Poker as a game
- [x] Keep multi-player Poker in the codebase for now, but do not use it
- [x] Test gameplay

---

# Milestone 2 — Separate Game Logic from the Terminal [CHECK]
*Week 0*

**Goal:** Make the casino engine independent of `input()` and `print()`.

### Tasks

- [x] Separate game logic from terminal UI
- [x] Move user input handling into the UI layer
- [x] Make game classes return game state/results
- [x] Make game actions callable through methods
- [x] Keep the terminal UI working as a client of the game engine

### Target Architecture

```
             ┌── Terminal UI
Game Logic ──┤
             └── Pygame UI (future)
```

### Checkpoint

> The casino games can run without depending on the terminal.

---

# Milestone 3 — Add the SQLite Database
*Week 1*

**Goal:** Persist player information so it survives when the application stops.

### Tasks

- [x] Design the database structure (players, chips, statistics)
- [x] Create the SQLite database and player table
- [x] Build a data access layer (create, read, update player records, delete)
- [x] Store player accounts
- [x] Store chips
- [x] Store player statistics
- [x] Load player information when logging in
- [x] Save updated information when leaving
- [x] Decide when additional saves should occur during gameplay (e.g., after each round)

### Checkpoint

> A player can leave the application, restart it, log back in, and still have their information.

---

# Milestone 4 — Build the Pygame Foundation
*Week 7*

**Goal:** Create the core structure of the desktop application.

### Tasks

- [ ] Create the Pygame window and main game loop
- [ ] Create a screen/state manager (login, lobby, game screens)
- [ ] Create reusable UI components (buttons, text, input boxes)
- [ ] Create card-drawing/rendering helpers
- [ ] Create the login screen
- [ ] Create the casino lobby
- [ ] Create the player information display (name, chips)

### Checkpoint

> The app launches, and a user can log in and navigate between the login screen and the lobby with the mouse.

---

# Milestone 5 — Build the Game Screens
*Weeks 8–9*

**Goal:** Create the visual interface for each casino game.

### Tasks

- [ ] Create Blackjack screen
- [ ] Create Video Poker screen
- [ ] Create War screen
- [ ] Create betting controls
- [ ] Create game action buttons
- [ ] Display cards and game state
- [ ] Connect game actions to the casino engine
- [ ] Update chips and statistics after each round
- [ ] Handle invalid actions and errors in the UI (e.g., bet exceeds chips)
- [ ] Add basic styling

### Checkpoint

> Blackjack, Video Poker, and War are fully playable with the mouse in the Pygame window.

---

# Milestone 6 — Integration, Polish, and Testing
*Week 10*

**Goal:** Make the desktop application complete, stable, and demo-ready.

### Tasks

- [ ] Create a player statistics screen
- [ ] Make Blackjack fully playable end to end
- [ ] Make Video Poker fully playable end to end
- [ ] Make War fully playable end to end
- [ ] Handle edge cases (out of chips, invalid login, duplicate accounts)
- [ ] Fix bugs and refactor duplicated code
- [ ] Test the complete player lifecycle
- [ ] Write final documentation

### Architecture

```
┌──────────────┐
│  Pygame UI   │
└──────┬───────┘
       ↕
┌──────────────┐
│Casino Engine │
└──────┬───────┘
       ↕
┌──────────────┐
│SQLite Database│
└──────────────┘
```

### Checkpoint

> A user can log in, play games, earn/lose chips, close the app, and have their information persist.

---

# Removed from the Original Plan

The following milestones were dropped because the project is now a desktop app instead of a web app:

- FastAPI backend
- Web UI and connecting the UI to the backend
- Deployment (hosting, HTTPS, domain, production database)
