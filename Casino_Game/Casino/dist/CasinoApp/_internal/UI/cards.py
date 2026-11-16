import math
import pygame
from UI.constants import DARK_GREEN, WHITE, BLACK, LIGHT_GRAY, GOLD

CARD_W, CARD_H = 120, 170
CARD_RED = (215, 35, 45)
CARD_BLACK = (30, 32, 38)
CARD_BACK = (28, 48, 115)
CARD_BACK_ACCENT = (70, 105, 195)
CARD_BACK_GOLD = (215, 175, 75)

RANK_LABELS = {"Jack": "J", "Queen": "Q", "King": "K", "Ace": "A"}


def _supersample_draw(surface, cx, cy, w, h, draw_fn):
    """Render at 2x resolution and scale down with smoothscale to eliminate jagged lines."""
    scale = 2
    pad = 8
    sw, sh = int(w * scale + pad * 2), int(h * scale + pad * 2)
    sub = pygame.Surface((sw, sh), pygame.SRCALPHA)

    sub_cx = sw // 2
    sub_cy = sh // 2
    draw_fn(sub, sub_cx, sub_cy, scale)

    downscaled = pygame.transform.smoothscale(sub, (sw // scale, sh // scale))
    surface.blit(downscaled, (cx - downscaled.get_width() // 2, cy - downscaled.get_height() // 2))


def draw_suit(surface, suit, center, s, color):
    """Draw a smooth, anti-aliased card suit pip centered at (cx, cy)."""
    cx, cy = center

    def _draw(surf, x, y, k):
        sk = s * k

        if suit == "Diamonds":
            pts = [
                (x, y - 1.05 * sk),
                (x + 0.72 * sk, y),
                (x, y + 1.05 * sk),
                (x - 0.72 * sk, y),
            ]
            pygame.draw.polygon(surf, color, pts)

        elif suit == "Hearts":
            # Smooth curved heart lobes using overlapping circles and polygon base
            r = sk * 0.46
            pygame.draw.circle(surf, color, (x - 0.42 * sk, y - 0.28 * sk), r)
            pygame.draw.circle(surf, color, (x + 0.42 * sk, y - 0.28 * sk), r)
            body = [
                (x - 0.88 * sk, y - 0.16 * sk),
                (x + 0.88 * sk, y - 0.16 * sk),
                (x, y + 0.98 * sk),
            ]
            pygame.draw.polygon(surf, color, body)

        elif suit == "Spades":
            # Inverted heart body with curved flare base
            r = sk * 0.46
            pygame.draw.circle(surf, color, (x - 0.42 * sk, y + 0.18 * sk), r)
            pygame.draw.circle(surf, color, (x + 0.42 * sk, y + 0.18 * sk), r)
            body = [
                (x - 0.88 * sk, y + 0.08 * sk),
                (x + 0.88 * sk, y + 0.08 * sk),
                (x, y - 0.98 * sk),
            ]
            pygame.draw.polygon(surf, color, body)
            # Flared pedestal stem
            stem = [
                (x, y + 0.10 * sk),
                (x - 0.40 * sk, y + 0.95 * sk),
                (x + 0.40 * sk, y + 0.95 * sk),
            ]
            pygame.draw.polygon(surf, color, stem)

        elif suit == "Clubs":
            # Three-clover cluster with triangular flared stem
            r = sk * 0.42
            pygame.draw.circle(surf, color, (x, y - 0.45 * sk), r)
            pygame.draw.circle(surf, color, (x - 0.45 * sk, y + 0.12 * sk), r)
            pygame.draw.circle(surf, color, (x + 0.45 * sk, y + 0.12 * sk), r)
            pygame.draw.circle(surf, color, (x, y - 0.05 * sk), r * 0.85)
            # Pedestal stem
            stem = [
                (x, y - 0.05 * sk),
                (x - 0.38 * sk, y + 0.95 * sk),
                (x + 0.38 * sk, y + 0.95 * sk),
            ]
            pygame.draw.polygon(surf, color, stem)

    _supersample_draw(surface, cx, cy, s * 2.5, s * 2.5, _draw)


def _draw_card_back(surface, rect):
    """Render a classic patterned casino card back with a beveled border."""
    pygame.draw.rect(surface, CARD_BACK, rect, border_radius=10)
    pygame.draw.rect(surface, (230, 235, 245), rect, width=2, border_radius=10)

    inner = rect.inflate(-16, -16)
    pygame.draw.rect(surface, (20, 35, 85), inner, border_radius=6)
    pygame.draw.rect(surface, CARD_BACK_GOLD, inner, width=2, border_radius=6)

    # Repeating diagonal lattice pattern
    old_clip = surface.get_clip()
    surface.set_clip(inner)

    grid_spacing = 14
    for offset in range(-inner.h, inner.w + inner.h, grid_spacing):
        p1 = (inner.left + offset, inner.top)
        p2 = (inner.left + offset + inner.h, inner.bottom)
        pygame.draw.line(surface, CARD_BACK_ACCENT, p1, p2, 1)

        p3 = (inner.left + offset, inner.bottom)
        p4 = (inner.left + offset + inner.h, inner.top)
        pygame.draw.line(surface, CARD_BACK_ACCENT, p3, p4, 1)

    surface.set_clip(old_clip)

    # Center medallion diamond
    cx, cy = rect.center
    m_pts = [(cx, cy - 24), (cx + 20, cy), (cx, cy + 24), (cx - 20, cy)]
    pygame.draw.polygon(surface, CARD_BACK, m_pts)
    pygame.draw.polygon(surface, CARD_BACK_GOLD, m_pts, 2)
    pygame.draw.circle(surface, CARD_BACK_GOLD, (cx, cy), 5)


def draw_card(surface, center, card, face_up, font, selected=False):
    rect = pygame.Rect(0, 0, CARD_W, CARD_H)
    rect.center = center

    # 1. Soft Alpha Drop Shadow
    shadow_surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 65), (0, 0, CARD_W, CARD_H), border_radius=10)
    surface.blit(shadow_surf, rect.move(3, 4))

    # 2. Card Back
    if not face_up:
        _draw_card_back(surface, rect)
        return rect

    # 3. Card Face
    color = CARD_RED if card.suit in ("Hearts", "Diamonds") else CARD_BLACK

    # Warm white card face
    pygame.draw.rect(surface, (252, 252, 250), rect, border_radius=10)
    pygame.draw.rect(surface, (215, 218, 225), rect, width=1, border_radius=10)

    rank = RANK_LABELS.get(card.rank, str(card.rank))
    label = font.render(rank, True, color)

    # Top-Left Index (Rank + Mini Pip)
    surface.blit(label, (rect.x + 8, rect.y + 6))
    draw_suit(surface, card.suit, (rect.x + 8 + label.get_width() // 2, rect.y + 12 + label.get_height()), 7, color)

    # Bottom-Right Inverted Index
    rot_label = pygame.transform.rotate(label, 180)
    surface.blit(rot_label, (rect.right - 8 - rot_label.get_width(), rect.bottom - 6 - rot_label.get_height()))
    draw_suit(surface, card.suit, (rect.right - 8 - rot_label.get_width() // 2, rect.bottom - 12 - rot_label.get_height()), 7, color)

    # Center Hero Suit Pip
    draw_suit(surface, card.suit, (rect.centerx, rect.centery), 30, color)

    # 4. Selection Highlight
    if selected:
        pygame.draw.rect(surface, GOLD, rect.inflate(8, 8), width=3, border_radius=12)

    return rect


def draw_hand(surface, cards, center, font, hidden=(), offset=40, selected=()):
    count = len(cards)
    total_w = CARD_W + max(count - 1, 0) * offset
    left = center[0] - total_w // 2

    for i, card in enumerate(cards):
        x = left + CARD_W // 2 + i * offset
        draw_card(surface, (x, center[1]), card, i not in hidden, font, selected=i in selected)

    return pygame.Rect(left, center[1] - CARD_H // 2, total_w, CARD_H)