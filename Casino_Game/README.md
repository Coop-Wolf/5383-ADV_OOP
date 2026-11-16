# 🎰 Coop's Casino

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Engine-Pygame-green)
![Database](https://img.shields.io/badge/Database-SQLite-lightgrey?logo=sqlite)
![Networking](https://img.shields.io/badge/Multiplayer-TCP_Sockets-orange)

## 🎲 Project Overview

**Coop's Casino** is a multi-game desktop casino built in Python and Pygame for **CMPS 5383: Advanced Object-Oriented Programming** at Midwestern State University. Built around a modular, screen-based OOP architecture, it blends classic card games, custom multi-reel slots, persistent SQLite profiles, and real-time LAN multiplayer chat.

* **Language & UI:** Python 3.11 & Pygame
* **Storage:** SQLite (local accounts, chip balances, and lifetime stats)
* **Networking:** Multithreaded TCP `socket` server for live chat & win broadcasts
* **Distribution:** Packaged with PyInstaller & Inno Setup

---

## ✨ Features

* **👤 Persistent Accounts:** Sign up or log in to track your chip balance and lifetime stats locally via SQLite.
* **⚙️ Settings Hub:** Top up your bankroll (**Add Funds**), check lifetime performance (**Stats**), or **Logout** from the main menu's Settings screen.
* **🃏 7 Playable Games:** **Blackjack**, **Video Poker**, **War**, and four custom slot machines (**Classic Fruit**, **Wild West**, **Gold Rush**, and **Cows Gone Wild**).
* **💬 Live Multiplayer Chat:** Toggleable bottom-right chat overlay (`[H]` hide/show, `[Enter]` type) over TCP sockets for LAN or hotspot play.
* **📣 Global Win Broadcasts:** Automatic server-wide alerts whenever any player hits a **20x+ win**, triggers **Free Spins**, or enters a **Bonus Round**.

---

## 🎮 Games & How to Play

All games inherit from an abstract `Game` base class handling bets, payouts, and automatic SQLite stat logging.

### ♠️ Card & Table Games

#### 🃏 Blackjack
* **Goal:** Beat the dealer's hand without busting over 21.
* **Actions:** **Hit**, **Stand**, **Double Down** (double bet, take 1 card, stand), or **Split** matching pairs into two independent hands.
* **Payouts:** Natural Blackjack pays **1.5x** (3:2) profit; standard wins pay **1x** (1:1); ties push.

#### 🎥 Video Poker (Jacks or Better)
* **Goal:** Hold your best cards and draw replacements to build a paying 5-card poker hand.
* **Payouts ("X for 1" total return per chip bet):**

| Hand | Return | Hand | Return |
| :--- | :---: | :--- | :---: |
| 👑 Royal Flush | **250x** | 🌊 Flush | **6x** |
| 🔥 Straight Flush | **50x** | 📏 Straight | **4x** |
| 🍀 Four of a Kind | **25x** | 🎲 Three of a Kind | **3x** |
| 🏠 Full House | **9x** | ✌️ Two Pair / Jacks or Better | **2x** / **1x** (Push) |

#### ⚔️ War
* **Goal:** Draw a higher card than the dealer (**Aces high**).
* **Payouts:** High card wins **1x** (1:1) profit; ties push.

---

### 🎰 Slot Machines

All machines run on a shared `Slot` engine with weighted RNG reels and built-in Monte Carlo RTP simulation. Multi-row slots pay horizontally across every row and sum multi-line wins.

| Slot | Grid | Line Payouts (Profit Multipliers) | Bonus Feature |
| :--- | :---: | :--- | :--- |
| **🍒 Classic Fruit** | `3x1` | Two Cherries: **1x** • Cherries: **8x** • Lemons: **12x** • Bars: **20x** • Bells: **40x** • Sevens: **100x** • Diamonds: **500x** | Classic single-line high-volatility payouts |
| **🤠 Wild West** | `3x4` | Horseshoe: **1x** • Boot: **2x** • Hat: **3x** • Revolver: **5x** • Badge: **12x** • Outlaw (Wild): **40x** | **3+ Saloons** trigger **10 Free Spins** at **2x** payouts (retriggerable up to 50 spins). **Outlaw** substitutes for any line symbol. |
| **⛏️ Gold Rush** | `3x4` | Pickaxe: **1x** • Lantern: **2x** • Nugget: **3x** • Dynamite: **6x** • Gold Sack: **20x** | **3+ Mine Carts** open a pick bonus—choose 1 of **6 carts** for **5x, 10x, 20x, 50x, 100x, or 250x**. |
| **🐄 Cows Gone Wild** | `4x3` *(base)* | Milk Carton: **2x** • Barn: **4x** • Tractor: **8x** • Farmer: **15x** • UFO: **50x** | **4+ Golden Jugs** (`1x`–`25x`) trigger **3 Respins**. `+4` jugs expands to **4x4**; `+8` expands to **4x5**. **Boss Cow** multiplies locked jugs by **2x–5x**. Filling all 20 cells wins the **+500x Grand Moo-lah Jackpot**! |

---

## 🌐 Multiplayer Chat Setup

Connect multiple players on the same Wi-Fi or mobile hotspot via **TCP port `5555`**.

1. **Start the Server (Host):** Run `python server.py` (or the server executable). It binds to `0.0.0.0:5555`.
2. **Allow Windows Firewall (Host):** Run in **Administrator PowerShell / CMD** to allow private-network connections:
   ```powershell
   netsh advfirewall firewall add rule name="Coops Casino Chat" dir=in action=allow protocol=TCP localport=5555 profile=private
   ```
   > **Tip:** Remove the rule anytime after your session with:
   > `netsh advfirewall firewall delete rule name="Coops Casino Chat"`
3. **Get Host IP:** Run `ipconfig` (Windows) or `ip addr` (Linux) on the host to grab its local IPv4 address (e.g., `192.168.1.x`).
4. **Connect Clients:** Launch the game on any device on the same network, enter the host IP (or `127.0.0.1` on the host PC), and log in.
   * **`[Enter]`** — Type & send a message
   * **`[H]`** — Hide / show the chat overlay

---

## 🚀 Installation & How to Run

### 🪟 Windows (Recommended)
1. Download **[CasinoApp_Setup.exe](Casino_Game/Casino/Output/CasinoApp_Setup.exe)** from the repository.
2. Run the installer and launch **Coop's Casino** (`CasinoApp.exe`) from your Desktop or Start Menu.

### 🐧 Linux (via Wine)
1. Install Wine and Winetricks:
   ```bash
   sudo apt install wine winetricks
   ```
2. Navigate to the extracted application folder and run:
   ```bash
   cd /path/to/folder
   wine CasinoApp.exe
   ```

### 💻 Run from Source
**Requires:** Python 3.11+ and `pygame`
```bash
git clone https://github.com/Coop-Wolf/5383-ADV_OOP/
cd Casino_Game/Casino
pip install pygame
python main.py
```