
from abc import ABC, abstractmethod
 
 
class Game(ABC):
 
    # Subclasses override these
    name = "Game"
    player_class = None
 
    def __init__(self, player, db=None):
 
        # Original casino player (carries the database id)
        self.player = player
        self.db = db
 
        # Game-specific player
        self.game_player = self.player_class(player.name, player.chips)
 
    # Save one finished hand to the database (updates chips and stats)
    def record_result(self, outcome, net_change):
        if self.db is not None:
            self.db.record_result(self.player.id, self.name, outcome, net_change)
 
    # Apply a hand's result to the player's chips and earnings, and save it.
    # Returns the net change (profit for a win, -bet for a loss, 0 for a push)
    def settle(self, player, bet, outcome, multiplier=1):
 
        if outcome == "win":
            net_change = player.win(bet, multiplier)
 
        elif outcome == "loss":
            player.lose(bet)
            net_change = -bet
 
        else:
            player.push(bet)
            net_change = 0
 
        self.record_result(outcome, net_change)
        return net_change
 
    # Apply a bet to the player (the UI decides the amount)
    def collect_bet(self, player, amount):
 
        if amount < 1 or amount > player.chips:
            raise ValueError(f"Invalid bet: {amount}")
 
        # Reset first: wager() adds to bet, and last round's bet is still there
        player.bet = 0
        player.wager(amount)
 
    # Each game implements these
    @abstractmethod
    def deal(self, bet): ...
 
    @abstractmethod
    def determine_winner(self): ...
 
