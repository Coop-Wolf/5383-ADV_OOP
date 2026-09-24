from ..game import Game
from ..deck import Deck
from ..util import Util
from .videopokerhand import VideoPokerHand
from .videopokerplayer import VideoPokerPlayer


class VideoPoker(Game):

    name = "VideoPoker"
    player_class = VideoPokerPlayer
    min_players = 1

    # Jacks or Better. Values are "X for 1": total chips returned per chip bet.
    # Keys must match the hand names VideoPokerHand.evaluate() returns.
    PAYTABLE = {
        "Royal Flush": 250,
        "Straight Flush": 50,
        "Four of a Kind": 25,
        "Full House": 9,
        "Flush": 6,
        "Straight": 4,
        "Three of a Kind": 3,
        "Two Pair": 2,
        "Pair": 1,          # only pays for jacks or better (see score_hand)
    }

    welcome_sections = [
        ("Goal", "Make the best five-card poker hand you can from a single draw."),
        ("How to Play", [
            "Place your bet and receive five cards.",
            "Choose which cards to hold by number, for example 1 3 5.",
            "Every card you don't hold is replaced once.",
            "Your final hand is paid according to the paytable.",
        ]),
        ("Paytable (pays X for 1)",
            [f"{hand_name} - {pays}" for hand_name, pays in PAYTABLE.items()]
            + ["A pair only pays if it is jacks or better."]
        ),
    ]
    
    
    def __init__(self, player):

        # Game expects a list, so wrap the single player
        super().__init__([player])
        self.video_player = self.game_players[0]
    

    def play_round(self):

        player = self.video_player

        self.deck = Deck()

        Util.clear_screen()
        player.place_bet()

        # Deal five cards
        player.hand = VideoPokerHand()
        for _ in range(5):
            player.hit(self.deck)

        # Hold, then draw once
        self.redraw(player=player)
        held = player.choose_holds()
        player.draw_replacements(self.deck, held)

        # Show the final hand and pay it
        self.redraw(player=player)
        self.determine_winner(player)

        input("\n  Press Enter to continue...")

    def show_table(self, player):

        Util.banner("VIDEO POKER")

        print(f"  {player.name}    Bet: {player.bet}    Chips: {player.chips}")
        print()
        print("  YOUR HAND")
        print("  " + "-" * 44)

        for number, card in enumerate(player.hand.cards, start=1):
            print(f"    {number}. {card}")

        print()
        print("=" * 50)

    def determine_winner(self, player):

        hand_name, pays = self.score_hand(player.hand)
        bet = player.bet

        Util.banner("ROUND RESULTS")

        print(f"  {player.name}")
        print(f"    Hand:   {player.hand}")
        print(f"    Bet:    {bet} chips")

        if pays == 0:
            self.settle(player, bet, "loss", f"{hand_name} does not pay")

        elif pays == 1:
            self.settle(player, bet, "push", "Jacks or better")

        else:
            self.settle(
                player, bet, "win",
                f"{hand_name} pays {pays} for 1",
                multiplier=pays - 1
            )

        print("=" * 50)

    # Returns (hand_name, pays); pays == 0 means the hand doesn't pay
    def score_hand(self, hand):

        hand_rank, hand_name = hand.evaluate()

        pays = self.PAYTABLE.get(hand_name, 0)

        # Only a pair of jacks or better pays
        if hand_name == "Pair" and not hand.is_jacks_or_better():
            pays = 0

        return hand_name, pays