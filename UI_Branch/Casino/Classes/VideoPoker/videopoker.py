from ..game import Game
from ..deck import Deck
from .videopokerhand import VideoPokerHand
from .videopokerplayer import VideoPokerPlayer


class VideoPoker(Game):

    name = "VideoPoker"
    player_class = VideoPokerPlayer

    # Jacks or Better.
    # Values are "X for 1":
    # total chips returned per chip bet.
    PAYTABLE = {
        "Royal Flush": 250,
        "Straight Flush": 50,
        "Four of a Kind": 25,
        "Full House": 9,
        "Flush": 6,
        "Straight": 4,
        "Three of a Kind": 3,
        "Two Pair": 2,
        "Pair": 1,
    }

    def __init__(self, player, db=None):
        super().__init__(player, db=db)
        self.video_player = self.game_player
        self.deck = None
        self.hand_name = None
        self.payout = 0
        self.net_change = 0

    def deal(self, bet):
        """Start a Video Poker round and deal five cards."""

        self.deck = Deck()

        player = self.video_player

        self.collect_bet(player, bet)

        player.hand = VideoPokerHand()

        for _ in range(5):
            player.hit(self.deck)

    def draw(self, held):
        """
        Replace all cards that were not held.

        held is a collection of card indexes.
        """

        if self.deck is None:
            raise RuntimeError("A hand must be dealt before drawing.")

        self.video_player.draw_replacements(
            self.deck,
            held
        )

    def determine_winner(self):
        """Evaluate the final hand and settle the player's bet."""

        player = self.video_player

        hand_name, pays = self.score_hand(player.hand)

        self.hand_name = hand_name
        self.payout = pays

        bet = player.bet

        if pays == 0:
            self.net_change = self.settle(
                player,
                bet,
                "loss"
            )

        elif pays == 1:
            self.net_change = self.settle(
                player,
                bet,
                "push"
            )

        else:
            self.net_change = self.settle(
                player,
                bet,
                "win",
                multiplier=pays - 1
            )

        return hand_name, pays

    def score_hand(self, hand):
        """
        Return (hand_name, payout).

        A normal pair does not pay.
        Only Jacks or Better pays for a pair.
        """

        hand_rank, hand_name = hand.evaluate()

        pays = self.PAYTABLE.get(hand_name, 0)

        if hand_name == "Pair" and not hand.is_jacks_or_better():
            pays = 0

        return hand_name, pays