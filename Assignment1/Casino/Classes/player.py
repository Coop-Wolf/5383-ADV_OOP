# Player
class Player:

    def __init__(self, name, chips=100):
        self.name = name
        self.chips = chips
        self.total_bet = 0
        self.bet = 0
        self.starting_amount = chips
        
    def get_starting_amount(self):
        return self.starting_amount
    
    # Understood to mean get a card (Used in both poker and blackjack)
    def hit(self, deck):
        card = deck.deal_card()
        self.hand.add_card(card)
        return card
    
    def get_player_info(self):
        return f"{self.name:<20} {self.chips:>6} chips"

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