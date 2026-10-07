import pygame

from UI.constants import (
    DARK_GREEN,
    WHITE,
    BLACK,
    LIGHT_GRAY,
    GOLD,
)


CARD_W, CARD_H = 120, 170

CARD_RED = (200, 30, 30)

CARD_BACK = (30, 60, 150)
CARD_BACK_LIGHT = (90, 130, 220)

RANK_LABELS = {
    "Jack": "J",
    "Queen": "Q",
    "King": "K",
    "Ace": "A",
}


def draw_suit(surface, suit, center, s, color):

    cx, cy = center

    # Diamond
    if suit == "Diamonds":

        pygame.draw.polygon(
            surface,
            color,
            [
                (cx, cy - s),
                (cx + 0.7 * s, cy),
                (cx, cy + s),
                (cx - 0.7 * s, cy),
            ],
        )

    # Heart
    elif suit == "Hearts":

        r = int(0.52 * s)

        pygame.draw.circle(
            surface,
            color,
            (
                int(cx - 0.48 * s),
                int(cy - 0.28 * s),
            ),
            r,
        )

        pygame.draw.circle(
            surface,
            color,
            (
                int(cx + 0.48 * s),
                int(cy - 0.28 * s),
            ),
            r,
        )

        pygame.draw.polygon(
            surface,
            color,
            [
                (cx - 0.98 * s, cy - 0.12 * s),
                (cx + 0.98 * s, cy - 0.12 * s),
                (cx, cy + 0.95 * s),
            ],
        )

    # Spade
    elif suit == "Spades":

        r = int(0.52 * s)

        pygame.draw.circle(
            surface,
            color,
            (
                int(cx - 0.48 * s),
                int(cy + 0.2 * s),
            ),
            r,
        )

        pygame.draw.circle(
            surface,
            color,
            (
                int(cx + 0.48 * s),
                int(cy + 0.2 * s),
            ),
            r,
        )

        pygame.draw.polygon(
            surface,
            color,
            [
                (cx - 0.98 * s, cy + 0.05 * s),
                (cx + 0.98 * s, cy + 0.05 * s),
                (cx, cy - 0.95 * s),
            ],
        )

        pygame.draw.polygon(
            surface,
            color,
            [
                (cx, cy + 0.2 * s),
                (cx - 0.3 * s, cy + 0.95 * s),
                (cx + 0.3 * s, cy + 0.95 * s),
            ],
        )

    # Clubs
    else:

        r = int(0.4 * s)

        pygame.draw.circle(
            surface,
            color,
            (
                int(cx),
                int(cy - 0.5 * s),
            ),
            r,
        )

        pygame.draw.circle(
            surface,
            color,
            (
                int(cx - 0.5 * s),
                int(cy + 0.2 * s),
            ),
            r,
        )

        pygame.draw.circle(
            surface,
            color,
            (
                int(cx + 0.5 * s),
                int(cy + 0.2 * s),
            ),
            r,
        )

        pygame.draw.polygon(
            surface,
            color,
            [
                (cx, cy + 0.1 * s),
                (cx - 0.3 * s, cy + 0.95 * s),
                (cx + 0.3 * s, cy + 0.95 * s),
            ],
        )


def draw_card(
    surface,
    center,
    card,
    face_up,
    font,
    selected=False,
):

    rect = pygame.Rect(
        0,
        0,
        CARD_W,
        CARD_H,
    )

    rect.center = center

    # Shadow
    pygame.draw.rect(
        surface,
        DARK_GREEN,
        rect.move(3, 4),
        border_radius=10,
    )

    # Card back
    if not face_up:

        pygame.draw.rect(
            surface,
            CARD_BACK,
            rect,
            border_radius=10,
        )

        pygame.draw.rect(
            surface,
            WHITE,
            rect,
            width=3,
            border_radius=10,
        )

        inner = rect.inflate(
            -24,
            -24,
        )

        pygame.draw.rect(
            surface,
            CARD_BACK_LIGHT,
            inner,
            width=2,
            border_radius=6,
        )

        cx, cy = rect.center

        pygame.draw.polygon(
            surface,
            CARD_BACK_LIGHT,
            [
                (cx, inner.top + 10),
                (inner.right - 10, cy),
                (cx, inner.bottom - 10),
                (inner.left + 10, cy),
            ],
            width=2,
        )

        return rect

    # Card color
    color = (
        CARD_RED
        if card.suit in ("Hearts", "Diamonds")
        else BLACK
    )

    # Card
    pygame.draw.rect(
        surface,
        WHITE,
        rect,
        border_radius=10,
    )

    pygame.draw.rect(
        surface,
        LIGHT_GRAY,
        rect,
        width=2,
        border_radius=10,
    )

    # Rank
    rank = RANK_LABELS.get(
        card.rank,
        card.rank,
    )

    label = font.render(
        rank,
        True,
        color,
    )

    surface.blit(
        label,
        (
            rect.x + 10,
            rect.y + 8,
        ),
    )

    # Small suit
    draw_suit(
        surface,
        card.suit,
        (
            rect.x
            + 10
            + label.get_width() // 2,

            rect.y
            + 8
            + label.get_height()
            + 12,
        ),
        9,
        color,
    )

    # Large center suit
    draw_suit(
        surface,
        card.suit,
        (
            rect.centerx,
            rect.centery + 8,
        ),
        32,
        color,
    )

    # Gold border for a held card
    if selected:

        pygame.draw.rect(
            surface,
            GOLD,
            rect.inflate(10, 10),
            width=4,
            border_radius=12,
        )

    return rect


def draw_hand(
    surface,
    cards,
    center,
    font,
    hidden=(),
    offset=40,
    selected=(),
):

    count = len(cards)

    total_w = (
        CARD_W
        + max(count - 1, 0) * offset
    )

    left = (
        center[0]
        - total_w // 2
    )

    for i, card in enumerate(cards):

        x = (
            left
            + CARD_W // 2
            + i * offset
        )

        draw_card(
            surface,
            (x, center[1]),
            card,
            i not in hidden,
            font,
            selected=i in selected,
        )

    return pygame.Rect(
        left,
        center[1] - CARD_H // 2,
        total_w,
        CARD_H,
    )