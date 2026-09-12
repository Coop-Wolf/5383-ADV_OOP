from .deck import Deck
from .dealer import Dealer
from .hand import Hand


# Game loop
class Game():
    def __init__(self, players):
        # create a deck of shuffled cards, players, and dealer
        self.deck = Deck()
        self.players = players
        self.dealer = Dealer("Dealer")

    # Main game loop
    def play_round(self):
        self.deck = Deck()
        self.deck.shuffle()

        # Reset hands for a fresh round
        for player in self.players:
            player.place_bet()

            player.hand = Hand()
        self.dealer.hand = Hand()
        
        print()
        print()

        # Deal 2 cards per player/dealer and show display cards
        self.deal_initial_cards()
        self.show_table()

        for player in self.players:
            self.take_player_turn(player)

        self.take_dealer_turn()
        self.determine_winner()

    def deal_initial_cards(self):
        # deal 2 cards to every player and dealer
        for _ in range(2):
            for player in self.players + [self.dealer]:
                player.hit(self.deck)
                

    def show_table(self):
        for player in self.players:
            print(f"{player.name}'s hand: {player.hand} (Value: {player.get_hand_value()})")
        print(f"Dealer shows: {self.dealer.get_visible_hand()}")

    def take_player_turn(self, player):
        while True:
            if player.is_bust():
                print(f"{player.name} busts!")
                break
            
            if player.is_blackjack():
                print(f"{player.name} BlackJack!")
                break

            action = player.decide_action(dealer_visible_card=self.dealer.hand.cards[0])

            if action == "hit":
                card = player.hit(self.deck)
                print(f"{player.name} draws {card}. Hand: {player.hand} (Value: {player.get_hand_value()})")
            else:
                print(f"{player.name} stands at {player.get_hand_value()}.")
                break

    def take_dealer_turn(self):
        print(f"\nDealer's full hand: {self.dealer.hand} (Value: {self.dealer.get_hand_value()})")

        while not self.dealer.is_bust():
            action = self.dealer.decide_action()
            if action == "hit":
                card = self.dealer.hit(self.deck)
                print(f"Dealer draws {card}. Hand: {self.dealer.hand} (Value: {self.dealer.get_hand_value()})")
            else:
                print(f"Dealer stands at {self.dealer.get_hand_value()}.")
                break

    def determine_winner(self):
        dealer_value = self.dealer.get_hand_value()
        dealer_busted = self.dealer.is_bust()

        for player in self.players:
            player_value = player.get_hand_value()

            if player.is_bust():
                print(f"{player.name} loses (busted).")
            elif player.is_blackjack():
                print(f"{player.name} wins! (Blackjack).")
                player.chips += 2.5 
            elif dealer_busted:
                print(f"{player.name} wins! Dealer busted.")
                player.chips += player.bet * 2
            elif player_value > dealer_value:
                print(f"{player.name} wins! {player_value} beats {dealer_value}.")
                player.chips += player.bet * 2
            elif player_value < dealer_value:
                print(f"{player.name} loses. {dealer_value} beats {player_value}.")
            else:
                print(f"{player.name} pushes (tie) at {player_value}.")
                player.chips += player.bet
                
    def players_info(self):
        for player in self.players:
            print(player.get_player_info())