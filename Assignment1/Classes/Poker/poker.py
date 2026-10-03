from ..game        import Game
from .pokerplayer import PokerPlayer
from ..deck        import Deck
from .pokerhand   import PokerHand
from ..util        import Util
from .pot         import Pot
import time

# Poker game
class Poker(Game):
    def __init__(self, players):
        
        self.name = "Poker"
        
        # Original Casino players
        self.players = players
        
        # Create pot
        self.pot = Pot()
        
        self.current_bet = 0
        
        # Cards on the table
        self.community_cards = []

        # Blackjack-specific players
        self.poker_players = [
            PokerPlayer(player.name, player.chips)
            for player in players
        ]
        


    # Main Game loop
    def play(self):

        self.welcome()

        if not self.whos_playing(self.poker_players, first_round=True):
            self.sync_players(self.players, self.poker_players, self.name)
            return

        while True:

            # Make sure at least 2 players are playing
            active_players = sum(player.playing for player in self.poker_players)

            if active_players < 2:
                # Sync player chips counts
                self.sync_players(self.players, self.poker_players, self.name)
                
                # Returning to main menu
                print("\nYou need at least 2 players to play Poker.")
                print("Returning to main menu...")
                time.sleep(3)
                return

            # Play one round of poker
            self.play_round()

            if not self.whos_playing(self.poker_players, first_round=False):
                self.sync_players(self.players, self.poker_players)
                break
            

    def play_round(self):
        self.deck = Deck()
        self.deck.shuffle()

        # Reset pot, community cards, and current bet
        self.pot = Pot()
        self.community_cards = []
        self.current_bet = 0

        # Reset players
        for poker_player in self.poker_players:

            if not poker_player.playing:
                continue

            poker_player.hand = PokerHand()
            poker_player.folded = False
            poker_player.bet = 0
            poker_player.total_bet = 0

        # Deal two cards to each player
        self.deal_initial_cards()

        # -------------------------
        # PRE-FLOP
        # -------------------------

        self.show_table()

        if not self.player_turns():
            self.determine_winner()
            return

        # -------------------------
        # FLOP
        # -------------------------

        self.deal_community_cards(3)
        self.reset_round_bets()

        self.show_table()

        if not self.player_turns():
            self.determine_winner()
            return

        # -------------------------
        # TURN
        # -------------------------

        self.deal_community_cards(1)
        self.reset_round_bets()

        self.show_table()

        if not self.player_turns():
            self.determine_winner()
            return

        # -------------------------
        # RIVER
        # -------------------------

        self.deal_community_cards(1)
        self.reset_round_bets()

        self.show_table()

        self.player_turns()

        # Determine winner
        self.determine_winner()
        
        
        
    def deal_initial_cards(self):
        for _ in range(2):
            for poker_player in self.poker_players:
                if not poker_player.playing:
                    continue
                poker_player.hit(self.deck)
                
    def deal_community_cards(self, amount):
        for _ in range(amount):
            self.community_cards.append(self.deck.deal_card())
            
            
    def show_table(self):
        Util.clear_screen()

        print()
        print("=" * 50)
        print("                    POKER")
        print("=" * 50)
        print()

        print("  COMMUNITY CARDS")
        print("  " + "-" * 44)

        if self.community_cards:
            print(f"  {' '.join(str(card) for card in self.community_cards)}")
        else:
            print("  No community cards yet.")

        print()
        print("=" * 50)
        
    def player_turns(self):
        while True:

            # Players who can still make a decision
            for poker_player in self.get_players_who_can_act():
                self.player_turn(poker_player)

            # If only one player remains, end the hand
            if len(self.get_active_players()) <= 1:
                return False

            # Check whether everyone has matched
            betting_complete = True

            for poker_player in self.get_players_who_can_act():
                if poker_player.bet < self.current_bet:
                    betting_complete = False
                    break

            if betting_complete:
                return True
            
    def player_turn(self, poker_player):
        if poker_player.folded:
            return

        if poker_player.chips == 0:
            return

        Util.clear_screen()
        self.show_table()

        action = poker_player.decide_action(
            self.current_bet,
            self.pot.amount
        )

        if action == "check":
            print(f"\n{poker_player.name} checks.")

        elif action == "call":
            self.call(poker_player)

        elif action == "raise":
            self.raise_bet(poker_player)

        elif action == "fold":
            poker_player.folded = True
            print(f"\n{poker_player.name} folds.")
            
    def determine_winner(self):
        print()
        print("=" * 50)
        print("                 ROUND RESULTS")
        print("=" * 50)
        print()

        # Get players who are still in the hand
        active_players = self.get_active_players()

        if not active_players:
            print("  No players remaining.")
            return

        # Only one player remains because everyone else folded
        if len(active_players) == 1:
            winner = active_players[0]

            winnings = self.pot.collect()

            # Give pot to winner
            winner.chips += winnings

            # Record winner's net earnings
            winner.earnings += winnings - winner.total_bet

            # Record losses for players who folded
            for poker_player in self.poker_players:
                if poker_player.folded:
                    poker_player.earnings -= poker_player.total_bet

            print(f"  WINNER: {winner.name}")
            print(f"  Winnings: {winnings} chips")
            print(
                f"  Earnings: "
                f"{winnings - winner.total_bet:+} chips"
            )

            print()
            print("=" * 50)
            return

        # Print community cards
        print("community cards")

        if self.community_cards:
            print(
                f"  {' '.join(str(card) for card in self.community_cards)}"
            )
        else:
            print("  No community cards.")

        print()

        # Evaluate each active player's hand
        players_with_hands = []

        for poker_player in active_players:

            hand_rank, hand_name = poker_player.hand.evaluate(
                self.community_cards
            )

            print(f"  {poker_player.name}")
            print(f"    Hand: {poker_player.hand}")
            print(f"    Result: {hand_name}")
            print()

            players_with_hands.append(
                (poker_player, hand_rank, hand_name)
            )

        # Find highest hand rank
        highest_rank = max(
            player[1]
            for player in players_with_hands
        )

        # Find all players with the highest rank
        winners = [
            player
            for player in players_with_hands
            if player[1] == highest_rank
        ]

        print("  " + "-" * 46)

        # One winner
        if len(winners) == 1:
            winner = winners[0][0]

            # Collect pot
            winnings = self.pot.collect()

            # Give pot to winner
            winner.chips += winnings

            # Record winner's net earnings
            winner.earnings += winnings - winner.total_bet

            print(f"  WINNER: {winner.name}")
            print(f"  Winnings: {winnings} chips")
            print(
                f"  Earnings: "
                f"{winnings - winner.total_bet:+} chips"
            )

        # Multiple winners
        else:
            # Split pot between winners
            winnings = self.pot.collect()
            share = winnings // len(winners)

            # Leftover chips go to the casino
            casino_tip = winnings % len(winners)

            print("  TIE!")

            for winner in winners:
                player = winner[0]

                player.chips += share

                # Record net earnings
                player.earnings += share - player.total_bet

                print(
                    f"    {player.name} wins {share} chips "
                    f"({share - player.total_bet:+} earnings)"
                )

            if casino_tip > 0:
                print(
                    f"    Casino tip: {casino_tip} chips"
                )

        # Record losses for players who folded
        for poker_player in self.poker_players:
            if poker_player.folded:
                poker_player.earnings -= poker_player.total_bet

        print()
        print("=" * 50)
        
    def call(self, poker_player):
        amount = self.current_bet - poker_player.bet

        if amount > poker_player.chips:
            amount = poker_player.chips

        poker_player.chips -= amount
        poker_player.bet += amount
        poker_player.total_bet += amount

        self.pot.add(amount)

        print(
            f"\n{poker_player.name} calls "
            f"{amount} chips."
        )
        
    def raise_bet(self, poker_player):
        while True:
            try:
                new_bet = int(
                    input(
                        "\n  Enter your new total bet: "
                    )
                )

                if new_bet <= self.current_bet:
                    print(
                        "  ERROR: Raise must be greater "
                        "than the current bet."
                    )

                elif new_bet <= poker_player.bet:
                    print(
                        "  ERROR: Your new bet must be "
                        "greater than your current bet."
                    )

                else:
                    amount = new_bet - poker_player.bet

                    if amount > poker_player.chips:
                        print(
                            "  ERROR: You don't have enough chips."
                        )
                        continue

                    poker_player.chips -= amount
                    poker_player.bet = new_bet
                    poker_player.total_bet += amount

                    self.pot.add(amount)

                    self.current_bet = new_bet

                    print(
                        f"\n{poker_player.name} raises "
                        f"to {new_bet} chips."
                    )

                    break

            except ValueError:
                print("  ERROR: Please enter a valid number.")
                
    def reset_round_bets(self):
        for poker_player in self.poker_players:
            
            if not poker_player.playing:
                continue
            
            poker_player.bet = 0

        self.current_bet = 0
        
    # Check if only one player is remaining in the game
    def one_player_remaining(self):
        active_players = 0

        for poker_player in self.poker_players:
            if not poker_player.playing:
                continue

            if poker_player.folded:
                continue

            active_players += 1

        return active_players <= 1
    
    # List of players active and have not folded
    def get_active_players(self):
        return [
            player
            for player in self.poker_players
            if player.playing and not player.folded
        ]
        
    # List of players who are active and able to place bets
    def get_players_who_can_act(self):
        return [
            player
            for player in self.poker_players
            if player.playing
            and not player.folded
            and player.chips > 0
        ]
        
    def welcome(self):
        Util.clear_screen()
        
        print()
        print("=" * 45)
        print("                  POKER")
        print("=" * 45)
        print()
        print("  Welcome to Poker!")
        print()
        print("  Goal:")
        print("    Make the best five-card poker hand")
        print("    using your two cards and the")
        print("    community cards.")
        print()
        print("  How to Play:")
        print("    • Each player is dealt two cards.")
        print("    • Five community cards are dealt.")
        print("    • The community cards are revealed")
        print("      in three stages: Flop, Turn, River.")
        print("    • Players bet after each stage.")
        print()
        print("  Actions:")
        print("    • Check - Stay in without adding chips.")
        print("    • Call  - Match the current table bet.")
        print("    • Raise - Increase the current table bet.")
        print("    • Fold  - Leave the current hand.")
        print()
        print("  Winning:")
        print("    The player with the highest-ranking")
        print("    five-card hand wins the pot.")
        print()
        print("=" * 45)
        print()
        