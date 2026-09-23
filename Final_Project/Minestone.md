# 🎰 Casino Project — Development Milestones

## Final Goal

Build a full-stack online casino application with:

- Blackjack
- Poker
- War
- Persistent player accounts and statistics
- Database storage
- FastAPI backend
- Web-based UI
- Multiplayer capability
- Deployment to a server

---

# Milestone 1 — Finish the Casino Engine

**Goal:** Make the current terminal casino stable and complete.

### Tasks

- [ ] Finish Blackjack
- [ ] Finish Poker
- [ ] Finish War
- [ ] Finish player management
- [ ] Finish betting/chip management
- [ ] Finish player statistics
- [ ] Fix known bugs
- [ ] Refactor duplicated/unnecessary code
- [ ] Make sure game rules work correctly
- [ ] Optimize OOP techniques by reusing code

### Checkpoint

> Blackjack, Poker, and War can be played reliably through the terminal.

---

# Milestone 2 — Separate Game Logic from the Terminal

**Goal:** Make the casino engine independent of `input()` and `print()`.

### Tasks

- [ ] Separate game logic from terminal UI
- [ ] Move user input handling into the UI layer
- [ ] Make game classes return game state/results
- [ ] Make game actions callable through methods
- [ ] Keep the terminal UI working as a client of the game engine

### Target Architecture


             ┌── Terminal UI
Game Logic ──┤
             └── Future Web UI


### Checkpoint

> The casino games can run without depending on the terminal


# Milestone 3 — Add the Database

**Goal:** Persist player information so it survives when the application stops.

### Tasks

- [ ] Choose a database
- [ ] Design the database structure
- [ ] Create the player table
- [ ] Store player accounts
- [ ] Store chips
- [ ] Store player statistics
- [ ] Load player information when logging in
- [ ] Save updated information when leaving
- [ ] Decide when additional saves should occur during gameplay

### Checkpoint

> A player can leave the application, restart it, log back in, and still have their information.

---

# Milestone 4 — Build the FastAPI Backend

**Goal:** Turn the casino into a server-side application.

### Tasks

- [ ] Create FastAPI application
- [ ] Create API structure
- [ ] Create player/account endpoints
- [ ] Create login/logout functionality
- [ ] Create game endpoints
- [ ] Connect API to casino engine
- [ ] Connect API to database
- [ ] Return game state through API responses
- [ ] Handle errors and invalid actions

### Checkpoint

> The casino can be played through API requests without using the terminal UI.

---

# Milestone 5 — Build the Web UI

**Goal:** Create the visual interface for the casino.

### Tasks

- [ ] Create basic website layout
- [ ] Create login screen
- [ ] Create casino lobby
- [ ] Create player information display
- [ ] Create Blackjack interface
- [ ] Create Poker interface
- [ ] Create War interface
- [ ] Create betting controls
- [ ] Create game action buttons
- [ ] Display cards and game state
- [ ] Add basic styling

### Checkpoint

> A user can open the casino in a browser and interact with the UI.

---

# Milestone 6 — Connect the UI to the Backend

**Goal:** Make the website fully functional.

### Tasks

- [ ] Connect login UI to API
- [ ] Load player information
- [ ] Connect game actions to API
- [ ] Update UI from API responses
- [ ] Update chips and statistics
- [ ] Handle errors in the UI
- [ ] Make Blackjack fully playable
- [ ] Make Poker fully playable
- [ ] Make War fully playable
- [ ] Test the complete player lifecycle

### Architecture


┌──────────────┐
│    Web UI    │
└──────┬───────┘
       ↕
┌──────────────┐
│   FastAPI    │
└──────┬───────┘
       ↕
┌──────────────┐
│Casino Engine │
└──────┬───────┘
       ↕
┌──────────────┐
│   Database   │
└──────────────┘

### Checkpoint

> A user can log in, play games, earn/lose chips, and have their information persist


# Milestone 7 — Multiplayer & Sessions

**Goal:** Support multiple users using the casino at the same time.

### Tasks

- [ ] Implement user sessions
- [ ] Handle multiple connected users
- [ ] Maintain separate game states
- [ ] Prevent conflicting game participation
- [ ] Support multiple games running simultaneously
- [ ] Determine how multiplayer games will work
- [ ] Ensure player data is isolated between users
- [ ] Test multiple users simultaneously

### Checkpoint

> Multiple users can use the casino simultaneously without interfering with each other's games or player data.

---

# Milestone 8 — Deployment

**Goal:** Run the casino on a real server and make it accessible online.

### Tasks

- [ ] Choose a hosting/server provider
- [ ] Set up production environment
- [ ] Deploy FastAPI backend
- [ ] Deploy web UI
- [ ] Set up production database
- [ ] Configure environment variables
- [ ] Configure HTTPS
- [ ] Configure domain name
- [ ] Set up database backups
- [ ] Add logging/error monitoring
- [ ] Test the production application

### Final Architecture


                 INTERNET
                     │
                     ▼
              ┌─────────────┐
              │   Web UI    │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │   FastAPI   │
              │   Backend   │
              └──────┬──────┘
                     │
             ┌───────┴───────┐
             ▼               ▼
      ┌─────────────┐  ┌──────────────┐
      │Casino Engine│  │   Database   │
      │             │  │              │
      │ Blackjack   │  │ Players      │
      │ Poker       │  │ Chips        │
      │ War         │  │ Statistics   │
      └─────────────┘  │ Game History │
                       └──────────────┘


### Final Checkpoint

> The casino is accessible through a website, users can create/login to accounts, play Blackjack, Poker, and War, their information persists in the database, and multiple users can use the application through the server.