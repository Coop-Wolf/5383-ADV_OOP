# 🎰 Casino Game

A Python-based casino game project built using **Object-Oriented Programming (OOP)** principles. The project currently features **Blackjack**, with plans to expand the casino with additional games such as Poker.

## 🎮 Features

### Blackjack

- Multiple players
- Player names and starting chip amounts
- Betting system
- Player hit/stand decisions
- Dealer logic
- Automatic Ace value adjustment
- Blackjack detection
- Blackjack payout of **3:2**
- Standard win/loss/push outcomes
- Player balance tracking
- Input validation
- Option to continue playing

### OOP Design

The project is structured around several classes that represent different parts of the casino:

- `Card` — Represents an individual playing card.
- `Deck` — Creates, stores, shuffles, and deals cards.
- `Hand` — Represents a collection of cards and calculates hand values.
- `Person` — Base class for people participating in games.
- `Player` — Represents a player and manages their chips.
- `Dealer` — Represents the casino dealer.
- `Blackjack` — Controls the Blackjack game logic.

The project uses **inheritance, composition, encapsulation, and class relationships** to demonstrate core OOP concepts.

## 📁 Project Structure

```text
Casino/
│
├── main.py
│
├── casino/
│   ├── __init__.py
│   ├── card.py
│   ├── deck.py
│   ├── hand.py
│   ├── person.py
│   ├── player.py
│   ├── dealer.py
│   └── blackjack.py
│
└── README.md


## ▶️ Running the Game

Navigate to the BlackJack Folder and run:

```bash
python main.py
```


## 🛡️ Input Validation

The game validates user input to prevent invalid values from crashing the program.

Examples include:

- Number of players must be greater than zero.
- Player chip amounts must be valid integers.
- Yes/no prompts only accept valid responses.
- Invalid input prompts the user to try again.

## 🧠 OOP Concepts Demonstrated

This project is designed to demonstrate several fundamental Object-Oriented Programming concepts.

### Encapsulation

Each class manages its own data and behavior.

### Inheritance

Classes such as `Player` and `Dealer` can inherit common functionality from the `Person` class.

### Composition

Objects are built from other objects. For example:

```text
Deck
 └── Cards

Hand
 └── Cards

Player
 └── Hand


 ### Abstraction

Game-specific logic is separated into classes so that `main.py` primarily handles running the program rather than implementing every detail of the game.

## 🚧 Future Plans

Planned additions include:

* Poker
* Casino menu
* Betting improvements
* Blackjack split
* Blackjack double down
* Dealer blackjack betting
* Additional casino games
* Improved terminal UI
* Game statistics

## 📚 Purpose

This project was created as an **Object-Oriented Programming course project** to apply Python OOP concepts to a practical application while building a playable casino game.
