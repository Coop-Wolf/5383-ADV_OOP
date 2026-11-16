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

---

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

---

## Games & How to Play

All games inherit from an abstract `Game` base class that handles bet collection, chip settlement, and automatic SQLite database stat tracking.

### Table & Card Games

#### 1. Blackjack
* **Objective:** Beat the dealer's hand total without exceeding 21.
* **Gameplay:** Place a bet to receive two cards while the dealer receives two cards. Choose from **Hit** (take another card), **Stand** (end your turn), **Double Down** (double your bet, take one card, and stand), or **Split** (split a matching pair into two independent hands, each with a matching bet).
* **Payouts:**
  * **Natural Blackjack:** Pays **1.5x** (3:2) profit unless the dealer also has Blackjack (Push).
  * **Standard Win / Dealer Bust:** Pays **1x** (1:1) profit.
  * **Tie:** Push (bet returned).

#### 2. Video Poker (Jacks or Better)
* **Objective:** Build the highest-ranking five-card poker hand.
* **Gameplay:** Place a bet to receive five cards. Select which cards to **Hold**, then **Draw** to replace the remaining cards from a freshly shuffled deck.
* **Paytable ("X for 1" total return per chip bet):**

| Hand Rank | Payout |
| :--- | :---: |
| Royal Flush | 250x |
| Straight Flush | 50x |
| Four of a Kind | 25x |
| Full House | 9x |
| Flush | 6x |
| Straight | 4x |
| Three of a Kind | 3x |
| Two Pair | 2x |
| Pair (Jacks or Better) | 1x (Push / Bet Returned) |

#### 3. War
* **Objective:** Draw a higher card than the dealer (Aces are high).
* **Gameplay:** Place a bet to deal one card to yourself and one card to the dealer.
* **Payouts:** Higher card wins **1x** (1:1) profit; ties result in a **Push** (bet returned).

### Slot Machines

All slot machines inherit from the shared `Slot` engine, which supports multi-line grid evaluation, weighted RNG reels, and built-in Monte Carlo RTP simulation. Multi-row slots pay horizontally across every row, and wins across multiple rows add together.

#### 1. Classic Fruit (`Fruits`)
* **Layout:** 3 columns $\times$ 1 row (single center payline).
* **Payouts (Profit Multipliers):**
  * **Two Cherries (Left & Center):** 1x
  * **3 Cherries:** 8x | **3 Lemons:** 12x | **3 Bars:** 20x | **3 Bells:** 40x | **3 Sevens:** 100x | **3 Diamonds:** 500x

#### 2. Wild West
* **Layout:** 3 columns $\times$ 4 rows (4 horizontal paylines).
* **Payouts (Profit Multipliers):**
  * **Horseshoe:** 1x | **Boot:** 2x | **Hat:** 3x | **Revolver:** 5x | **Badge:** 12x | **Outlaw (Wild):** 40x
* **Special Features:**
  * **Outlaw (Wild):** Substitutes for any regular payline symbol.
  * **Saloon Free Spins:** Landing **3 or more Saloon symbols** anywhere on the grid awards **10 Free Spins** where all line wins are **doubled (2x)**. Free spins can retrigger up to a maximum of 50 total spins.

#### 3. Gold Rush
* **Layout:** 3 columns $\times$ 4 rows (4 horizontal paylines).
* **Payouts (Profit Multipliers):**
  * **Pickaxe:** 1x | **Lantern:** 2x | **Nugget:** 3x | **Dynamite:** 6x | **Gold Sack:** 20x
* **Special Feature — Mine Cart Pick Bonus:**
  * Landing **3 or more Mine Cart symbols** anywhere on the grid triggers a pick-and-win bonus round. Choose 1 of **6 Mine Carts** to reveal an instant multiplier prize of **5x, 10x, 20x, 50x, 100x, or 250x** your bet.

