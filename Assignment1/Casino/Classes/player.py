# Player
class Player:

    def __init__(self, name, chips=100):
        self.name = name
        self.chips = chips
        self.bet = 0
        self.starting_amount = chips
        
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