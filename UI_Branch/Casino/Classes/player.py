
class Player:
 
    # Display names for the stats screen, keyed by the game names the database uses
    GAME_LABELS = {
        "Blackjack": "Blackjack",
        "VideoPoker": "Video Poker",
        "War": "War",
    }
 
    def __init__(self, name, chips=100, player_id=None):
        self.id = player_id
        self.name = name
        self.chips = chips
        self.starting_amount = chips
        self.bet = 0
        self.funds_added = 0
        self.blackjack_earnings = 0
        self.videopoker_earnings = 0
        self.war_earnings = 0
        self.earnings = 0
 
    # Add chips to the player's balance. Returns the new chip count.
    def add_funds(self, amount):
        if not isinstance(amount, int) or amount <= 0:
            raise ValueError("Amount must be a positive whole number")
 
        self.chips += amount
        self.funds_added += amount
        return self.chips
 
    # Move chips from the player into a bet
    def wager(self, amount):
        self.chips -= amount
        self.bet += amount
 
    # Bet was already deducted, so return it plus the profit
    def win(self, bet, multiplier=1):
        profit = int(bet * multiplier)
        self.chips += bet + profit
        self.earnings += profit
        return profit
 
    # Bet was already deducted, so only record the loss
    def lose(self, bet):
        self.earnings -= bet
 
    # Bet is returned, with no profit or loss
    def push(self, bet):
        self.chips += bet
 
    # Understood to mean get a card
    def hit(self, deck):
        card = deck.deal_card()
        self.hand.add_card(card)
        return card