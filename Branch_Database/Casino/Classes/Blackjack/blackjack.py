from .blackjackplayer import BlackjackPlayer
from .blackjackdealer import BlackjackDealer
from ..deck import Deck
from ..game import Game


class Blackjack(Game):

    name = "Blackjack"
    player_class = BlackjackPlayer

    welcome_sections = [
        ("Goal", "Get as close to 21 as possible without going over."),
        ("How to Play", [
            "You and the dealer are dealt two cards.",
            "Hit - Take another card.",
            "Stand - Keep your current hand.",
            "Double Down - Double your bet and receive exactly one more card.",
            "Split - Split a pair into two hands.",
            "The dealer must hit until reaching 17.",
            "Go over 21 and you bust!",
        ]),
        ("Blackjack", "An Ace + a 10-value card on your first two cards is a Blackjack."),
    ]

    def __init__(self, player, ui=None):
        super().__init__(player, ui=ui)
        self.blackjack_player = self.game_player
        self.dealer = BlackjackDealer()

    # Play one round
    def play_round(self):

        self.deck = Deck()

        self.blackjack_player.reset_hands()

        self.ui.clear()
        self.collect_bet(self.blackjack_player)

        # Store the initial bet on the first hand
        self.blackjack_player.hand.bet = self.blackjack_player.bet

        self.dealer.reset_hand()

        # Deal initial cards
        self.ui.clear()
        self.deal_initial_cards()

        # Show completed initial deal
        self.redraw()

        # Player turn
        self.take_player_turn()

        # Dealer turn
        self.take_dealer_turn()

        # Show final table
        self.redraw(reveal_dealer=True)

        # Determine winner
        self.determine_winner()

    def deal_initial_cards(self):

        # Deal 2 cards to the player and the dealer
        for _ in range(2):
            self.blackjack_player.hit(self.deck)
            self.dealer.hit(self.deck)

    def ask_player_action(self):
        return self.ui.ask_action(
            self.blackjack_player.name,
            self.blackjack_player.hand,
            self.blackjack_player.get_hand_value(),
            self.blackjack_player.chips,
            self.blackjack_player.hand.bet,
            self.blackjack_player.available_actions()
        )

    def show_table(self, reveal_dealer=False):

        self.ui.show_message("")
        self.ui.show_message("=" * 80)
        self.ui.show_message("                                     BLACKJACK")
        self.ui.show_message("=" * 80)
        self.ui.show_message("")

        self.ui.show_message("  YOUR HAND" if len(self.blackjack_player.hands) == 1 else "  YOUR HANDS")
        self.ui.show_message("  " + "-" * 70)

        # Show every hand the player has
        for index, hand in enumerate(self.blackjack_player.hands):

            value = hand.get_value()

            if value > 21:
                status = "(Busted)"
            elif hand.is_blackjack():
                status = "(Blackjack)"
            elif hand.stood:
                status = "(Stand)"
            else:
                status = ""

            hand_name = self.blackjack_player.hand_label(index)

            self.ui.show_message(
                f"  {hand_name:<20}"
                f"{str(hand):<33}"
                f"Value: {value:<3} "
                f"Bet: {hand.bet:<3} "
                f"{status}"
            )

        # Dealer section
        self.ui.show_message("")
        self.ui.show_message("  DEALER")
        self.ui.show_message("  " + "-" * 70)

        if reveal_dealer:

            self.ui.show_message(
                f"  {str(self.dealer.hand):<53}"
                f"Value: {self.dealer.get_hand_value()}"
            )

        else:

            self.ui.show_message(
                f"  {str(self.dealer.get_visible_hand()):<53}"
            )

        self.ui.show_message("")
        self.ui.show_message("=" * 80)

    def take_player_turn(self):

        hand_index = 0

        while hand_index < len(self.blackjack_player.hands):

            self.blackjack_player.set_active_hand(hand_index)
            hand = self.blackjack_player.hand

            # Skip hands that are already finished
            if hand.stood:
                hand_index += 1
                continue

            # Automatically finish busted hands and any 21
            if hand.is_bust() or hand.get_value() == 21:
                hand.stood = True
                hand_index += 1
                continue

            action = self.ask_player_action()

            # HIT
            if action == "hit":

                self.blackjack_player.hit(self.deck)

                self.redraw()

                # Only move to the next hand if busted
                if hand.is_bust():
                    hand.stood = True
                    hand_index += 1

            # STAND
            elif action == "stand":

                hand.stood = True

                self.redraw()

                hand_index += 1

            # DOUBLE DOWN
            elif action == "double":

                self.blackjack_player.double_down(self.deck)

                self.redraw()

                hand_index += 1

            # SPLIT
            elif action == "split":

                self.blackjack_player.split(self.deck)

                self.redraw()

                # Stay on the current hand

    def take_dealer_turn(self):

        # Reveal dealer's hand
        self.redraw(reveal_dealer=True)
        self.pause()

        while True:

            action = self.dealer.decide_action()

            if action == "hit":

                card = self.dealer.hit(self.deck)

                # Show what dealer drew
                self.redraw(reveal_dealer=True)

                self.ui.show_message(f"\n  Dealer draws {card}.")

                self.pause()

            else:

                self.redraw(reveal_dealer=True)

                self.ui.show_message(
                    f"\n  Dealer stands at "
                    f"{self.dealer.get_hand_value()}."
                )

                self.pause()
                break

            if self.dealer.is_bust():

                self.redraw(reveal_dealer=True)

                self.ui.show_message(
                    f"\n  Dealer busts at "
                    f"{self.dealer.get_hand_value()}."
                )

                self.pause()

                break

    def determine_winner(self):

        dealer_value = self.dealer.get_hand_value()
        dealer_busted = self.dealer.is_bust()
        dealer_blackjack = self.dealer.hand.is_blackjack()

        self.ui.show_message("")
        self.ui.show_message("=" * 50)
        self.ui.show_message("                 ROUND RESULTS")
        self.ui.show_message("=" * 50)
        self.ui.show_message("")

        # Evaluate every hand
        for index, hand in enumerate(self.blackjack_player.hands):

            player_value = hand.get_value()
            bet = hand.bet
            hand_name = self.blackjack_player.hand_label(index)

            self.ui.show_message(f"  {hand_name}")
            self.ui.show_message(f"    Hand:   {hand}")
            self.ui.show_message(f"    Value:  {player_value}")
            self.ui.show_message(f"    Bet:    {bet} chips")

            if hand.is_bust():
                self.settle(self.blackjack_player, bet, "loss", "Busted")

            elif hand.is_blackjack() and dealer_blackjack:
                self.settle(self.blackjack_player, bet, "push", "Both have blackjack")

            elif hand.is_blackjack():
                self.settle(self.blackjack_player, bet, "win", "Blackjack!", multiplier=1.5)

            elif dealer_blackjack:
                self.settle(self.blackjack_player, bet, "loss", "Dealer has blackjack")

            elif dealer_busted:
                self.settle(self.blackjack_player, bet, "win", "Dealer busted")

            elif player_value > dealer_value:
                self.settle(self.blackjack_player, bet, "win", f"{player_value} beats {dealer_value}")

            elif player_value < dealer_value:
                self.settle(self.blackjack_player, bet, "loss", f"{dealer_value} beats {player_value}")

            else:
                self.settle(self.blackjack_player, bet, "push", f"Tie at {player_value}")

            self.ui.show_message("  " + "-" * 46)

        self.ui.show_message("=" * 50)