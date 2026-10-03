# NO LONGER NEED


from ..game import Game
from .wardealer import WarDealer
from .warplayer import WarPlayer
from ..deck import Deck
from ..hand import Hand


class War(Game):

    name = "War"
    player_class = WarPlayer

    welcome_sections = [
        ("Goal", "Draw a higher card than the dealer."),
        ("How to Play", [
            "Place your bet.",
            "You and the dealer each draw one card.",
            "The higher card wins. Aces are high, 2s are low.",
            "A win pays 1 to 1.",
            "If both cards match, your bet is returned.",
        ]),
    ]

    def __init__(self, player, ui=None, db=None):
        super().__init__(player, ui=ui, db=db)

        self.war_dealer = WarDealer()
        self.war_player = self.game_player

    def play_round(self):

        # Create a new shuffled deck
        self.deck = Deck()

        # Create/reset player and dealer hand
        self.war_player.hand = Hand()
        self.war_dealer.reset_hand()

        # Player place bet
        self.ui.clear_screen()
        self.collect_bet(self.war_player)
        self.ui.clear_screen()

        # Deal player card
        self.war_player.hit(self.deck)

        # Show table
        self.show_table()
        self.pause()
        self.ui.clear_screen()

        # Deal dealer card
        self.war_dealer.hit(self.deck)

        # Show table
        self.show_table(reveal_dealer=True)
        self.pause()
        self.ui.clear_screen()

        # Determine winner
        self.determine_winner()

    def determine_winner(self):

        # Get card from player and dealer
        player_card = self.war_player.hand.cards[0]
        dealer_card = self.war_dealer.hand.cards[0]

        # Get card value (Ace is high)
        player_hand_value = player_card.get_poker_value()
        dealer_hand_value = dealer_card.get_poker_value()

        # Get player bet
        bet = self.war_player.bet

        # Show results
        self.ui.show_message("")
        self.ui.show_message("=" * 50)
        self.ui.show_message("                 ROUND RESULTS")
        self.ui.show_message("=" * 50)
        self.ui.show_message("")
        self.ui.show_message(f"  {self.war_player.name}")
        self.ui.show_message(f"    Card:   {player_card}")
        self.ui.show_message(f"    Bet:    {bet} chips")
        self.ui.show_message("")
        self.ui.show_message("  Dealer")
        self.ui.show_message(f"    Card:   {dealer_card}")
        self.ui.show_message("")

        if player_hand_value > dealer_hand_value:
            self.settle(
                self.war_player, bet, "win",
                f"{player_hand_value} beats {dealer_hand_value}"
            )

        elif player_hand_value < dealer_hand_value:
            self.settle(
                self.war_player, bet, "loss",
                f"{dealer_hand_value} beats {player_hand_value}"
            )

        else:
            self.settle(
                self.war_player, bet, "push",
                f"Tie at {player_hand_value}"
            )

        self.ui.show_message("  " + "-" * 46)
        self.ui.show_message("=" * 50)

    def show_table(self, reveal_dealer=False):

        self.ui.show_message("")
        self.ui.show_message("=" * 80)
        self.ui.show_message("                                      WAR")
        self.ui.show_message("=" * 80)
        self.ui.show_message("")

        # Player section
        self.ui.show_message("  YOU")
        self.ui.show_message("  " + "-" * 70)

        player_card = str(self.war_player.hand)

        self.ui.show_message(
            f"  {self.war_player.name:<20}"
            f"{player_card:<20}"
            f"Bet: {self.war_player.bet}"
        )

        # Dealer section
        self.ui.show_message("")
        self.ui.show_message("  DEALER")
        self.ui.show_message("  " + "-" * 70)

        if reveal_dealer:
            dealer_card = str(self.war_dealer.hand)

            self.ui.show_message(
                f"  {'Dealer':<20}"
                f"{dealer_card:<20}")

        else:
            self.ui.show_message(f"  {'Dealer':<20}")

        self.ui.show_message("")
        self.ui.show_message("=" * 80)