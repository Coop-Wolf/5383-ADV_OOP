
from ..game import Game
from ..dealer import Dealer
from .warplayer import WarPlayer
from ..deck import Deck
from ..hand import Hand
 
 
class War(Game):
 
    name = "War"
    player_class = WarPlayer
 
    def __init__(self, player, db=None):
        super().__init__(player, db=db)
 
        self.war_dealer = Dealer()
        self.war_player = self.game_player
 
        self.deck = None
        self.outcome = None
        self.net_change = 0
 
    # The two cards in play
    @property
    def player_card(self):
        return self.war_player.hand.cards[0]
 
    @property
    def dealer_card(self):
        return self.war_dealer.hand.cards[0]
 
    def deal(self, bet):
        """Start a round: new shuffled deck, fresh hands, place the bet, one card each."""
 
        self.deck = Deck()
 
        self.war_player.hand = Hand()
        self.war_dealer.reset_hand()
 
        self.collect_bet(self.war_player, bet)
 
        self.war_player.hit(self.deck)
        self.war_dealer.hit(self.deck)
 
        self.outcome = None
        self.net_change = 0
 
    def determine_winner(self):
        """
        Compare the cards (Ace is high), settle the bet, and save the result.
        Returns (outcome, net_change).
        """
 
        player_value = self.player_card.get_poker_value()
        dealer_value = self.dealer_card.get_poker_value()
        bet = self.war_player.bet
 
        if player_value > dealer_value:
            outcome = "win"
        elif player_value < dealer_value:
            outcome = "loss"
        else:
            outcome = "push"
 
        self.net_change = self.settle(self.war_player, bet, outcome)
        self.outcome = outcome
 
        return self.outcome, self.net_change