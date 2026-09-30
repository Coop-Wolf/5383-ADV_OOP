import textwrap
from abc import ABC, abstractmethod
from .terminal_ui import TerminalUI


class Game(ABC):

    # Subclasses override these
    name = "Game"
    player_class = None
    welcome_sections = []

    def __init__(self, player, ui=None):

        # Original casino player
        self.player = player

        # Whatever UI this game talks through. Defaults to the terminal,
        # but a future UI pygame will be passed in instead.
        self.ui = ui or TerminalUI()

        # Game-specific player
        self.game_player = self.player_class(player.name, player.chips)

    # Main game loop, the same flow for every game
    def play(self):

        self.welcome()

        while True:

            self.play_round()

            if self.game_player.chips <= 0:
                self.ui.show_message(f"\n{self.game_player.name} is out of chips.")
                self.ui.pause(3)
                break

            answer = self.ui.ask_yes_no(
                f"\n{self.game_player.name}, do you want to play again? (y/n): "
            )

            # "no", or the question was interrupted
            if not answer:
                break

        self.sync_player()

    # Sync chips and earnings back to the original casino player
    def sync_player(self):

        earnings_attribute = f"{self.name.lower()}_earnings"

        self.player.chips = self.game_player.chips

        current_earnings = getattr(self.player, earnings_attribute)
        setattr(
            self.player,
            earnings_attribute,
            current_earnings + self.game_player.earnings
        )

        # Reset the game player's earnings
        self.game_player.earnings = 0

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



    # Each game implements these
    @abstractmethod
    def play_round(self): ...

    @abstractmethod
    def show_table(self): ...

    @abstractmethod
    def determine_winner(self): ...