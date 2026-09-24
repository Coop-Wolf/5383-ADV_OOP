import time
from abc import ABC, abstractmethod
from .util import Util
import textwrap

class Game(ABC):

    # Subclasses override these
    name = "Game"
    player_class = None
    min_players = 1
    welcome_sections = []

    def __init__(self, players):

        # Original casino players
        self.players = players

        # Game-specific players, in the same order
        self.game_players = [
            self.player_class(player.name, player.chips)
            for player in players
        ]

    # Main game loop, the same flow for every game
    def play(self):

        self.welcome()

        if self.whos_playing(first_round=True):

            while self.enough_players():

                self.play_round()

                if not self.whos_playing():
                    break

        self.sync_players()

    # Players who chose to play this round
    def playing_players(self):
        return [player for player in self.game_players if player.playing]

    def enough_players(self):

        if len(self.playing_players()) >= self.min_players:
            return True

        print(f"\nYou need at least {self.min_players} players to play {self.name}.")
        print("Returning to main menu...")
        time.sleep(3)
        return False

    # Sync chips and earnings back to the original casino players
    def sync_players(self):

        earnings_attribute = f"{self.name.lower()}_earnings"

        for original_player, game_player in zip(self.players, self.game_players):

            original_player.chips = game_player.chips

            current_earnings = getattr(original_player, earnings_attribute)
            setattr(
                original_player,
                earnings_attribute,
                current_earnings + game_player.earnings
            )

            # Reset the game player's earnings
            game_player.earnings = 0

    def whos_playing(self, first_round=False):

        verb = "play" if first_round else "play again"

        for player in self.game_players:

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

        return any(player.playing for player in self.game_players)

    # Print a hand's result and update the player's chips and earnings
    def settle(self, player, bet, outcome, detail, multiplier=1):

        if outcome == "win":
            profit = player.win(bet, multiplier)
            print(f"    Result: WIN - {detail}")
            print(f"    Payout: +{profit} chips")

        elif outcome == "loss":
            player.lose(bet)
            print(f"    Result: LOSS - {detail}")

        else:
            player.push(bet)
            print(f"    Result: PUSH - {detail}")
            print(f"    Payout: {bet} chips returned")

        print(f"    Chips:  {player.chips}")
        
        
    def redraw(self, **kwargs):
        Util.clear_screen()
        self.show_table(**kwargs)

    def pause(self, seconds=2):
        time.sleep(seconds)

    def welcome(self):

        Util.clear_screen()
        Util.banner(self.name.upper(), 45)

        print(f"  Welcome to {self.name}!")
        print()

        for title, content in self.welcome_sections:

            print(f"  {title}:")

            if isinstance(content, str):
                print(textwrap.fill(
                    content, width=45,
                    initial_indent="    ", subsequent_indent="    "
                ))
            else:
                for item in content:
                    print(textwrap.fill(
                        item, width=45,
                        initial_indent="    • ", subsequent_indent="      "
                    ))

            print()

        print("=" * 45)
        print()
        

    # Each game must implement these
    @abstractmethod
    def play_round(self): ...

    @abstractmethod
    def show_table(self): ...

    @abstractmethod
    def determine_winner(self): ...