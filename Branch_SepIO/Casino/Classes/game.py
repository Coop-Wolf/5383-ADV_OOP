import textwrap
from abc import ABC, abstractmethod
from .terminal_ui import TerminalUI


class Game(ABC):

    # Subclasses override these
    name = "Game"
    player_class = None
    min_players = 1
    welcome_sections = []

    def __init__(self, players, ui=None):

        # Original casino players
        self.players = players

        # Whatever UI this game talks through. Defaults to the terminal,
        # but a future UI (pygame, web) could be passed in instead.
        self.ui = ui or TerminalUI()

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

        self.ui.show_message(f"\nYou need at least {self.min_players} players to play {self.name}.")
        self.ui.show_message("Returning to main menu...")
        self.ui.pause(3)
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
                self.ui.show_message(f"{player.name} has no chips and cannot play.")
                player.playing = False
                self.ui.pause(3)
                continue

            answer = self.ui.ask_yes_no(
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
            self.ui.show_message(f"    Result: WIN - {detail}")
            self.ui.show_message(f"    Payout: +{profit} chips")

        elif outcome == "loss":
            player.lose(bet)
            self.ui.show_message(f"    Result: LOSS - {detail}")

        else:
            player.push(bet)
            self.ui.show_message(f"    Result: PUSH - {detail}")
            self.ui.show_message(f"    Payout: {bet} chips returned")

        self.ui.show_message(f"    Chips:  {player.chips}")

    def redraw(self, **kwargs):
        self.ui.clear()
        self.show_table(**kwargs)

    def pause(self, seconds=2):
        self.ui.pause(seconds)
        
        # Ask a player for their bet through the UI, then apply it
    def collect_bet(self, player):
        bet = self.ui.ask_bet(player.name, player.chips)

        # Reset first: wager() adds to bet, and last round's bet is still there
        player.bet = 0
        player.wager(bet)

    def welcome(self):

        self.ui.clear()
        self.ui.banner(self.name.upper(), 45)

        self.ui.show_message(f"  Welcome to {self.name}!")
        self.ui.show_message("")

        for title, content in self.welcome_sections:

            self.ui.show_message(f"  {title}:")

            if isinstance(content, str):
                self.ui.show_message(textwrap.fill(
                    content, width=45,
                    initial_indent="    ", subsequent_indent="    "
                ))
            else:
                for item in content:
                    self.ui.show_message(textwrap.fill(
                        item, width=45,
                        initial_indent="    • ", subsequent_indent="      "
                    ))

            self.ui.show_message("")

        self.ui.show_message("=" * 45)
        self.ui.show_message("")

    # Each game must implement these
    @abstractmethod
    def play_round(self): ...

    @abstractmethod
    def show_table(self): ...

    @abstractmethod
    def determine_winner(self): ...