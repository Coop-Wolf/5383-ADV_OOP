from ..game import Game
from .wardealer import Wardealer
from .warplayer import WarPlayer
from ..deck import Deck
from ..hand import Hand
from ..util import Util
import time

class War(Game):

    def __init__(self, player):
        
        self.name = "War"
        
        # Original Casino players
        self.player = player

        self.war_dealer = Wardealer()
        self.war_player = WarPlayer(player.name, player.chips)


    # Main Game loop
    def play(self):

        #self.welcome()

        while True:

            # Play one round of war
            self.play_round()

            if not self.whos_playing(self.war_player):
                self.sync_players(self.player, self.war_player, self.name)
                break
            
            
    def play_round(self):
        
        # Create deck and shuffle cards
        self.deck = Deck()
        self.deck.shuffle()
        
        # Create/reset player and dealer hand
        self.war_player.hand = Hand()
        self.war_dealer.hand = Hand()
        
        # Player place bet
        Util.clear_screen()
        self.war_player.place_bet()
        Util.clear_screen()
        
        # Deal player card
        card = self.deck.deal_card()
        self.war_player.hand.add_card(card)
        
        # Show table
        self.show_table()
        time.sleep(2)
        Util.clear_screen()
        
        # Deal dealer card
        card = self.deck.deal_card()
        self.war_dealer.hand.add_card(card)
        
        # Show table
        self.show_table(reveal_dealer=True)
        time.sleep(2)
        Util.clear_screen()
        
        # Determine winner
        self.determine_winner()
        
        
    def determine_winner(self):

        # Get card from player and dealer
        player_card = self.war_player.hand.cards[0]
        dealer_card = self.war_dealer.hand.cards[0]

        # Get card rank
        player_card_rank = player_card.rank
        dealer_card_rank = dealer_card.rank

        # Get card value
        player_hand_value = player_card.get_poker_value(player_card_rank)
        dealer_hand_value = dealer_card.get_poker_value(dealer_card_rank)

        # Get player bet
        bet = self.war_player.bet

        # Print results to terminal
        print()
        print("=" * 50)
        print("                 ROUND RESULTS")
        print("=" * 50)
        print()

        print(f"  {self.war_player.name}")
        print(f"    Card:   {player_card}")
        print(f"    Bet:    {bet} chips")

        print()

        print("  Dealer")
        print(f"    Card:   {dealer_card}")

        print()

        # Player wins
        if player_hand_value > dealer_hand_value:

            print(
                f"    Result: WIN - "
                f"{player_hand_value} beats "
                f"{dealer_hand_value}"
            )

            print(
                f"    Payout: +{bet} chips"
            )

            self.war_player.chips += bet * 2

            # Record net profit
            self.war_player.earnings += bet

        # Dealer wins
        elif player_hand_value < dealer_hand_value:

            print(
                f"    Result: LOSS - "
                f"{dealer_hand_value} beats "
                f"{player_hand_value}"
            )

            # Record net loss
            self.war_player.earnings -= bet

        # Tie
        else:

            print(
                f"    Result: PUSH - "
                f"Tie at {player_hand_value}"
            )

            print(
                f"    Payout: "
                f"{bet} chips returned"
            )

            self.war_player.chips += bet

            # No profit or loss
            # earnings stays the same

        print(
            f"    Chips: {self.war_player.chips}"
        )

        print("  " + "-" * 46)
        print("=" * 50)
        
        
    def show_table(self, reveal_dealer=False):

        print()
        print("=" * 80)
        print("                                      WAR")
        print("=" * 80)
        print()

        # Player section
        print("  YOU")
        print("  " + "-" * 70)

        player_card = str(self.war_player.hand)

        print(
            f"  {self.war_player.name:<20}"
            f"{player_card:<20}"
            f"Bet: {self.war_player.bet}"
        )

        # Dealer section
        print()
        print("  DEALER")
        print("  " + "-" * 70)

        if reveal_dealer:
            dealer_card = str(self.war_dealer.hand)

            print(
                f"  {'Dealer':<20}"
                f"{dealer_card:<20}")

        else:
            print(f"  {'Dealer':<20}")

        print()
        print("=" * 80)