#### 4. Cows Gone Wild
* **Layout:** 4 columns $\times$ 3 rows base grid (3 horizontal paylines of 4 matching symbols).
* **Payouts (Profit Multipliers):**
  * **Milk Carton:** 2x | **Barn:** 4x | **Tractor:** 8x | **Farmer:** 15x | **UFO:** 50x
* **Special Feature — Barnyard Hold & Respin Bonus:**
  * Landing **4 or more Golden Jugs** triggers the Hold & Respin feature with **3 respins**. Each Golden Jug carries a random multiplier (`1x`, `2x`, `3x`, `5x`, `10x`, or `25x`).
  * Every new Golden Jug or Boss Cow that lands locks in place and resets the respin counter to **3**.
  * **Grid Expansions:** Collecting **+4 new jugs** expands the grid to **4$\times$4**; collecting **+8 total new jugs** expands the grid to **4$\times$5** (20 cells).
  * **Boss Cow Multiplier:** When the Boss Cow lands during respins, it fires bolts that multiply all currently locked Golden Jugs by **2x, 3x, or 5x**.
  * **Grand Moo-lah Jackpot:** Filling all **20 cells** on the expanded 4$\times$5 grid awards an extra **+500x** Grand Jackpot.

---

## Multiplayer Chat Setup (Host & Client)

Coop's Casino includes a built-in TCP chat system (`port 5555`) designed for local network or mobile hotspot sessions. Players on the same local network can chat and receive real-time server broadcasts whenever someone hits a 20x+ big win, triggers free spins, or enters a bonus round.

### 1. Hosting the Chat Server
One machine on the local network acts as the chat host:
1. **Start the Server:** Run the server script (`python server.py` or the packaged server executable). The server binds to `0.0.0.0` on **TCP port `5555`** to accept connections on the local subnet.
2. **Allow Local Traffic Through Windows Firewall (Host Machine):** If hosting on Windows, run the following command in an **Administrator PowerShell** or **Command Prompt** to allow inbound connections on private networks only:
   ```powershell
   netsh advfirewall firewall add rule name="Coops Casino Chat" dir=in action=allow protocol=TCP localport=5555 profile=private
   ```
   *(Optional cleanup after your session: remove the rule anytime with `netsh advfirewall firewall delete rule name="Coops Casino Chat"`.)*
3. **Find the Host IP Address:** Run `ipconfig` (Windows) or `ip addr` (Linux) on the host machine to note its local IPv4 address (for example, `192.168.1.x` or `172.20.10.x` on a mobile hotspot).

### 2. Connecting Clients & In-Game Controls
1. Launch **Coop's Casino** on any device connected to the same local network or hotspot as the host.
2. Enter the host's local IPv4 address when prompted (or use `127.0.0.1` if playing solo on the host machine).
3. Log in to connect to the chat room automatically.
4. **Chat Overlay Hotkeys:**
   * **`[Enter]`**: Focus the chat input box and send a message.
   * **`[H]`**: Hide or show the bottom-right chat overlay.

---

## Installation & How to Run

### Option 1: Windows (Standalone Installer)
1. Download the [Coop's Casino Windows Installer (`CasinoApp_Setup.exe`)](Casino/Output/CasinoApp_Setup.exe).
2. Run `CasinoApp_Setup.exe` and follow the installation wizard to install the application.
3. Launch **Coop's Casino** from your Desktop or Start Menu (`CasinoApp.exe`). The SQLite database initializes automatically on first launch.

### Option 2: Linux (via Wine)
You can run the packaged Windows executable (`CasinoApp.exe`) on Linux using **Wine**:
1. Install Wine and Winetricks via your terminal:
   ```bash
   sudo apt install wine winetricks
   ```
2. Navigate to the folder containing the extracted application files and launch `CasinoApp.exe`:
   ```bash
   cd /path/to/folder
   wine CasinoApp.exe
   ```

### Option 3: Running from Source (Developers)
**Prerequisites:** Python 3.11+ and `pygame`

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone <your-repo-url>
   cd <project-folder>
   ```
2. Install dependencies:
   ```bash
   pip install pygame
   ```
3. Run the application:
   ```bash
   python main.py
   ```