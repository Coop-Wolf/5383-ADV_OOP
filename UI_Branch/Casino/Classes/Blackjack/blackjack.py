
from .blackjackplayer import BlackjackPlayer
from .blackjackdealer import BlackjackDealer
from ..deck import Deck
from ..game import Game
 
 
class Blackjack(Game):
 
    name = "Blackjack"
    player_class = BlackjackPlayer
 
    def __init__(self, player, db=None):
        super().__init__(player, db=db)
 
        self.blackjack_player = self.game_player
        self.dealer = BlackjackDealer()
 
        self.deck = None
        self.results = []
 
    # ------------------------------------------------------------------
    # Round setup
    # ------------------------------------------------------------------
    def deal(self, bet):
        """Start a round: new deck, place the bet, deal two cards to each side."""
 
        self.deck = Deck()
        self.results = []
 
        self.blackjack_player.reset_hands()
        self.collect_bet(self.blackjack_player, bet)
 
        # Store the initial bet on the first hand
        self.blackjack_player.hand.bet = self.blackjack_player.bet
 
        self.dealer.reset_hand()
 
        for _ in range(2):
            self.blackjack_player.hit(self.deck)
            self.dealer.hit(self.deck)
 
        # A starting 21 needs no decisions
        self._advance()
 
    # ------------------------------------------------------------------
    # Player turn
    # ------------------------------------------------------------------
    @property
    def player_turn_over(self):
        return all(hand.stood for hand in self.blackjack_player.hands)
 
    def available_actions(self):
        if self.player_turn_over:
            return []
 
        return self.blackjack_player.available_actions()
 
    def hit(self):
        self._require("hit")
        self.blackjack_player.hit(self.deck)
        self._advance()
 
    def stand(self):
        self._require("stand")
        self.blackjack_player.hand.stood = True
        self._advance()
 
    def double_down(self):
        self._require("double")
        self.blackjack_player.double_down(self.deck)
        self._advance()
 
    def split(self):
        self._require("split")
        self.blackjack_player.split(self.deck)
 
        # Stay on the current hand, unless it came up 21
        self._advance()
 
    def _require(self, action):
        if action not in self.available_actions():
            raise ValueError(f"Action not available: {action}")
 
    def _advance(self):
        """
        Finish every hand that needs no more decisions (busted or 21),
        and move to the next hand that does.
        """
 
        player = self.blackjack_player
        index = player.active_index
 
        while index < len(player.hands):
 
            player.set_active_hand(index)
            hand = player.hand
 
            # This hand still needs a decision
            if not hand.stood and not hand.is_bust() and hand.get_value() != 21:
                return
 
            hand.stood = True
            index += 1
 
    # ------------------------------------------------------------------
    # Dealer turn (the screen calls these one step at a time)
    # ------------------------------------------------------------------
    @property
    def dealer_needs_to_play(self):
        # If every player hand busted, the dealer's cards can't change the result
        return not all(hand.is_bust() for hand in self.blackjack_player.hands)
 
    def dealer_should_hit(self):
        return self.dealer.decide_action() == "hit"
 
    def dealer_hit(self):
        return self.dealer.hit(self.deck)
 
    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------
    def determine_winner(self):
        """
        Settle every hand and save the results.
        Returns a list with one dict per hand:
            {"outcome": "win"/"loss"/"push", "detail": str, "net_change": int}
        """
 
        dealer_value = self.dealer.get_hand_value()
        dealer_busted = self.dealer.is_bust()
        dealer_blackjack = self.dealer.hand.is_blackjack()
 
        self.results = []
 
        for hand in self.blackjack_player.hands:
 
            player_value = hand.get_value()
            multiplier = 1
 
            if hand.is_bust():
                outcome, detail = "loss", "Busted"
 
            elif hand.is_blackjack() and dealer_blackjack:
                outcome, detail = "push", "Both have blackjack"
 
            elif hand.is_blackjack():
                outcome, detail, multiplier = "win", "Blackjack!", 1.5
 
            elif dealer_blackjack:
                outcome, detail = "loss", "Dealer has blackjack"
 
            elif dealer_busted:
                outcome, detail = "win", "Dealer busted"
 
            elif player_value > dealer_value:
                outcome, detail = "win", f"{player_value} beats {dealer_value}"
 
            elif player_value < dealer_value:
                outcome, detail = "loss", f"{dealer_value} beats {player_value}"
 
            else:
                outcome, detail = "push", f"Tie at {player_value}"
 
            net_change = self.settle(self.blackjack_player, hand.bet, outcome, multiplier)
 
            self.results.append({
                "outcome": outcome,
                "detail": detail,
                "net_change": net_change,
            })
 
        return self.results
 
