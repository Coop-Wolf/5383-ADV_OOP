from ..hand import Hand


class PokerHand(Hand):

    def get_poker_value(self, rank):
        values = {
            "Jack": 11,
            "Queen": 12,
            "King": 13,
            "Ace": 14
        }

        if rank in values:
            return values[rank]

        return int(rank)

    def evaluate(self, community_cards):
        all_cards = self.cards + community_cards

        if len(all_cards) < 5:
            return (0,), "Incomplete"

        ranks = [
            self.get_poker_value(card.rank)
            for card in all_cards
        ]

        suits = [card.suit for card in all_cards]

        rank_counts = {}

        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1

        counts = sorted(rank_counts.values(), reverse=True)

        is_flush = len(set(suits)) == 1

        # Four of a Kind
        if counts[0] >= 4:
            four_rank = max(
                rank for rank in rank_counts
                if rank_counts[rank] >= 4
            )

            return (8, four_rank), "Four of a Kind"

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
        if is_flush:
            return (6, *sorted(ranks, reverse=True)), "Flush"

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
                if rank not in pairs
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