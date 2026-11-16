# Coop's Casino

## Project Overview

**Coop's Casino** is a multi-game desktop casino application built in Python and Pygame for **CMPS 5383: Advanced Object-Oriented Programming** at Midwestern State University. Designed around a modular, screen-based object-oriented architecture, the application combines classic casino card games, custom multi-reel slot machines, persistent player profiles, and real-time local network multiplayer chat.

Players can create an account, manage their chip balance, track lifetime statistics, and play across seven distinct games—including **Blackjack**, **Video Poker**, **War**, and four custom slot machines (**Fruits**, **Wild West**, **Gold Rush**, and **Cows Gone Wild**). For local multiplayer sessions, a built-in TCP socket chat system connects players on the same network and broadcasts live announcements whenever someone hits a big win or triggers a bonus round.

### Tech Stack
* **Language:** Python 3.11
* **GUI & Rendering:** Pygame
* **Database:** SQLite (local storage for user accounts, chip balances, and game statistics)
* **Networking:** Python `socket` and `threading` (TCP client-server architecture for live chat and win broadcasts)
* **Packaging & Distribution:** PyInstaller & Inno Setup (Windows desktop installer)



## Features

* **Persistent Player Accounts & Profiles:** Create an account or log in to save chip balances and lifetime gameplay statistics locally via SQLite.
* **Centralized Settings Menu:** Manage account options—including adding chips (**Add Funds**), viewing lifetime performance (**Stats**), and logging out—from a dedicated Settings screen accessible from the main menu.
* **Seven Playable Casino Games:**
  * **Card & Table Games:** Classic **Blackjack**, **Video Poker**, and **War** with custom betting controls and payout logic.
  * **Four Custom Slot Machines:** **Fruits**, **Wild West**, **Gold Rush**, and **Cows Gone Wild**, featuring unique reel layouts, free-spin retriggers, pick-style bonus rounds, hold-and-spin mechanics, grid expansions, and win multipliers.
* **Real-Time Local Multiplayer Chat:** A non-intrusive, toggleable bottom-right chat overlay (`[H]` to hide/show, `[Enter]` to type) powered by a multithreaded TCP server so players on the same local network or mobile hotspot can message each other while playing.
* **Global Win & Bonus Broadcasts:** Automatic server-wide chat announcements whenever any connected player hits a 20x+ big win, triggers free spins, or enters a bonus game across any of the seven games.
* **Object-Oriented Screen Architecture:** Built on a modular `Screen` base class and reusable UI widgets (`Button`, `ChatOverlay`) for clean state transitions and responsive Pygame rendering.
* **Standalone Windows Distribution:** Packaged with PyInstaller and Inno Setup into a Windows desktop installer with automatic user-writable database initialization.



for linux systems. wine needs to be installed.

sudo apt install wine winetricks

cd /path/to/folder
wine CasinoApp.exe