import random


# Card
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def get_value(self):
        if self.rank in ["Jack", "Queen", "King"]:
            return 10
        if self.rank == "Ace":
            return 11  # Hand class will adjust this down if needed
        return int(self.rank)

    def __str__(self):
        return f"{self.rank} of {self.suit}"


# Deck
class Deck:
    SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
    RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10",
              "Jack", "Queen", "King", "Ace"]

    def __init__(self):
        self.cards = [Card(suit, rank) for suit in self.SUITS for rank in self.RANKS]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop()


# Hand
class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

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

    def is_blackjack(self):
        return len(self.cards) == 2 and self.get_value() == 21

    def __str__(self):
        return ", ".join(str(card) for card in self.cards)


# Person
class Person:

    def __init__(self, name, chips=100):
        self.name = name
        self.hand = Hand()
        self.chips = chips

    def hit(self, deck):
        card = deck.deal_card()
        self.hand.add_card(card)
        return card

    def stand(self):
        pass  # no state change needed; turn simply ends

    def get_hand_value(self):
        return self.hand.get_value()

    def is_bust(self):
        return self.hand.is_bust()

    def decide_action(self, dealer_visible_card=None):
        # Default behavior — subclasses override this
        return "stand"


# Player
class Player(Person):
    def decide_action(self, dealer_visible_card=None):
        choice = input(f"{self.name}, hit or stand? ").strip().lower()
        return "hit" if choice == "hit" else "stand"


# Dealer
class Dealer(Person):
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
        self.deck = Deck()
        self.players = players          # list of Player subclass instances (Human/Bot)
        self.dealer = Dealer("Dealer")

    def play_round(self):
        self.deck = Deck()
        self.deck.shuffle()

        # Reset hands for a fresh round
        for player in self.players:
            player.hand = Hand()
        self.dealer.hand = Hand()

        self.deal_initial_cards()
        self.show_table()

        for player in self.players:
            self.take_player_turn(player)

        self.take_dealer_turn()
        self.determine_winner()

    def deal_initial_cards(self):
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
            elif dealer_busted:
                print(f"{player.name} wins! Dealer busted.")
            elif player_value > dealer_value:
                print(f"{player.name} wins! {player_value} beats {dealer_value}.")
            elif player_value < dealer_value:
                print(f"{player.name} loses. {dealer_value} beats {player_value}.")
            else:
                print(f"{player.name} pushes (tie) at {player_value}.")



player = Player("Cooper")
player2 = Player("Kenzi")
player3 = Player("Bob")

game = Game([player, player2, player3])
game.play_round()