from ..game import Game
from ..deck import Deck
from .videopokerhand import VideoPokerHand
from .videopokerplayer import VideoPokerPlayer


class VideoPoker(Game):

    name = "VideoPoker"
    player_class = VideoPokerPlayer

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

    def __init__(self, player, db=None):
        super().__init__(player, db=db)
        self.video_player = self.game_player

    def play_round(self):

        player = self.video_player

        self.deck = Deck()

        self.collect_bet(player)

        # Deal five cards
        player.hand = VideoPokerHand()
        for _ in range(5):
            player.hit(self.deck)

        # Hold, then draw once
        self.redraw(player=player)
        held = self.ui.ask_holds()
        player.draw_replacements(self.deck, held)

        # Show the final hand and pay it
        self.redraw(player=player)
        self.determine_winner(player)


    def determine_winner(self, player):

        hand_name, pays = self.score_hand(player.hand)
        bet = player.bet

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


    # Returns (hand_name, pays); pays == 0 means the hand doesn't pay
    def score_hand(self, hand):

        hand_rank, hand_name = hand.evaluate()

        pays = self.PAYTABLE.get(hand_name, 0)

        # Only a pair of jacks or better pays
        if hand_name == "Pair" and not hand.is_jacks_or_better():
            pays = 0

        return hand_name, pays