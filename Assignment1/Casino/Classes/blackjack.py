from .blackjackplayer import BlackjackPlayer
from .dealer import Dealer
from .deck import Deck
from .blackjackhand import BlackjackHand
import os


class Blackjack:
    def __init__(self, players):
        # Original Casino players
        self.players = players

        # Blackjack-specific players
        self.blackjack_players = [
            BlackjackPlayer(player.name, player.chips)
            for player in players
        ]

        self.dealer = Dealer()
        
    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    # Main Blackjack session loop
    def play(self):
        while True:
            self.welcome()
            self.play_round()

            while True:
                choice = input("\nPlay another round? (y/n): ").strip().lower()

                if choice == "y":
                    break
                elif choice == "n":
                    self.sync_players()
                    return
                else:
                    print("ERROR: please enter 'y' or 'n'.")

    # Play one round
    def play_round(self):
        self.deck = Deck()
        self.deck.shuffle()

        # Reset hands and place bets
        for blackjack_player in self.blackjack_players:
            blackjack_player.place_bet()
            blackjack_player.hand = BlackjackHand()

        self.dealer.hand = BlackjackHand()

        # Deal initial cards
        self.clear_screen()
        self.deal_initial_cards()

        # Show completed initial deal
        self.clear_screen()
        self.show_table()

        # Player turns
        for blackjack_player in self.blackjack_players:
            self.take_player_turn(blackjack_player)

        # Dealer turn
        self.take_dealer_turn()

        # Show final table
        self.clear_screen()
        self.show_table()

        # Determine winners
        self.determine_winner()

    def deal_initial_cards(self):
        # Deal 2 cards to every player and dealer
        for _ in range(2):
            for blackjack_player in self.blackjack_players:
                blackjack_player.hit(self.deck)

            self.dealer.hit(self.deck)

    def show_table(self):
        print()
        print("=" * 50)
        print("                  BLACKJACK")
        print("=" * 50)
        print()

        print("  YOUR HANDS")
        print("  " + "-" * 44)

        for blackjack_player in self.blackjack_players:
            value = blackjack_player.get_hand_value()

            if value > 21:
                status = "(Busted)"
            elif blackjack_player.is_blackjack():
                status = "(Blackjack)"
            else:
                status = ""

            print(
                f"  {blackjack_player.name:<15}"
                f"{str(blackjack_player.hand):<22}"
                f"Value: {value:<3} {status}"
            )

        # Dealer section is OUTSIDE the player loop
        print()
        print("  DEALER")
        print("  " + "-" * 44)
        print(
            f"  {str(self.dealer.get_visible_hand()):<22}"
        )

        print()
        print("=" * 50)

    def take_player_turn(self, blackjack_player):
        while True:
            if blackjack_player.is_bust():
                print(f"{blackjack_player.name} busts!")
                break

            if blackjack_player.is_blackjack():
                print(f"{blackjack_player.name} has Blackjack!")
                break

            action = blackjack_player.decide_action(
                dealer_visible_card=self.dealer.hand.cards[0]
            )

            if action == "hit":
                card = blackjack_player.hit(self.deck)

                print(
                    f"\n{blackjack_player.name} draws {card}."
                )

                # Immediately refresh the table
                self.clear_screen()
                self.show_table()

            else:
                print(
                    f"\n{blackjack_player.name} stands at "
                    f"{blackjack_player.get_hand_value()}."
                )

                # Refresh the table
                self.clear_screen()
                self.show_table()

                break
            

    def take_dealer_turn(self):
        print()
        print("=" * 50)
        print("                 DEALER TURN")
        print("=" * 50)
        print()

        print(
            f"  Dealer's hand: {self.dealer.hand}"
        )
        print(
            f"  Dealer's value: {self.dealer.get_hand_value()}"
        )
        print()

        while not self.dealer.is_bust():
            action = self.dealer.decide_action()

            if action == "hit":
                card = self.dealer.hit(self.deck)
                print(f"  Dealer draws {card}.")
            else:
                print(
                    f"  Dealer stands at "
                    f"{self.dealer.get_hand_value()}."
                )
                break

        if self.dealer.is_bust():
            print(
                f"  Dealer busts at "
                f"{self.dealer.get_hand_value()}."
            )

        print()
        print("=" * 50)

    def determine_winner(self):
        dealer_value = self.dealer.get_hand_value()
        dealer_busted = self.dealer.is_bust()

        print()
        print("=" * 50)
        print("                 ROUND RESULTS")
        print("=" * 50)
        print()

        for blackjack_player in self.blackjack_players:
            player_value = blackjack_player.get_hand_value()

            print(f"  {blackjack_player.name}")
            print(f"    Hand:   {blackjack_player.hand}")
            print(f"    Value:  {player_value}")
            print(f"    Bet:    {blackjack_player.bet} chips")

            if blackjack_player.is_bust():
                print("    Result: LOSS - Busted")

            elif blackjack_player.is_blackjack():
                print("    Result: BLACKJACK!")
                print(
                    f"    Payout: +{blackjack_player.bet * 1.5:.0f} chips"
                )
                blackjack_player.chips += blackjack_player.bet * 2.5

            elif dealer_busted:
                print("    Result: WIN - Dealer busted")
                print(
                    f"    Payout: +{blackjack_player.bet} chips"
                )
                blackjack_player.chips += blackjack_player.bet * 2

            elif player_value > dealer_value:
                print(
                    f"    Result: WIN - {player_value} beats {dealer_value}"
                )
                print(
                    f"    Payout: +{blackjack_player.bet} chips"
                )
                blackjack_player.chips += blackjack_player.bet * 2

            elif player_value < dealer_value:
                print(
                    f"    Result: LOSS - "
                    f"{dealer_value} beats {player_value}"
                )

            else:
                print(f"    Result: PUSH - Tie at {player_value}")
                print(
                    f"    Payout: {blackjack_player.bet} chips returned"
                )
                blackjack_player.chips += blackjack_player.bet

            print()
            print("  " + "-" * 46)

        print("=" * 50)

    def players_info(self):
        for blackjack_player in self.blackjack_players:
            print(blackjack_player.get_player_info())
            
    def welcome(self):
        self.clear_screen()
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
        print("    • Choose to Hit or Stand.")
        print("    • Hit  - Take another card.")
        print("    • Stand - Keep your current hand.")
        print("    • The dealer must hit until reaching 17.")
        print("    • Go over 21 and you bust!")
        print()
        print("  Blackjack:")
        print("    An Ace + a 10-value card on your first")
        print("    two cards is a Blackjack.")
        print()
        print("=" * 45)
        print()

    def sync_players(self):
        # Copy Blackjack chip balances back to Casino players
        for casino_player, blackjack_player in zip(
            self.players,
            self.blackjack_players
        ):
            casino_player.chips = blackjack_player.chips