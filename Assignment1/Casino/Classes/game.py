class Game():

    # Sync player chip count from game
    def sync_players(self, original_players, game_players):
        for original_player, game_player in zip(
            original_players,
            game_players
        ):
            original_player.chips = game_player.chips
            
                        
            
    def whos_playing(self, players, first_round=False):
        for player in players:

            if player.chips <= 0:
                print(f"{player.name} has no chips and cannot play.")
                player.playing = False
                continue

            while True:
                try:
                    if first_round:
                        choice = input(
                            f"{player.name}, do you want to play? (y/n): "
                        ).strip().lower()
                    else:
                        choice = input(
                            f"{player.name}, do you want to play again? (y/n): "
                        ).strip().lower()

                    if choice == "y":
                        player.playing = True
                        break

                    elif choice == "n":
                        player.playing = False
                        break

                    else:
                        print("ERROR: please enter 'y' or 'n'.")

                except (EOFError, KeyboardInterrupt):
                    print("\nInput interrupted. Exiting game.")
                    return False

        return True