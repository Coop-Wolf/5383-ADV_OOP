from .person import Person

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