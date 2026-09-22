import time

class Game():

    # Sync player chip count from game
    def sync_players(self, original_players, game_players):
        
        if isinstance(game_players, list):
            for original_player, game_player in zip(
                original_players,
                game_players
            ):
                
                original_player.chips = game_player.chips
        
        else:
            original_players.chips = game_players.chips
            
                        
            
    def whos_playing(self, players, first_round=False):
        
        if isinstance(players, list):
            for player in players:

                if player.chips <= 0:
                    print(f"{player.name} has no chips and cannot play.")
                    player.playing = False
                    time.sleep(3)
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

            # Check if anyone is still playing
            for player in players:
                if player.playing:
                    return True
                
                
        # If there is only one player (war game)
        else:
            
            player = players
            
            if player.chips <= 0:
                print(f"{player.name} has no chips and cannot play.")
                time.sleep(2)
                return False

            while True:
                try:
                    choice = input(f"{player.name}, do you want to play again? (y/n): ").strip().lower()

                    if choice == "y":
                        player.playing = True
                        return True

                    elif choice == "n":
                        player.playing = False
                        return False

                    else:
                        print("ERROR: please enter 'y' or 'n'.")

                except (EOFError, KeyboardInterrupt):
                    print("\nInput interrupted. Exiting game.")
                    return False

        return False