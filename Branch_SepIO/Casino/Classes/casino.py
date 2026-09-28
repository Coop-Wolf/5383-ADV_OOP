from .player import Player
from .Blackjack.blackjack import Blackjack
from .VideoPoker.videopoker import VideoPoker
from .War.war import War
from .util import Util
import sys
import time


class Casino:

    # Games in the lobby: (menu label, game class, takes a single player?)
    # Add a game here and it shows up in the lobby and welcome screen.
    GAMES = [
        ("Blackjack", Blackjack, False),
        ("Video Poker", VideoPoker, True),
        ("War", War, True),
    ]

    def __init__(self):
        self.players = []
        self.current_game = None

    # ----------------
    # Helper Functions
    # ----------------
    def _name_taken(self, name):
        """Case-insensitive check so two players can't share a name."""
        return any(p.name.lower() == name.lower() for p in self.players)

    def _prompt_name(self, prompt, pending=()):
        """Ask for a non-empty, unique player name made of letters, spaces, hyphens, or apostrophes."""
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
            elif self._name_taken(name) or name.lower() in (n.lower() for n in pending):
                print(f"  ERROR: A player named '{name}' already exists.")
            else:
                return name

    # -----
    # Menus
    # -----
    def lobby_options(self):
        """Every lobby option in menu order as (label, action). Exit's action is None."""

        # cls=cls, single=single binds each game's own values to its lambda
        options = [
            (label, lambda cls=cls, single=single: self.play_game(cls, single))
            for label, cls, single in self.GAMES
        ]

        options += [
            ("Add / Remove Player", self.add_or_remove_player),
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

    def play_game(self, game_class, single_player):
        """Create and run a game. Single-player games ask who is playing."""

        if single_player:
            player = self.get_single_player()

            if player is None:
                return

            self.current_game = game_class(player)

        else:
            self.current_game = game_class(self.players)

        self.current_game.play()

    def add_funds(self):
        Util.banner("ADD FUNDS", 50)

        if not self.players:
            print("  No players available.")
            print()
            print("=" * 50)
            time.sleep(3)
            return

        print("  CURRENT PLAYERS")
        print("  " + "-" * 46)

        for i, player in enumerate(self.players):
            print(
                f"  {i + 1:<4}"
                f"{player.name:<20}"
                f"{player.chips:>10} chips"
            )

        print()
        print("  " + "-" * 46)

        # Select player
        player_number = Util.ask_int(
            "  Select a player's number: ", 1, len(self.players)
        )
        player = self.players[player_number - 1]

        print()
        print(f"  Selected Player: {player.name}")
        print(f"  Current Balance: {player.chips} chips")
        print()

        # Enter amount
        amount = Util.ask_int("  Amount to add: ", 1)

        # Add funds
        player.chips += amount
        player.funds_added += amount

        print()
        print("  " + "-" * 46)
        print("               FUNDS ADDED")
        print("  " + "-" * 46)
        print()
        print(f"  Player:         {player.name}")
        print(f"  Amount Added:   +{amount} chips")
        print(f"  New Balance:    {player.chips} chips")
        print()
        print("=" * 50)
        time.sleep(3)

    def add_or_remove_player(self):
        Util.banner("PLAYER MANAGEMENT", 35)

        print("  1.  Add Player")
        print("  2.  Remove Player")
        print("  3.  Back to Casino Lobby")
        print()
        print("=" * 35)

        option = Util.ask_int("Select an option: ", 1, 3)

        if option == 1:
            name = self._prompt_name("Enter player name: ")
            money = Util.ask_int(f"Enter starting chips for {name}: ", 0)

            self.players.append(Player(name, chips=money))
            print(f"{name} has been added with {money} chips.")
            time.sleep(2)

        elif option == 2:
            if not self.players:
                print("No players to remove.")
                time.sleep(2)
                return

            print("Current Players:")
            for i, player in enumerate(self.players):
                print(f"{i + 1}. {player.name} - {player.chips} chips")

            player_number = Util.ask_int(
                "Enter the number of the player to remove: ",
                1,
                len(self.players),
            )
            removed_player = self.players.pop(player_number - 1)
            print(f"{removed_player.name} has been removed from the game.")
            time.sleep(2)

        elif option == 3:
            return

    # Get number of players and chip amount
    def get_players(self):
        Util.banner("PLAYER SETUP", 40)

        num_players = Util.ask_int("  Number of players: ", 1, 5)
        print()

        new_names = []

        for i in range(num_players):
            print(f"  --- Player {i + 1} ---")

            name = self._prompt_name("  Name: ", pending=new_names)
            money = Util.ask_int("  Starting chips: ", 0)

            new_names.append(name)
            self.players.append(Player(name, chips=money))
            print()

        print("=" * 40)
        print("          PLAYERS READY!")
        print("=" * 40)
        print()

    def get_player_info(self):
        Util.banner("PLAYER STATS", 50)

        for player in self.players:
            print(player.get_player_info())
            print()

        print("=" * 50)
        print()

        Util.ask_int('Enter "1" to return: ', 1, 1)

    def get_single_player(self):
        """Return the chosen Player, or None if the user backs out / can't play."""
        if not self.players:
            print()
            print("  No players available. Add a player first.")
            print()
            time.sleep(3)
            return None

        Util.banner("PLAYERS", 50)

        print("  0.  Back to lobby")

        for number, player in enumerate(self.players, start=1):
            print(f"  {number}.  {player.name:<10} {player.chips:>5} chips")

        print("=" * 50)
        print()

        choice = Util.ask_int("Select a player: ", 0, len(self.players))

        if choice == 0:
            return None

        player = self.players[choice - 1]

        if player.chips <= 0:
            print(f"{player.name} has no chips and cannot play.")
            time.sleep(3)
            return None

        return player


    def welcome(self):
        Util.banner("WELCOME TO COOP'S CASINO", 45)

        print("  Choose your game, place your bets,")
        print("  and see if you can come out ahead.")
        print()
        print("  Available games include:")

        for label, _, _ in self.GAMES:
            print(f"    • {label}")

        print()
        print("  Manage your players, add funds,")
        print("  and keep track of your stats.")
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
            self.get_players()

            while self.players:
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

            if not self.players:
                print("\nNo players left at the table.")

        except (KeyboardInterrupt, EOFError):
            pass

        print("\nLeaving the casino. Goodbye!")