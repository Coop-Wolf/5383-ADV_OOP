from .blackjackplayer import BlackjackPlayer
from .blackjackdealer import BlackjackDealer
from ..deck import Deck
from ..util import Util
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

    def __init__(self, players):
        super().__init__(players)
        self.dealer = BlackjackDealer()

    # Play one round
    def play_round(self):

        self.deck = Deck()

        # Reset hands and place bets
        for blackjack_player in self.game_players:

            # Skip player if they are not playing
            if not blackjack_player.playing:
                continue

            blackjack_player.reset_hands()

            Util.clear_screen()
            blackjack_player.place_bet()

            # Store the initial bet on the first hand
            blackjack_player.hand.bet = blackjack_player.bet

            self.dealer.reset_hand()

        # Deal initial cards
        Util.clear_screen()
        self.deal_initial_cards()

        # Show completed initial deal
        self.redraw()

        # Player turns
        for blackjack_player in self.game_players:

            # Skip player if they are not playing
            if not blackjack_player.playing:
                continue

            self.take_player_turn(blackjack_player)

        # Dealer turn
        self.take_dealer_turn()

        # Show final table
        self.redraw(reveal_dealer=True)

        # Determine winners
        self.determine_winner()

    def deal_initial_cards(self):

        # Deal 2 cards to every player
        for _ in range(2):

            for blackjack_player in self.game_players:

                # Skip player if they are not playing
                if not blackjack_player.playing:
                    continue

                # Deal to every hand
                for hand in blackjack_player.hands:
                    if len(hand.cards) < 2:
                        card = self.deck.deal_card()
                        hand.add_card(card)

                # Only one hand exists during initial deal

            self.dealer.hit(self.deck)

    def show_table(self, reveal_dealer=False):

        print()
        print("=" * 80)
        print("                                     BLACKJACK")
        print("=" * 80)
        print()

        print("  YOUR HANDS")
        print("  " + "-" * 70)

        for blackjack_player in self.game_players:

            # Skip player if they are not playing
            if not blackjack_player.playing:
                continue

            # Show every hand the player has
            for index, hand in enumerate(blackjack_player.hands):

                value = hand.get_value()

                if value > 21:
                    status = "(Busted)"
                elif hand.is_blackjack():
                    status = "(Blackjack)"
                elif hand.stood:
                    status = "(Stand)"
                else:
                    status = ""

                hand_name = blackjack_player.hand_label(index)

                print(
                    f"  {hand_name:<20}"
                    f"{str(hand):<33}"
                    f"Value: {value:<3} "
                    f"Bet: {hand.bet:<3} "
                    f"{status}"
                )

        # Dealer section
        print()
        print("  DEALER")
        print("  " + "-" * 70)

        if reveal_dealer:

            print(
                f"  {str(self.dealer.hand):<53}"
                f"Value: {self.dealer.get_hand_value()}"
            )

        else:

            print(
                f"  {str(self.dealer.get_visible_hand()):<53}"
            )

        print()
        print("=" * 80)

    def take_player_turn(self, blackjack_player):

        hand_index = 0

        while hand_index < len(blackjack_player.hands):

            blackjack_player.set_active_hand(hand_index)
            hand = blackjack_player.hand

            # Skip hands that are already finished
            if hand.stood:
                hand_index += 1
                continue

            # Automatically finish busted hands and any 21
            if hand.is_bust() or hand.get_value() == 21:
                hand.stood = True
                hand_index += 1
                continue

            action = blackjack_player.decide_action(
                dealer_visible_card=self.dealer.hand.cards[0])

            # HIT
            if action == "hit":

                blackjack_player.hit(self.deck)

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

                blackjack_player.double_down(self.deck)

                self.redraw()

                hand_index += 1

            # SPLIT
            elif action == "split":

                blackjack_player.split(self.deck)

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

                print(
                    f"\n  Dealer draws {card}."
                )

                self.pause()

            else:

                self.redraw(reveal_dealer=True)

                print(
                    f"\n  Dealer stands at "
                    f"{self.dealer.get_hand_value()}."
                )

                self.pause()
                break

            if self.dealer.is_bust():

                self.redraw(reveal_dealer=True)

                print(
                    f"\n  Dealer busts at "
                    f"{self.dealer.get_hand_value()}."
                )

                self.pause()

                break

    def determine_winner(self):

        dealer_value = self.dealer.get_hand_value()
        dealer_busted = self.dealer.is_bust()
        dealer_blackjack = self.dealer.hand.is_blackjack()

        print()
        print("=" * 50)
        print("                 ROUND RESULTS")
        print("=" * 50)
        print()

        for blackjack_player in self.game_players:

            # Skip player if they are not playing
            if not blackjack_player.playing:
                continue

            # Evaluate every hand
            for index, hand in enumerate(blackjack_player.hands):

                player_value = hand.get_value()
                bet = hand.bet
                hand_name = blackjack_player.hand_label(index)

                print(f"  {hand_name}")
                print(f"    Hand:   {hand}")
                print(f"    Value:  {player_value}")
                print(f"    Bet:    {bet} chips")

                if hand.is_bust():
                    self.settle(blackjack_player, bet, "loss", "Busted")

                elif hand.is_blackjack() and dealer_blackjack:
                    self.settle(
                        blackjack_player, bet, "push",
                        "Both have blackjack"
                    )

                elif hand.is_blackjack():
                    self.settle(
                        blackjack_player, bet, "win",
                        "Blackjack!", multiplier=1.5
                    )

                elif dealer_blackjack:
                    self.settle(
                        blackjack_player, bet, "loss",
                        "Dealer has blackjack"
                    )

                elif dealer_busted:
                    self.settle(blackjack_player, bet, "win", "Dealer busted")

                elif player_value > dealer_value:
                    self.settle(
                        blackjack_player, bet, "win",
                        f"{player_value} beats {dealer_value}"
                    )

                elif player_value < dealer_value:
                    self.settle(
                        blackjack_player, bet, "loss",
                        f"{dealer_value} beats {player_value}"
                    )

                else:
                    self.settle(
                        blackjack_player, bet, "push",
                        f"Tie at {player_value}"
                    )

                print("  " + "-" * 46)

        print("=" * 50)