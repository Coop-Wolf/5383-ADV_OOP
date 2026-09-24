from .util import Util


# Player
class Player:

    def __init__(self, name, chips=100):
        self.name = name
        self.chips = chips
        self.bet = 0
        self.starting_amount = chips
        self.funds_added = 0
        self.blackjack_earnings = 0
        self.videopoker_earnings = 0
        self.war_earnings = 0

        # Per-game earnings. Game players use this, and
        # Game.sync_players adds it to the totals above.
        self.earnings = 0
        self.playing = True

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

    def get_player_info(self):
        total_earnings = (
            self.blackjack_earnings
            + self.videopoker_earnings
            + self.war_earnings
        )

        return (
            f"  {self.name.upper()}\n"
            f"  {'-' * 48}\n"
            f"  {'Starting Amount:':<30} {self.starting_amount:>10,} chips\n"
            f"  {'Funds Added:':<30} {self.funds_added:>10,} chips\n"
            f"  {'Current Chips:':<30} {self.chips:>10,} chips\n"
            f"\n"
            f"  Earnings\n"
            f"    {'Blackjack:':<28} {self.blackjack_earnings:>+10,} chips\n"
            f"    {'Video Poker:':<28} {self.videopoker_earnings:>+10,} chips\n"
            f"    {'War:':<28} {self.war_earnings:>+10,} chips\n"
            f"    {'-' * 42}\n"
            f"    {'Total Earnings:':<28} {total_earnings:>+10,} chips"
        )

    def place_bet(self):

        Util.banner("PLACE BET", 45)

        print(f"  Player:          {self.name}")
        print(f"  Available Chips: {self.chips}")
        print()

        bet = Util.ask_int(
            "  Enter your bet: ",
            minimum=1,
            maximum=self.chips
        )

        # Reset first: wager() adds to bet, and last round's bet is still there
        self.bet = 0
        self.wager(bet)