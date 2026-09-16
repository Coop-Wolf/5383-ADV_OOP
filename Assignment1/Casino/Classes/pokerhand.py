from .hand import Hand


class PokerHand(Hand):

    def evaluate(self, community_cards):
        all_cards = self.cards + community_cards

        if len(all_cards) < 5:
            return 0, "Incomplete"

        ranks = [card.rank for card in all_cards]
        suits = [card.suit for card in all_cards]

        rank_counts = {}

        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1

        counts = sorted(rank_counts.values(), reverse=True)

        is_flush = len(set(suits)) == 1

        if counts[0] >= 4:
            return 8, "Four of a Kind"

        if counts[0] >= 3 and counts[1] >= 2:
            return 7, "Full House"

        if is_flush:
            return 6, "Flush"

        if counts[0] >= 3:
            return 4, "Three of a Kind"

        if counts[0] >= 2 and counts[1] >= 2:
            return 3, "Two Pair"

        if counts[0] >= 2:
            return 2, "Pair"

        return 1, "High Card"