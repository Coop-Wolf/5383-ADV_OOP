import random


# Cards
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    # Return value of card
    def get_value(self):
        if self.rank in ["Jack", "Queen", "King"]:
            return 10
        if self.rank == "Ace":
            # Hand class will adjust this down if needed
            return 11
        return int(self.rank)

    # Return value and suit of card
    def __str__(self):
        return f"{self.rank} of {self.suit}"


# Deck is a list of unique cards
class Deck:
    SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
    RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10",
              "Jack", "Queen", "King", "Ace"]

    # Put every possible card in the "cards" list
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in self.SUITS for rank in self.RANKS]

    def shuffle(self):
        random.shuffle(self.cards)

    # Get a card off the list of cards
    def deal_card(self):
        return self.cards.pop()


# Hand per player and dealer
class Hand:
    def __init__(self):
        # List of cards
        self.cards = []

    # Add a card to hand
    def add_card(self, card):
        self.cards.append(card)

    # Get total value of hand
    def get_value(self):
        total = sum(card.get_value() for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == "Ace")

        # Downgrade Aces from 11 to 1 as needed to avoid busting
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        return total

    def is_bust(self):
        return self.get_value() > 21

    # Blackjack can only happen with opening hand
    def is_blackjack(self):
        return len(self.cards) == 2 and self.get_value() == 21

    def __str__(self):
        return ", ".join(str(card) for card in self.cards)


# Person is a parent class to players and the dealer
class Person:

    def __init__(self, name, chips=100):
        self.name = name
        self.hand = Hand()
        self.chips = chips

    def hit(self, deck):
        card = deck.deal_card()
        self.hand.add_card(card)
        return card

    # Do nothing here
    def stand(self):
        pass

    def get_hand_value(self):
        return self.hand.get_value()

    def is_bust(self):
        return self.hand.is_bust()
    
    def is_blackjack(self):
        return self.hand.is_blackjack()

    # Child class will override
    def decide_action(self, dealer_visible_card=None):
        return "stand"


# Player
class Player(Person):

    def __init__(self, name, chips=100, bet=0):
        # initialze name and chips from parent class
        super().__init__(name, chips)
        
        # initialize bet and starting_amount
        self.bet = bet
        self.starting_amount = chips

    # Player can either hit or stand
    def decide_action(self, dealer_visible_card=None):
        choice = input(f"{self.name}, hit or stand? ").strip().lower()
        
        if choice == "hit" or choice == "stand":
            return choice
        else:
            self.decide_action()
    
    def get_starting_amount(self):
        return self.starting_amount
    
    def get_player_info(self):
        return f"{self.name}: {self.chips} chips"

    def place_bet(self):
        
        # Continue until player places correct bet amount
        while True:
            bet = int(input(f"{self.name}, place your bet: "))

            if bet <= 0:
                print("ERROR: bet must be greater than 0. Try again.")
                print()
            elif bet > self.chips:
                print("ERROR: bet exceeded player chip amount. Try again.")
                print()
            else:
                break

        self.chips -= bet
        self.bet = bet


# Dealer
class Dealer(Person):
    
    # Must hit until 17 or higher
    def decide_action(self, dealer_visible_card=None):
        return "hit" if self.get_hand_value() < 17 else "stand"

    def get_visible_hand(self):
        # Only show the first card; hide the rest ("hole card")
        if not self.hand.cards:
            return ""
        return f"{self.hand.cards[0]} and [hidden]"
        

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



# Get number of players
def get_players():
    num_players = int(input("Number of players: "))
    players = []

    for i in range(num_players):
        name = input(f"Player {i+1} Name: ")
        money = input(f"Money for {name}: ")
        players.append(Player(name, chips=int(money)))
        
    print()
    return players


def ask_to_continue(player):
    choice = input(f"{player.name}, would you like to keep playing? (y/n): ").strip().lower()
    return choice == "y"


peeps = get_players()
game = Game(peeps)


# Main game loop
while game.players:
    print("====================")
    print()
    game.play_round()
    print()
    print("====================")
    print()

    print("\n--- Round Results ---")
    for player in game.players:
        print(player.get_player_info())
    print()

    # Ask each player if they want to continue
    remaining_players = []
    for player in game.players:
        if ask_to_continue(player):
            remaining_players.append(player)
        else:
            print(f"{player.name} started with {player.get_starting_amount()}, and has left the table with {player.chips} chips.")

    game.players = remaining_players

    if not game.players:
        print("\nAll players have left. Game over!")