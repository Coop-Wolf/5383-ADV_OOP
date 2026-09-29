# 🎰 Casino

A terminal-based casino application built in Python using object-oriented programming principles. The project provides a central casino lobby where players can manage their funds, view statistics, and play multiple casino games.

## 📋 Overview

This project simulates a small casino environment through a command-line interface. Players can enter the casino, manage their chip balances, choose from available games, and track their performance across different games.

The project was designed with an emphasis on **object-oriented design**, **class organization**, **inheritance**, **encapsulation**, and **reusable game components**.

Currently supported games include:

* ♠️ Blackjack
* ♥️ Poker
* ♦️ War

Additional games can be added to the casino using the existing game structure.

---

## ✨ Features

### Casino Lobby

The casino provides a central lobby where players can:

* Add players
* Remove players
* Add funds to a player's balance
* View player statistics
* Select and play available games
* Exit the casino

### Player Management

Players have their own casino account information, including:

* Player name
* Current chip balance
* Starting balance
* Game-specific winnings/losses
* Total profit/loss
* Current game status

Player balances are maintained by the casino and synchronized after games are completed.

### Player Statistics

The casino tracks player performance across games.

Example:

```text
==================================================
                  PLAYER STATS
==================================================

PLAYER                    CHIPS
--------------------------------------------------
Cooper                     1000 chips
                     Starting Amount:  +1000 chips
                     Blackjack:        -100 chips
                     Poker:              +50 chips
                     War:               +100 chips
                     Total:              +50 chips

==================================================
```

This allows players to see both their current balance and their overall performance.

---

# 🎲 Games

## ♠️ Blackjack

Blackjack is a card game where players attempt to get as close to 21 as possible without going over.

### Features

* Player vs. dealer gameplay
* Hit
* Stand
* Double down
* Split
* Multiple hands
* Blackjack detection
* Bust detection
* Dealer turn
* Push/tie handling
* Blackjack payout
* Chip management

The Blackjack implementation uses specialized classes such as `BlackjackPlayer` and `BlackjackHand` while reusing common casino components such as the deck and cards.

---

## ♥️ Poker

The Poker implementation is a simplified Texas Hold'em-style game.

### Features

* Multiple players
* Community cards
* Betting rounds
* Check
* Call
* Raise
* Fold
* Pot management
* Player elimination when folding
* Winner determination
* Poker hand evaluation

Supported poker hands include:

* High Card
* Pair
* Two Pair
* Three of a Kind
* Straight
* Flush
* Full House
* Four of a Kind

The Poker system also tracks each player's total contribution to the pot.

---

## ♦️ War

War is a simple card game where players compare cards to determine the winner.

### Features

* Player vs. dealer gameplay
* Card comparison
* Winner determination
* Chip payouts
* War handling
* Integration with the casino's player and statistics systems

War provides a simpler game implementation while still using the project's reusable card and player architecture.

---

# 🏗️ Project Structure

The project is organized around reusable object-oriented components.

A simplified structure looks like:

```text
Casino/
│
├── Casino.py
├── Game.py
├── Player.py
├── Person.py
│
├── Blackjack.py
├── BlackjackPlayer.py
│
├── Poker.py
├── PokerPlayer.py
│
├── War.py
├── WarPlayer.py
│
├── Dealer.py
├── Deck.py
├── Card.py
├── Hand.py
├── BlackjackHand.py
├── PokerHand.py
├── Pot.py
│
├── Util.py
│
└── main.py
```

The exact file structure may vary depending on the current implementation.

---

# 🧱 Object-Oriented Design

One of the primary goals of the project is to demonstrate object-oriented programming concepts.

## Inheritance

Games share common functionality through a base `Game` class.

```text
              Game
             /    \
            /      \
     Blackjack     Poker
                      \
                       ...
```

Game-specific classes extend the base functionality when additional behavior is required.

Players also have specialized implementations for different games.

```text
              Player
             /      \
            /        \
 BlackjackPlayer   PokerPlayer
```

This allows common player functionality to be reused while giving individual games access to their own specialized behavior.

## Encapsulation

Game-specific information and behavior are kept inside their respective classes.

For example:

* `Blackjack` manages Blackjack gameplay
* `Poker` manages Poker gameplay
* `PokerHand` evaluates Poker hands
* `Pot` manages the Poker pot
* `Dealer` manages dealer behavior
* `Casino` manages the overall casino and player list

