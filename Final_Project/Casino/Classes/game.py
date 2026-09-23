from multiprocessing import util
import time
from .util import Util

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

        verb = "play" if first_round else "play again"

        if isinstance(players, list):
            for player in players:

                if player.chips <= 0:
                    print(f"{player.name} has no chips and cannot play.")
                    player.playing = False
                    time.sleep(3)
                    continue

                answer = Util.ask_yes_no(
                    f"{player.name}, do you want to {verb}? (y/n): "
                )

                # Input was interrupted
                if answer is None:
                    return False

                player.playing = answer

            # Check if anyone is still playing
            return any(player.playing for player in players)

        # If there is only one player (war game)
        player = players

        if player.chips <= 0:
            print(f"{player.name} has no chips and cannot play.")
            time.sleep(2)
            return False

        answer = Util.ask_yes_no(
            f"{player.name}, do you want to {verb}? (y/n): "
        )

        # Input was interrupted
        if answer is None:
            return False

        player.playing = answer
        return answer