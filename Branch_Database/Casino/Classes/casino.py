from .player import Player
from .Blackjack.blackjack import Blackjack
from .VideoPoker.videopoker import VideoPoker
from .War.war import War
from .util import Util
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

    # ----------------
    # Helper Function
    # ----------------
    def _prompt_name(self, prompt):
        """Ask for a non-empty name made of letters, spaces, hyphens, or apostrophes."""
        while True:
            name = input(prompt).strip()

            if not name:
                print("  ERROR: Name cannot be empty.")
            elif not any(ch.isalpha() for ch in name):
                print("  ERROR: Name must contain at least one letter.")
            elif not all(ch.isalpha() or ch in " -'" for ch in name):
                print("  ERROR: Names can only contain letters, spaces, hyphens, and apostrophes.")
            elif len(name) > 20:
                print("  ERROR: Name must be 20 characters or fewer.")
            else:
                return name

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
        Util.banner("CASINO LOBBY", 35)

        for number, (label, _) in enumerate(options, start=1):
            print(f"  {number}.  {label}")

        print()
        print("=" * 35)

    def play_game(self, game_class):

        if self.player.chips <= 0:
            print(f"\n{self.player.name} has no chips. Add funds to keep playing.")
            time.sleep(3)
            return

        self.current_game = game_class(self.player)
        self.current_game.play()

    def add_funds(self):
        Util.banner("ADD FUNDS", 50)

        print(f"  Player:          {self.player.name}")
        print(f"  Current Balance: {self.player.chips} chips")
        print()

        amount = Util.ask_int("  Amount to add: ", 1)

        self.player.chips += amount
        self.player.funds_added += amount

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

    # Get the player's name and starting chip amount
    def create_player(self):
        Util.banner("PLAYER SETUP", 40)

        name = self._prompt_name("  Name: ")
        money = Util.ask_int("  Starting chips: ", 0)

        self.player = Player(name, chips=money)

        print()
        print("=" * 40)
        print("          PLAYER READY!")
        print("=" * 40)
        print()

    def get_player_info(self):
        Util.banner("PLAYER STATS", 50)

        print(self.player.get_player_info())
        print()

        print("=" * 50)
        print()

        Util.ask_int('Enter "1" to return: ', 1, 1)

    def welcome(self):
        Util.banner("WELCOME TO COOP'S CASINO", 45)

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

        choice = Util.ask_int(" Select an option: ", 1, 2)

        if choice == 2:
            print("\n Exiting casino...")
            sys.exit()

    # Casino loop
    def start(self):
        try:
            self.welcome()
            Util.clear_screen()
            self.create_player()

            while True:
                Util.clear_screen()

                options = self.lobby_options()
                self.casino_lobby(options)

                choice = Util.ask_int("Select an option: ", 1, len(options))
                Util.clear_screen()

                _, action = options[choice - 1]

                # Exit
                if action is None:
                    break

                action()

        except (KeyboardInterrupt, EOFError):
            pass

        print("\nLeaving the casino. Goodbye!")