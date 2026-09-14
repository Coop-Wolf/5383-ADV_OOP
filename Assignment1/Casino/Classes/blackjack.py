from .blackjackplayer import BlackjackPlayer
from .dealer import Dealer
from .deck import Deck
from .blackjackhand import BlackjackHand


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

    # Main Blackjack session loop
    def play(self):
        while True:
            self.play_round()

            self.players_info()

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

        # Reset hands for a fresh round
        for blackjack_player in self.blackjack_players:
            blackjack_player.place_bet()
            blackjack_player.hand = BlackjackHand()

        self.dealer.hand = BlackjackHand()

        print()
        print()

        # Deal 2 cards to every player and dealer
        self.deal_initial_cards()
        self.show_table()

        # Player turns
        for blackjack_player in self.blackjack_players:
            self.take_player_turn(blackjack_player)

        # Dealer turn
        self.take_dealer_turn()

        # Determine winners
        self.determine_winner()

    def deal_initial_cards(self):
        # Deal 2 cards to every player and dealer
        for _ in range(2):
            for blackjack_player in self.blackjack_players:
                blackjack_player.hit(self.deck)

            self.dealer.hit(self.deck)

    def show_table(self):
        for blackjack_player in self.blackjack_players:
            print(
                f"{blackjack_player.name}'s hand: "
                f"{blackjack_player.hand} "
                f"(Value: {blackjack_player.get_hand_value()})"
            )

        print(f"Dealer shows: {self.dealer.get_visible_hand()}")

    def take_player_turn(self, blackjack_player):
        while True:
            if blackjack_player.is_bust():
                print(f"{blackjack_player.name} busts!")
                break

            if blackjack_player.is_blackjack():
                print(f"{blackjack_player.name} Blackjack!")
                break

            action = blackjack_player.decide_action(
                dealer_visible_card=self.dealer.hand.cards[0]
            )

            if action == "hit":
                card = blackjack_player.hit(self.deck)

                print(
                    f"{blackjack_player.name} draws {card}. "
                    f"Hand: {blackjack_player.hand} "
                    f"(Value: {blackjack_player.get_hand_value()})"
                )
            else:
                print(
                    f"{blackjack_player.name} stands at "
                    f"{blackjack_player.get_hand_value()}."
                )
                break

    def take_dealer_turn(self):
        print(
            f"\nDealer's full hand: {self.dealer.hand} "
            f"(Value: {self.dealer.get_hand_value()})"
        )

        while not self.dealer.is_bust():
            action = self.dealer.decide_action()

            if action == "hit":
                card = self.dealer.hit(self.deck)

                print(
                    f"Dealer draws {card}. "
                    f"Hand: {self.dealer.hand} "
                    f"(Value: {self.dealer.get_hand_value()})"
                )
            else:
                print(
                    f"Dealer stands at "
                    f"{self.dealer.get_hand_value()}."
                )
                break

    def determine_winner(self):
        dealer_value = self.dealer.get_hand_value()
        dealer_busted = self.dealer.is_bust()

        for blackjack_player in self.blackjack_players:
            player_value = blackjack_player.get_hand_value()

            if blackjack_player.is_bust():
                print(
                    f"{blackjack_player.name} loses (busted)."
                )

            elif blackjack_player.is_blackjack():
                print(
                    f"{blackjack_player.name} wins! (Blackjack)."
                )
                blackjack_player.chips += blackjack_player.bet * 2.5

            elif dealer_busted:
                print(
                    f"{blackjack_player.name} wins! Dealer busted."
                )
                blackjack_player.chips += blackjack_player.bet * 2

            elif player_value > dealer_value:
                print(
                    f"{blackjack_player.name} wins! "
                    f"{player_value} beats {dealer_value}."
                )
                blackjack_player.chips += blackjack_player.bet * 2

            elif player_value < dealer_value:
                print(
                    f"{blackjack_player.name} loses. "
                    f"{dealer_value} beats {player_value}."
                )

            else:
                print(
                    f"{blackjack_player.name} pushes (tie) "
                    f"at {player_value}."
                )
                blackjack_player.chips += blackjack_player.bet

    def players_info(self):
        for blackjack_player in self.blackjack_players:
            print(blackjack_player.get_player_info())

    def sync_players(self):
        # Copy Blackjack chip balances back to Casino players
        for casino_player, blackjack_player in zip(
            self.players,
            self.blackjack_players
        ):
            casino_player.chips = blackjack_player.chips