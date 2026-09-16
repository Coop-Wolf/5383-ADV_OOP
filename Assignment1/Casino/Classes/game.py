class Game():

    # Sync player chip count from game
    def sync_players(self, original_players, game_players):
        for original_player, game_player in zip(
            original_players,
            game_players
        ):
            original_player.chips = game_player.chips
            
            
    def play_again(self, players):

        for player in players:

            # If player has no chips left, they cannot play again
            if player.chips <= 0:
                print(f"{player.name} has no chips left and cannot continue.")
                return False

        # Ask player if they want to play another round
        while True:
            try:
                choice = input(
                    f"{player.name}, would you like to keep playing? (y/n): "
                ).strip().lower()
                if choice == "y":
                    return True
                elif choice == "n":
                    return False

                print("ERROR: please enter 'y' or 'n'.")
            except (EOFError, KeyboardInterrupt):
                print("\nInput interrupted. Exiting game.")
                return False