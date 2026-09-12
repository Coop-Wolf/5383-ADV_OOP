from Classes import *



# Get number of players and chip amount
def get_players():
    while True:
        try:
            num_players = int(input("Number of players: "))

            if num_players > 0:
                break

            print("ERROR: number of players must be greater than 0.")

        except ValueError:
            print("ERROR: number of players must be an integer.")

    players = []

    for i in range(num_players):
        name = input(f"Player {i+1} Name: ")

        while True:
            try:
                money = int(input(f"Money for {name}: "))

                if money >= 0:
                    break

                print("ERROR: money cannot be negative.")

            except ValueError:
                print("ERROR: money must be an integer.")

        players.append(Player(name, chips=money))

    print()
    return players


def ask_to_continue(player):
    
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


peeps = get_players()
game = Game(peeps)


# Main game loop
while game.players:
    print("====================")
    print()
    game.play_round()
    print()
    print("====================")
    print()

    print("\n--- Round Results ---")
    for player in game.players:
        print(player.get_player_info())
    print()

    # Ask each player if they want to continue
    remaining_players = []
    for player in game.players:
        if ask_to_continue(player):
            remaining_players.append(player)
        else:
            print(f"{player.name} started with {player.get_starting_amount()}, and has left the table with {player.chips} chips.")

    game.players = remaining_players

    if not game.players:
        print("\nAll players have left. Game over!")