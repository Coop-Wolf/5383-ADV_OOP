from .player import Player
from .Blackjack.blackjack import Blackjack
from .VideoPoker.videopoker import VideoPoker
from .War.war import War
from .terminal_ui import TerminalUI
from .Database.database import Database
import sys
import time
 
 
class Casino:
 
    # Games in the lobby: (menu label, game class)
    GAMES = [
        ("Blackjack", Blackjack),
        ("Video Poker", VideoPoker),
        ("War", War),
    ]
 
    def __init__(self):
        self.player = None
        self.current_game = None
        self.db = Database()
        self.ui = TerminalUI()
 
    # ----------------
    # Helper Function
    # ----------------
    def shutdown(self):
        """Close the database. Chips are already saved after every hand."""
        self.db.close()
 
    # -----
    # Menus
    # -----
    def lobby_options(self):
        """Every lobby option in menu order as (label, action). Exit's action is None."""
 
        options = [
            (label, lambda cls=cls: self.play_game(cls))
            for label, cls in self.GAMES
        ]
 
        options += [
            ("Add Funds", self.add_funds),
            ("Player Stats", self.get_player_info),
            ("Exit", None),
        ]
 
        return options
 
    def casino_lobby(self, options):
        self.ui.banner("CASINO LOBBY", 35)
 
        for number, (label, _) in enumerate(options, start=1):
            print(f"  {number}.  {label}")
 
        print()
        print("=" * 35)
 
    def play_game(self, game_class):
 
        if self.player.chips <= 0:
            print(f"\n{self.player.name} has no chips. Add funds to keep playing.")
            time.sleep(3)
            return
 
        self.current_game = game_class(self.player, db=self.db)
        self.current_game.play()
 
    def add_funds(self):
        self.ui.banner("ADD FUNDS", 50)
 
        print(f"  Player:          {self.player.name}")
        print(f"  Current Balance: {self.player.chips} chips")
        print()
 
        amount = self.ui.ask_int("  Amount to add: ", 1)
 
        self.player.chips += amount
        self.player.funds_added += amount
        self.db.save_chips(self.player.id, self.player.chips)
 
        print()
        print("  " + "-" * 46)
        print("               FUNDS ADDED")
        print("  " + "-" * 46)
        print()
        print(f"  Player:         {self.player.name}")
        print(f"  Amount Added:   +{amount} chips")
        print(f"  New Balance:    {self.player.chips} chips")
        print()
        print("=" * 50)
        time.sleep(3)
 
    # Ask for a username, then load that player from the database (or create them)
    def login(self):
        """Returns True once a player is loaded, False if input was interrupted."""
        self.ui.banner("PLAYER LOGIN", 40)
 
        username = self.ui.ask_username("  Username: ")
        if username is None:
            return False
 
        record, is_new = self.db.get_or_create_player(username)
 
        self.player = Player(
            record["username"], chips=record["chips"], player_id=record["id"]
        )
 
        print()
        print("=" * 40)
        if is_new:
            print(f"  Welcome, {self.player.name}!")
            print(f"  You start with {self.player.chips} chips.")
        else:
            print(f"  Welcome back, {self.player.name}!")
            print(f"  You have {self.player.chips} chips.")
        print("=" * 40)
        print()
        time.sleep(2)
        return True
 
    def get_player_info(self):
        self.ui.banner("PLAYER STATS", 50)
 
        print(self.player.get_player_info(self.db.get_stats(self.player.id)))
        print()
 
        print("=" * 50)
        print()
 
        self.ui.ask_int('Enter "1" to return: ', 1, 1)
 
    def welcome(self):
        self.ui.banner("WELCOME TO COOP'S CASINO", 45)
 
        print("  Choose your game, place your bets,")
        print("  and see if you can come out ahead.")
        print()
        print("  Available games include:")
 
        for label, _ in self.GAMES:
            print(f"    • {label}")
 
        print()
        print("  Manage your funds and keep track")
        print("  of your stats along the way.")
        print()
        print("                 WARNING")
        print("-" * 41)
        print("  If you or someone you know has a")
        print("  gambling problem, help is available.")
        print()
        print("  National Problem Gambling Helpline")
        print("             1-800-426-2537")
        print("-" * 41)
        print()
        print("=" * 45)
        print(" 1. Continue")
        print(" 2. Exit")
        print()
 
        choice = self.ui.ask_int(" Select an option: ", 1, 2)
 
        if choice == 2:
            print("\n Exiting casino...")
            sys.exit()
 
    # Casino loop
    def start(self):
        try:
            self.welcome()
            self.ui.clear_screen()
 
            if self.login():
                while True:
                    self.ui.clear_screen()
 
                    options = self.lobby_options()
                    self.casino_lobby(options)
 
                    choice = self.ui.ask_int("Select an option: ", 1, len(options))
                    self.ui.clear_screen()
 
                    _, action = options[choice - 1]
 
                    # Exit
                    if action is None:
                        break
 
                    action()
 
        except (KeyboardInterrupt, EOFError):
            pass
 
        finally:
            self.shutdown()
 
        print("\nLeaving the casino. Goodbye!")