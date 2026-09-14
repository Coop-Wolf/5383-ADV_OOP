from .player import Player
from .blackjack import Blackjack
from .poker import Poker

class Casino:
    def __init__(self):
        self.players = []
        self.current_game = None
        
    def casino_lobby(self):
        print()
        print("CASINO LOBBY")
        print()
        print("1. Blackjack")
        print("2. Poker")
        print("3. Add/Remove Player")
        print("4. Add Funds")
        print("5. Exit")
        print()
    
    def add_funds(self):
        print()
        print("Add Funds")
        print()
        if not self.players:
            print("No players available to add funds.")
            return
        print("Current Players:")
        for i, player in enumerate(self.players):
            print(f"{i + 1}. {player.name} - {player.chips} chips")
        while True:
            try:
                player_index = int(input("Enter the number of the player to add funds to: ")) - 1
                if 0 <= player_index < len(self.players):
                    break
                else:
                    print("ERROR: Invalid player number.")
            except ValueError:
                print("ERROR: Please enter a valid integer.")
        
        while True:
            try:
                amount = int(input(f"Enter amount to add for {self.players[player_index].name}: "))
                if amount >= 0:
                    self.players[player_index].chips += amount
                    print(f"{amount} chips added to {self.players[player_index].name}. New balance: {self.players[player_index].chips} chips.")
                    break
                else:
                    print("ERROR: amount cannot be negative.")
            except ValueError:
                print("ERROR: amount must be an integer.")
        
    def add_or_remove_player(self):
        print()
        print("Add/Remove Player")
        print()
        print("1. Add Player")
        print("2. Remove Player")
        print("3. Back to Casino Lobby")
        print()
        
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
        while True:
            try:
                num_players = int(input("Number of players: "))

                if num_players > 0:
                    break

                print("ERROR: number of players must be greater than 0.")

            except ValueError:
                print("ERROR: number of players must be an integer.")

        for i in range(num_players):
            name = input(f"Player {i + 1} Name: ")

            while True:
                try:
                    money = int(input(f"Money for {name}: "))

                    if money >= 0:
                        break

                    print("ERROR: money cannot be negative.")

                except ValueError:
                    print("ERROR: money must be an integer.")

            self.players.append(Player(name, chips=money))

        print()


    def ask_to_continue(self, player):
        
        # If player has no chips left, they cannot continue
        if player.chips <= 0:
            print(f"{player.name} has no chips left and cannot continue.")
            return False
        
        # Ask player if they want to continue playing
        while True:
            choice = input(f"{player.name}, would you like to keep playing? (y/n): ").strip().lower()

            if choice == "y":
                return True
            elif choice == "n":
                return False

            print("ERROR: please enter 'y' or 'n'.")
            
    # Casino loop
    def start(self):
        self.get_players()

        while self.players:
            self.casino_lobby()

            option = int(input("Select an option: "))

            if option == 1:
                self.current_game = Blackjack(self.players)
                self.current_game.play()
            elif option == 2:
                self.current_game = Poker(self.players)
                self.current_game.play_round()
            elif option == 3:
                self.add_or_remove_player()
            elif option == 4:
                self.add_funds()
            elif option == 5:
                break