from .blackjackplayer import BlackjackPlayer
from .blackjackdealer import BlackjackDealer
from ..deck import Deck
from .blackjackhand import BlackjackHand
from ..util import Util
from ..game import Game
import time


class Blackjack(Game):

    def __init__(self, players):
        # Original Casino players
        self.players = players

        # Blackjack-specific players
        self.blackjack_players = [
            BlackjackPlayer(player.name, player.chips)
            for player in players
        ]

        self.dealer = BlackjackDealer()

    # Main Game loop
    def play(self):

        self.welcome()

        if not self.whos_playing(self.blackjack_players, first_round=True):
            self.sync_players(self.players, self.blackjack_players)
            return

        while True:
            self.play_round()

            if not self.whos_playing(self.blackjack_players, first_round=False):
                self.sync_players(self.players, self.blackjack_players)
                return

    # Play one round
    def play_round(self):

        self.deck = Deck()
        self.deck.shuffle()

        # Reset hands and place bets
        for blackjack_player in self.blackjack_players:
            
            # Skip player if they are not playing
            if not blackjack_player.playing:
                continue

            blackjack_player.reset_hands()

            Util.clear_screen()
            blackjack_player.place_bet()

            # Store the initial bet for the first hand
            blackjack_player.hand_bets[0] = blackjack_player.bet

        self.dealer.hand = BlackjackHand()

        # Deal initial cards
        Util.clear_screen()
        self.deal_initial_cards()

        # Show completed initial deal
        Util.clear_screen()
        self.show_table()

        # Player turns
        for blackjack_player in self.blackjack_players:
            
            # Skip player if they are not playing
            if not blackjack_player.playing:
                continue
            
            self.take_player_turn(blackjack_player)

        # Dealer turn
        self.take_dealer_turn()

        # Show final table
        Util.clear_screen()
        self.show_table(reveal_dealer=True)

        # Determine winners
        self.determine_winner()

    def deal_initial_cards(self):

        # Deal 2 cards to every player
        for _ in range(2):

            for blackjack_player in self.blackjack_players:
            
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

        for blackjack_player in self.blackjack_players:
            
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
                elif blackjack_player.hand_stood[index]:
                    status = "(Stand)"
                else:
                    status = ""

                # Label first hand normally
                if len(blackjack_player.hands) == 1:
                    hand_name = blackjack_player.name

                else:
                    hand_name = (
                        f"{blackjack_player.name} "
                        f"Hand {index + 1}"
                    )

                bet = blackjack_player.hand_bets[index]

                print(
                    f"  {hand_name:<20}"
                    f"{str(hand):<33}"
                    f"Value: {value:<3} "
                    f"Bet: {bet:<3} "
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

            # Skip hands that are already finished
            if blackjack_player.hand_stood[hand_index]:
                hand_index += 1
                continue

            # Automatically finish busted hands
            if blackjack_player.is_bust():
                blackjack_player.hand_stood[hand_index] = True
                hand_index += 1
                continue

            # Automatically finish blackjack
            if blackjack_player.is_blackjack():
                blackjack_player.hand_stood[hand_index] = True
                hand_index += 1
                continue

            action = blackjack_player.decide_action(
                dealer_visible_card=self.dealer.hand.cards[0])

            # HIT
            if action == "hit":

                blackjack_player.hit(self.deck)

                Util.clear_screen()
                self.show_table()

                # Only move to next hand if busted
                if blackjack_player.is_bust():
                    blackjack_player.hand_stood[hand_index] = True
                    hand_index += 1

            # STAND
            elif action == "stand":

                blackjack_player.hand_stood[hand_index] = True

                Util.clear_screen()
                self.show_table()

                hand_index += 1

            # DOUBLE DOWN
            elif action == "double":

                current_bet = blackjack_player.hand_bets[hand_index]

                blackjack_player.chips -= current_bet
                blackjack_player.hand_bets[hand_index] *= 2
                blackjack_player.bet += current_bet

                blackjack_player.hit(self.deck)

                blackjack_player.hand_stood[hand_index] = True

                Util.clear_screen()
                self.show_table()

                hand_index += 1

            # SPLIT
            elif action == "split":

                self.split_hand(
                    blackjack_player,
                    hand_index
                )

                Util.clear_screen()
                self.show_table()

                # Stay on the current hand
                continue

    def split_hand(self, blackjack_player, hand_index):

        original_hand = blackjack_player.hands[hand_index]

        # Get the two original cards
        card1 = original_hand.cards[0]
        card2 = original_hand.cards[1]

        # Get the original bet
        original_bet = blackjack_player.hand_bets[hand_index]

        # Pay the additional bet
        blackjack_player.chips -= original_bet

        # Update player's total bet
        blackjack_player.bet += original_bet

        # Create two new hands
        hand1 = BlackjackHand()
        hand2 = BlackjackHand()

        # Give each hand one card
        hand1.add_card(card1)
        hand2.add_card(card2)

        # Replace original hand with first hand
        blackjack_player.hands[hand_index] = hand1

        # Add second hand
        blackjack_player.hands.insert(
            hand_index + 1,
            hand2
        )

        # Give both hands the same bet
        blackjack_player.hand_bets[hand_index] = original_bet

        blackjack_player.hand_bets.insert(
            hand_index + 1,
            original_bet
        )

        # Both hands are active
        blackjack_player.hand_stood[hand_index] = False

        blackjack_player.hand_stood.insert(
            hand_index + 1,
            False
        )

        # Deal one additional card to each split hand
        hand1.add_card(self.deck.deal_card())
        hand2.add_card(self.deck.deal_card())

        # Set active hand back to the first hand
        blackjack_player.set_active_hand(hand_index)

    def take_dealer_turn(self):

        # Reveal dealer's hand
        Util.clear_screen()
        self.show_table(reveal_dealer=True)
        time.sleep(2)

        while True:

            action = self.dealer.decide_action()

            if action == "hit":

                card = self.dealer.hit(self.deck)

                # Show what dealer drew
                Util.clear_screen()
                self.show_table(reveal_dealer=True)

                print(
                    f"\n  Dealer draws {card}."
                )

                time.sleep(2)

            else:

                Util.clear_screen()
                self.show_table(reveal_dealer=True)

                print(
                    f"\n  Dealer stands at "
                    f"{self.dealer.get_hand_value()}."
                )

                time.sleep(2)
                break

            if self.dealer.is_bust():

                Util.clear_screen()
                self.show_table(reveal_dealer=True)

                print(
                    f"\n  Dealer busts at "
                    f"{self.dealer.get_hand_value()}."
                )

                time.sleep(2)

                break

    def determine_winner(self):

        dealer_value = self.dealer.get_hand_value()
        dealer_busted = self.dealer.is_bust()

        print()
        print("=" * 50)
        print("                 ROUND RESULTS")
        print("=" * 50)
        print()

        for blackjack_player in self.blackjack_players:
            
            # Skip player if they are not playing
            if not blackjack_player.playing:
                continue

            # Evaluate every hand
            for index, hand in enumerate(blackjack_player.hands):

                player_value = hand.get_value()
                bet = blackjack_player.hand_bets[index]

                if len(blackjack_player.hands) == 1:
                    hand_name = blackjack_player.name
                else:
                    hand_name = (
                        f"{blackjack_player.name} "
                        f"Hand {index + 1}"
                    )

                print(f"  {hand_name}")
                print(f"    Hand:   {hand}")
                print(f"    Value:  {player_value}")
                print(f"    Bet:    {bet} chips")

                # Bust
                if hand.is_bust():

                    print("    Result: LOSS - Busted")

                # Blackjack
                elif hand.is_blackjack():

                    print("    Result: BLACKJACK!")

                    payout = bet * 1.5

                    print(
                        f"    Payout: +{payout:.0f} chips"
                    )

                    blackjack_player.chips += bet * 2.5

                # Dealer bust
                elif dealer_busted:

                    print("    Result: WIN - Dealer busted")

                    print(
                        f"    Payout: +{bet} chips"
                    )

                    blackjack_player.chips += bet * 2

                # Player beats dealer
                elif player_value > dealer_value:

                    print(
                        f"    Result: WIN - "
                        f"{player_value} beats "
                        f"{dealer_value}"
                    )

                    print(
                        f"    Payout: +{bet} chips"
                    )

                    blackjack_player.chips += bet * 2

                # Dealer beats player
                elif player_value < dealer_value:

                    print(
                        f"    Result: LOSS - "
                        f"{dealer_value} beats "
                        f"{player_value}"
                    )

                # Push
                else:

                    print(
                        f"    Result: PUSH - "
                        f"Tie at {player_value}"
                    )

                    print(
                        f"    Payout: "
                        f"{bet} chips returned"
                    )

                    blackjack_player.chips += bet

                print("    Chips: " + str(blackjack_player.chips))
                print("  " + "-" * 46)

        print("=" * 50)

    def players_info(self):

        for blackjack_player in self.blackjack_players:
            
            # Skip player if they are not playing
            if not blackjack_player.playing:
                continue
            
            print(blackjack_player.get_player_info())

    def welcome(self):

        Util.clear_screen()

        print()
        print("=" * 45)
        print("              BLACKJACK")
        print("=" * 45)
        print()

        print("  Welcome to Blackjack!")
        print()

        print("  Goal:")
        print("    Get as close to 21 as possible without")
        print("    going over.")
        print()

        print("  How to Play:")
        print("    • You and the dealer are dealt two cards.")
        print("    • Hit - Take another card.")
        print("    • Stand - Keep your current hand.")
        print("    • Double Down - Double your bet and")
        print("      receive exactly one more card.")
        print("    • Split - Split a pair into two hands.")
        print("    • The dealer must hit until reaching 17.")
        print("    • Go over 21 and you bust!")
        print()

        print("  Blackjack:")
        print("    An Ace + a 10-value card on your first")
        print("    two cards is a Blackjack.")
        print()

        print("=" * 45)
        print()