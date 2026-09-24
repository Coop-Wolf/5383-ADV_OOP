from ..player import Player
from .videopokerhand import VideoPokerHand


class VideoPokerPlayer(Player):

    def __init__(self, name, chips=100):
        super().__init__(name, chips)
        self.hand = VideoPokerHand()

    # Returns the set of card positions (0-4) the player wants to keep
    def choose_holds(self):

        while True:
            raw = input(
                "\n  Cards to hold (e.g. 1 3 5), or Enter to replace all: "
            )

            cleaned = raw.replace(",", "").replace(" ", "")

            if cleaned == "":
                return set()

            if any(char not in "12345" for char in cleaned):
                print("  ERROR: Enter card numbers 1-5, like 1 3 5.")
                continue

            return {int(char) - 1 for char in cleaned}

    # Keep the held cards and replace the rest, once
    def draw_replacements(self, deck, held):

        new_hand = VideoPokerHand()

        for index, card in enumerate(self.hand.cards):
            if index in held:
                new_hand.add_card(card)
            else:
                new_hand.add_card(deck.deal_card())

        self.hand = new_hand