This separation keeps responsibilities organized and makes the project easier to modify.

## Reusable Components

Common card-game functionality is separated into reusable classes.

For example:

```text
Card
 ↓
Deck
 ↓
Hand
```

These components can then be reused by multiple games rather than implementing the same functionality separately for every game.

---

# 👥 Multiplayer

The casino is designed to support multiple players.

Players are managed by the central `Casino` class, allowing the casino to maintain player information independently from individual games.

A game can create or use its own game-specific player collection while preserving the main casino player information.

This separation allows the casino to keep track of:

* Player balances
* Player statistics
* Game participation
* Game-specific information

The multiplayer functionality is being developed alongside the existing game architecture so that multiple players can participate in supported games without losing their persistent casino information.

---

# 💰 Chip System

Players use casino chips to participate in games.

Each player has a current chip balance, and games modify that balance based on the outcome of bets.

The casino also maintains statistics about how a player's balance has changed.

For example:

```text
Starting Amount: 1000
Blackjack:       -100
Poker:           +200
War:              -50
----------------------
Total:            +50

Current Chips:   1050
```

This allows game results to remain connected to the player's overall casino account.

---

# 🖥️ User Interface

The application runs through the terminal and uses formatted text to create a casino-style interface.

The interface includes:

* Menus
* Section headers
* Player tables
* Game prompts
* Game status displays
* Card displays
* Betting information
* Clear-screen transitions

Example:

```text
==================================================
                    CASINO
==================================================

1. Blackjack
2. Poker
3. War
4. Add Player
5. Remove Player
6. Add Funds
7. Player Stats
8. Exit

==================================================
Select an option:
```

---

# 🚀 Getting Started

## Requirements

* Python 3.x
* A terminal or command prompt

No external database is currently required.

## Installation

Clone the repository:

```bash
git clone <repository-url>
```

Navigate into the project:

```bash
cd Casino
```

Run the application:

```bash
python main.py
```

Depending on the project setup, you may need to use:

```bash
python3 main.py
```

---

# 🎮 How to Play

1. Start the application.
2. Add one or more players.
3. Add funds to player accounts if necessary.
4. Select a casino game.
5. Follow the prompts for the selected game.
6. Place bets and play the game.
7. Complete the game.
8. Player balances and statistics are updated.
9. Return to the casino lobby to select another option.

---

# 🧪 Testing

The project can be tested by running the application and checking different gameplay scenarios.

### Blackjack

* Player hits
* Player stands
* Player busts
* Player gets Blackjack
* Dealer busts
* Player/dealer push
* Double down
* Split hands
* Multiple players

### Poker

* Check
* Call
* Raise
* Fold
* Multiple betting rounds
* Different poker hand rankings
* Tie/winner determination
* Pot distribution

### War

* Player wins
* Dealer wins
* Tie/war
* Chip changes
* Multiple players

### Casino

* Adding players
* Removing players
* Adding funds
* Viewing statistics
* Switching between games
* Maintaining player balances

---

# 🔮 Future Improvements

Possible future additions include:

* Additional casino games
* More advanced Poker hand evaluation and tie-breaking
* More sophisticated betting systems
* Improved multiplayer support
* Persistent player accounts
* Database integration
* Web-based user interface
* Player authentication
* Casino leaderboard
* Game history
* Improved animations and visual effects
* More detailed statistics

Potential future games could include:

* Baccarat
* Craps
* Roulette
* Slots
* Higher/Lower
* Three Card Poker

---

# 📚 Technologies

* **Python**
* **Object-Oriented Programming**
* **Command-Line Interface**
* **Inheritance**
* **Encapsulation**
* **Polymorphism**
* **Lists and Collections**
* **Class-based game architecture**

---

# 🎓 Project Goals

This project was created to practice and demonstrate software development concepts through a larger object-oriented application.

The primary goals include:

* Designing reusable classes
* Applying inheritance and polymorphism
* Separating responsibilities between classes
* Managing relationships between objects
* Building reusable game components
* Managing player state
* Creating a functional command-line application
* Expanding an application without significantly rewriting existing functionality

---

# 👤 Author

**Cooper Wolf**

This project was developed as an object-oriented programming project and is intended to demonstrate the design and implementation of a modular casino application in Python.
