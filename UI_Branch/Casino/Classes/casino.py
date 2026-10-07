from .player import Player
from .Blackjack.blackjack import Blackjack
from .VideoPoker.videopoker import VideoPoker
from .War.war import War
from .terminal_ui import TerminalUI
from ..Database.database import Database
import sys
 
 
class Casino:
 
    # Games in the lobby
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
 
    def shutdown(self):
        """Close the database. Chips are already saved after every hand."""
        self.db.close()
 
    # -----
    # Menus
    # -----
    def lobby_options(self):
        """Every lobby option in menu order as (label, action). Exit's action is None."""
 
        options = [(label, lambda cls=cls: self.play_game(cls)) for label, cls in self.GAMES]
 
        options += [
            ("Add Funds", self.add_funds),
            ("Player Stats", self.get_player_info),
            ("Exit", None),
        ]
 
        return options
 
    def casino_lobby(self, options):
        self.ui.banner("CASINO LOBBY", 35)
 
        for number, (label, _) in enumerate(options, start=1):
            self.ui.show_message(f"  {number}.  {label}")
 
        self.ui.show_message()
        self.ui.show_message("=" * 35)
 
    def play_game(self, game_class):
 
        if self.player.chips <= 0:
            self.ui.show_message(f"\n{self.player.name} has no chips. Add funds to keep playing.")
            self.ui.pause(3)
            return
 
        self.current_game = game_class(self.player, db=self.db)
        self.current_game.play()
 
    def add_funds(self):
        self.ui.banner("ADD FUNDS", 50)
 
        self.ui.show_message(f"  Player:          {self.player.name}")
        self.ui.show_message(f"  Current Balance: {self.player.chips} chips")
        self.ui.show_message()
 
        amount = self.ui.ask_int("  Amount to add: ", 1)
 
        self.player.chips += amount
        self.player.funds_added += amount
        self.db.save_chips(self.player.id, self.player.chips)
 
        self.ui.show_message()
        self.ui.show_message("  " + "-" * 46)
        self.ui.show_message("               FUNDS ADDED")
        self.ui.show_message("  " + "-" * 46)
        self.ui.show_message()
        self.ui.show_message(f"  Player:         {self.player.name}")
        self.ui.show_message(f"  Amount Added:   +{amount} chips")
        self.ui.show_message(f"  New Balance:    {self.player.chips} chips")
        self.ui.show_message()
        self.ui.show_message("=" * 50)
        self.ui.ask_continue()
 
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
 
        self.ui.show_message()
        self.ui.show_message("=" * 40)
        if is_new:
            self.ui.show_message(f"  Welcome, {self.player.name}!")
            self.ui.show_message(f"  You start with {self.player.chips} chips.")
        else:
            self.ui.show_message(f"  Welcome back, {self.player.name}!")
            self.ui.show_message(f"  You have {self.player.chips} chips.")
        self.ui.show_message("=" * 40)
        self.ui.show_message()
        self.ui.pause(2)
        return True
 
    def get_player_info(self):
        self.ui.banner("PLAYER STATS", 50)
 
        self.ui.show_message(self.player.get_player_info(self.db.get_stats(self.player.id)))
        self.ui.show_message()
 
        self.ui.show_message("=" * 50)
        self.ui.show_message()
 
        self.ui.ask_continue()
 
    def welcome(self):
        self.ui.banner("WELCOME TO COOP'S CASINO", 45)
 
        self.ui.show_message("  Choose your game, place your bets,")
        self.ui.show_message("  and see if you can come out ahead.")
        self.ui.show_message()
        self.ui.show_message("  Available games include:")
 
        for label, _ in self.GAMES:
            self.ui.show_message(f"    • {label}")
 
        self.ui.show_message()
        self.ui.show_message("  Manage your funds and keep track")
        self.ui.show_message("  of your stats along the way.")
        self.ui.show_message()
        self.ui.show_message("                 WARNING")
        self.ui.show_message("-" * 41)
        self.ui.show_message("  If you or someone you know has a")
        self.ui.show_message("  gambling problem, help is available.")
        self.ui.show_message()
        self.ui.show_message("  National Problem Gambling Helpline")
        self.ui.show_message("             1-800-426-2537")
        self.ui.show_message("-" * 41)
        self.ui.show_message()
        self.ui.show_message("=" * 45)
        self.ui.show_message(" 1. Continue")
        self.ui.show_message(" 2. Exit")
        self.ui.show_message()
 
        choice = self.ui.ask_int(" Select an option: ", 1, 2)
 
        if choice == 2:
            self.ui.show_message("\n Exiting casino...")
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
 
        self.ui.show_message("\nLeaving the casino. Goodbye!")