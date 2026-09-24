from ..hand import Hand


class VideoPokerHand(Hand):

    # High card of the best straight in these ranks, or None.
    # An ace can also play low (A-2-3-4-5).
    def find_straight(self, ranks):
        unique = set(ranks)

        if 14 in unique:
            unique.add(1)

        for high in range(14, 4, -1):
            if all(value in unique for value in range(high - 4, high + 1)):
                return high

        return None

    # Ranks of the cards in a flush (five or more of one suit), or None
    def find_flush(self, cards):
        by_suit = {}

        for card in cards:
            by_suit.setdefault(card.suit, []).append(card.get_poker_value())

        for suit_ranks in by_suit.values():
            if len(suit_ranks) >= 5:
                return suit_ranks

        return None

    # True if the hand has a pair of jacks or better
    def is_jacks_or_better(self):
        counts = {}

        for card in self.cards:
            value = card.get_poker_value()
            counts[value] = counts.get(value, 0) + 1

        return any(
            value >= 11 and count >= 2
            for value, count in counts.items()
        )

    def evaluate(self):
        all_cards = self.cards

        if len(all_cards) < 5:
            return (0,), "Incomplete"

        ranks = [card.get_poker_value() for card in all_cards]

        rank_counts = {}

        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1

        counts = sorted(rank_counts.values(), reverse=True)

        flush_ranks = self.find_flush(all_cards)
        straight_high = self.find_straight(ranks)

        # Straight flush: a straight made only of the flush suit's cards
        if flush_ranks:
            straight_flush_high = self.find_straight(flush_ranks)

            if straight_flush_high == 14:
                return (10,), "Royal Flush"

            if straight_flush_high:
                return (9, straight_flush_high), "Straight Flush"

        # Four of a Kind
        if counts[0] >= 4:
            four_rank = max(
                rank for rank in rank_counts
                if rank_counts[rank] >= 4
            )

            kicker = max(rank for rank in ranks if rank != four_rank)

            return (8, four_rank, kicker), "Four of a Kind"

        # Full House
        if counts[0] >= 3 and counts[1] >= 2:
            three_rank = max(
                rank for rank in rank_counts
                if rank_counts[rank] >= 3
            )

            pair_rank = max(
                rank for rank in rank_counts
                if rank_counts[rank] >= 2
                and rank != three_rank
            )

            return (7, three_rank, pair_rank), "Full House"

        # Flush
        if flush_ranks:
            return (6, *sorted(flush_ranks, reverse=True)[:5]), "Flush"

        # Straight
        if straight_high:
            return (5, straight_high), "Straight"

        # Three of a Kind
        if counts[0] >= 3:
            three_rank = max(
                rank for rank in rank_counts
                if rank_counts[rank] >= 3
            )

            kickers = sorted(
                [rank for rank in ranks if rank != three_rank],
                reverse=True
            )

            return (4, three_rank, *kickers[:2]), "Three of a Kind"

        # Two Pair
        if counts[0] >= 2 and counts[1] >= 2:
            pairs = sorted(
                [
                    rank for rank in rank_counts
                    if rank_counts[rank] >= 2
                ],
                reverse=True
            )

            kicker = max(
                rank for rank in ranks
                if rank not in pairs[:2]
            )

            return (3, pairs[0], pairs[1], kicker), "Two Pair"

        # Pair
        if counts[0] >= 2:
            pair_rank = max(
                rank for rank in rank_counts
                if rank_counts[rank] >= 2
            )

            kickers = sorted(
                [
                    rank for rank in ranks
                    if rank != pair_rank
                ],
                reverse=True
            )

            return (2, pair_rank, *kickers[:3]), "Pair"

        # High Card
        sorted_ranks = sorted(ranks, reverse=True)

        return (1, *sorted_ranks[:5]), "High Card"