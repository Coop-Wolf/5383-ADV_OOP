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










Create Readme for Project



for linux systems. wine needs to be installed.

sudo apt install wine winetricks

cd /path/to/folder
wine CasinoApp.exe