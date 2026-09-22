# Player
class Player:

    def __init__(self, name, chips=100):
        self.name = name
        self.chips = chips
        self.total_bet = 0
        self.bet = 0
        self.starting_amount = chips
        self.funds_added = 0
        self.poker_earnings = 0
        self.blackjack_earnings = 0
        self.war_earnings = 0
        
        # Track whether the player is activly playing
        self.playing = True
        
        
    def get_starting_amount(self):
        return self.starting_amount
    
    # Understood to mean get a card
    def hit(self, deck):
        card = deck.deal_card()
        self.hand.add_card(card)
        return card
    
    def get_player_info(self):
        total_earnings = (
            self.blackjack_earnings
            + self.poker_earnings
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
            f"    {'Poker:':<28} {self.poker_earnings:>+10,} chips\n"
            f"    {'War:':<28} {self.war_earnings:>+10,} chips\n"
            f"    {'-' * 42}\n"
            f"    {'Total Earnings:':<28} {total_earnings:>+10,} chips"
        )


    def place_bet(self):

        while True:
            print()
            print("=" * 45)
            print("            PLACE BET")
            print("=" * 45)
            print()
            print(f"  Player:          {self.name}")
            print(f"  Available Chips: {self.chips}")
            print()

            try:
                bet = int(input("  Enter your bet: "))

                if bet <= 0:
                    print()
                    print("  ERROR: Bet must be greater than 0.")

                elif bet > self.chips:
                    print()
                    print("  ERROR: You don't have enough chips.")

                else:
                    self.chips -= bet
                    self.bet = bet
                    self.total_bet += bet
                    break

            except ValueError:
                print()
                print("  ERROR: Please enter a valid number.")