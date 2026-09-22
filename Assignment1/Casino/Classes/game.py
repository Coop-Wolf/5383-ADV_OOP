import time

class Game():


    # Sync player information from game
    def sync_players(self, original_players, game_players, game_name):

        earnings_attribute = f"{game_name.lower()}_earnings"

        if isinstance(game_players, list):

            for original_player, game_player in zip(
                original_players,
                game_players
            ):

                original_player.chips = game_player.chips

                current_earnings = getattr(
                    original_player,
                    earnings_attribute
                )

                setattr(
                    original_player,
                    earnings_attribute,
                    current_earnings + game_player.earnings
                )
                
                # Reset players earnings on the game
                game_player.earnings = 0

        else:

            original_players.chips = game_players.chips

            current_earnings = getattr(
                original_players,
                earnings_attribute
            )

            setattr(
                original_players,
                earnings_attribute,
                current_earnings + game_players.earnings
            )
            
            # Reset players earnings on the game
            game_players.earnings = 0
            
                        
            
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