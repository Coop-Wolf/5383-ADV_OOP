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
 
    # stats comes from Database.get_stats()
    def get_player_info(self, stats):
        rows = ""
        for game, label in self.GAME_LABELS.items():
            s = stats[game]
            rows += (
                f"    {label:<12}{s['rounds_played']:>5}{s['wins']:>5}"
                f"{s['losses']:>5}{s['biggest_win']:>8,}{s['net_profit']:>+9,}\n"
            )
 
        all_stats = [stats[game] for game in self.GAME_LABELS]
        total_rounds = sum(s["rounds_played"] for s in all_stats)
        total_wins = sum(s["wins"] for s in all_stats)
        total_losses = sum(s["losses"] for s in all_stats)
        best_win = max(s["biggest_win"] for s in all_stats)
        total_net = sum(s["net_profit"] for s in all_stats)
 
        return (
            f"  {self.name.upper()}\n"
            f"  {'-' * 48}\n"
            f"  {'Session Start:':<30} {self.starting_amount:>10,} chips\n"
            f"  {'Funds Added (this session):':<30} {self.funds_added:>10,} chips\n"
            f"  {'Current Chips:':<30} {self.chips:>10,} chips\n"
            f"\n"
            f"  Lifetime Stats\n"
            f"    {'Game':<12}{'Rnds':>5}{'W':>5}{'L':>5}{'Best':>8}{'Net':>9}\n"
            f"    {'-' * 44}\n"
            f"{rows}"
            f"    {'-' * 44}\n"
            f"    {'Total':<12}{total_rounds:>5}{total_wins:>5}{total_losses:>5}"
            f"{best_win:>8,}{total_net:>+9,}"
        )