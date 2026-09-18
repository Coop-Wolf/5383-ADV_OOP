from .player import Player
from .Blackjack.blackjack import Blackjack
from .Poker.poker import Poker
from .util import Util
import time


class Casino:
    def __init__(self):
        self.players = []
        self.current_game = None
        
    def casino_lobby(self):
        print()
        print("=" * 35)
        print("          CASINO LOBBY")
        print("=" * 35)
        print()
        print("  1.  Blackjack")
        print("  2.  Poker")
        print("  3.  Add / Remove Player")
        print("  4.  Add Funds")
        print("  5.  Player Stats")
        print("  6.  Exit")
        print()
        print("=" * 35)
    
    
    def add_funds(self):
        print()
        print("=" * 50)
        print("                    ADD FUNDS")
        print("=" * 50)
        print()

        if not self.players:
            print("  No players available.")
            print()
            print("=" * 50)
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
        while True:
            try:
                player_index = int(
                    input("  Select a player's number: ")
                ) - 1

                if 0 <= player_index < len(self.players):
                    break

                print("  ERROR: Invalid player number.")

            except ValueError:
                print("  ERROR: Please enter a valid number.")

        player = self.players[player_index]

        print()
        print(f"  Selected Player: {player.name}")
        print(f"  Current Balance: {player.chips} chips")
        print()

        # Enter amount
        while True:
            try:
                amount = int(
                    input("  Amount to add: ")
                )

                if amount > 0:
                    break

                print("  ERROR: Amount must be greater than 0.")

            except ValueError:
                print("  ERROR: Please enter a valid amount.")

        # Add funds
        player.chips += amount

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
        
    def add_or_remove_player(self):
        print()
        print("=" * 35)
        print("       PLAYER MANAGEMENT")
        print("=" * 35)
        print()
        print("  1.  Add Player")
        print("  2.  Remove Player")
        print("  3.  Back to Casino Lobby")
        print()
        print("=" * 35)
        
        option = int(input("Select an option: "))
        if option == 1:
            name = input("Enter player name: ")
            while True:
                try:
                    money = int(input(f"Enter starting chips for {name}: "))
                    if money >= 0:
                        break
                    print("ERROR: money cannot be negative.")
                except ValueError:
                    print("ERROR: money must be an integer.")
            new_player = Player(name, chips=money)
            self.players.append(new_player)
            print(f"{name} has been added with {money} chips.")
            
        elif option == 2:
            if not self.players:
                print("No players to remove.")
                return
            print("Current Players:")
            for i, player in enumerate(self.players):
                print(f"{i + 1}. {player.name} - {player.chips} chips")
            while True:
                try:
                    player_index = int(input("Enter the number of the player to remove: ")) - 1
                    if 0 <= player_index < len(self.players):
                        removed_player = self.players.pop(player_index)
                        print(f"{removed_player.name} has been removed from the game.")
                        break
                    else:
                        print("ERROR: Invalid player number.")
                except ValueError:
                    print("ERROR: Please enter a valid integer.")
                    
        elif option == 3:
            return

    # Get number of players and chip amount
    def get_players(self):
        print()
        print("=" * 40)
        print("            PLAYER SETUP")
        print("=" * 40)
        print()

        while True:
            try:
                num_players = int(input("  Number of players: "))

                if num_players > 0:
                    break

                print()
                print("  ERROR: Number of players must be greater than 0.")
                print()

            except ValueError:
                print()
                print("  ERROR: Number of players must be an integer.")
                print()

        print()

        for i in range(num_players):
            print(f"  --- Player {i + 1} ---")

            name = input("  Name: ")

            while True:
                try:
                    money = int(input(f"  Starting chips: "))

                    if money >= 0:
                        break

                    print("  ERROR: Chips cannot be negative.")

                except ValueError:
                    print("  ERROR: Chips must be an integer.")

            self.players.append(Player(name, chips=money))
            print()

        print("=" * 40)
        print("          PLAYERS READY!")
        print("=" * 40)
        print()

    def get_player_info(self):
        print()
        print("=" * 35)
        print("          PLAYER STATS")
        print("=" * 35)
        print()
        print(f"{'PLAYER':<20} {'CHIPS':>10}")
        print("-" * 35)

        for player in self.players:
            print(player.get_player_info())

        print()
        print("=" * 35)
        print()
        print()
        
        while True:
            choice = input("Enter \"1\" to return: ").strip()
            
            if choice == "1":
                break
            else: print(" Invalid selection. Please choose 1 to return.")
        
            

    def welcome(self):
        print()
        print("=" * 45)
        print("          WELCOME TO COOP'S CASINO")
        print("=" * 45)
        print()
        print("  Choose your game, place your bets,")
        print("  and see if you can come out ahead.")
        print()
        print("  Available games include:")
        print("    • Blackjack")
        print("    • Poker")
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
        
        while True:
            choice = input(" Select an option: ").strip()
            
            if choice == "1":
                break
            elif choice == "2":
                print("\n Exiting casino...")
                exit()
            else: print(" Invalid selection. Please choose 1 or 2.")

            
    # Casino loop
    def start(self):
        self.welcome()
        Util.clear_screen()
        self.get_players()

        while self.players:
            Util.clear_screen()
            self.casino_lobby()

            option = int(input("Select an option: "))

            if option == 1:
                Util.clear_screen()
                self.current_game = Blackjack(self.players)
                self.current_game.play()
            elif option == 2 and len(self.players) > 1:
                Util.clear_screen()
                self.current_game = Poker(self.players)
                self.current_game.play()
            elif option == 2 and len(self.players) <= 1:
                print()
                print("Must have 2 or more players to play poker.")
                time.sleep(3)
            elif option == 3:
                Util.clear_screen()
                self.add_or_remove_player()
            elif option == 4:
                Util.clear_screen()
                self.add_funds()
            elif option == 5:
                Util.clear_screen()
                self.get_player_info()
            elif option == 6:
                break