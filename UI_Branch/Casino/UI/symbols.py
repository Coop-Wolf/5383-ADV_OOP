"""
 
Slot symbols for the Casino App, drawn with pygame shapes (no image files).
 
    draw_symbol(surface, name, rect):       Draw one symbol centered in rect.
    draw_mine_cart(surface, rect, gold):    Draw a mine cart (also used by the Gold Rush bonus).
    get_font(size, bold):                   Cached font, same font as the rest of the app.
 
    To add a symbol for a new machine, write a function(surface, cx, cy, s) and add
    it to DRAWERS. (cx, cy) is the center and s is a size unit, about a third of the
    cell height, so a symbol roughly spans from -1 to +1 in s units.
 
"""
 
import math
import pygame
from functools import lru_cache
from UI.constants import GOLD, WHITE, FONT_NAME
 
DARK = (15, 15, 15)
REEL_BG = (245, 240, 225)
 
 
@lru_cache(maxsize=None)
def get_font(size, bold=False):
    font = pygame.font.Font(FONT_NAME, size)
    font.set_bold(bold)
    return font
 
 
# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------
 
def _star(cx, cy, r_outer, r_inner, points=5):
    """Corner points of a star with one point straight up."""
    pts = []
    for i in range(points * 2):
        angle = -math.pi / 2 + i * math.pi / points
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts
 
 
def _arc_poly(cx, cy, r_outer, r_inner, start_deg, end_deg, steps=28):
    """A thick arc as a filled polygon (angles in degrees, 0 = right, 90 = up)."""
    outer, inner = [], []
    for i in range(steps + 1):
        a = math.radians(start_deg + (end_deg - start_deg) * i / steps)
        outer.append((cx + r_outer * math.cos(a), cy - r_outer * math.sin(a)))
        inner.append((cx + r_inner * math.cos(a), cy - r_inner * math.sin(a)))
    return outer + inner[::-1]
 
 
def _outlined_text(surface, text, size, center, color, outline=DARK):
    font = get_font(size, True)
    img = font.render(text, True, color)
    shadow = font.render(text, True, outline)
    rect = img.get_rect(center=center)
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        surface.blit(shadow, rect.move(dx, dy))
    surface.blit(img, rect)
 
 
# --------------------------------------------------------------------------
# Classic Fruit
# --------------------------------------------------------------------------
 
def _cherry(surface, cx, cy, s):
    pygame.draw.line(surface, (40, 120, 40), (cx - s * 0.45, cy + s * 0.2), (cx + s * 0.1, cy - s * 0.9), 4)
    pygame.draw.line(surface, (40, 120, 40), (cx + s * 0.45, cy + s * 0.2), (cx + s * 0.1, cy - s * 0.9), 4)
    pygame.draw.circle(surface, (200, 40, 40), (cx - s * 0.45, cy + s * 0.4), s * 0.5)
    pygame.draw.circle(surface, (200, 40, 40), (cx + s * 0.45, cy + s * 0.4), s * 0.5)
    pygame.draw.circle(surface, (255, 150, 150), (cx - s * 0.6, cy + s * 0.25), s * 0.12)
    pygame.draw.circle(surface, (255, 150, 150), (cx + s * 0.3, cy + s * 0.25), s * 0.12)
 
 
def _lemon(surface, cx, cy, s):
    body = pygame.Rect(0, 0, int(s * 1.9), int(s * 1.25))
    body.center = (cx, cy)
    pygame.draw.ellipse(surface, (250, 225, 50), body)
    pygame.draw.ellipse(surface, (200, 170, 20), body, 3)
 
 
def _bar(surface, cx, cy, s):
    body = pygame.Rect(0, 0, int(s * 1.95), int(s * 1.0))
    body.center = (cx, cy)
    pygame.draw.rect(surface, DARK, body, border_radius=8)
    pygame.draw.rect(surface, GOLD, body, 3, border_radius=8)
    label = get_font(int(s * 0.85), True).render("BAR", True, GOLD)
    surface.blit(label, label.get_rect(center=body.center))
 
 
def _bell(surface, cx, cy, s):
    pygame.draw.circle(surface, GOLD, (cx, cy - s * 0.15), s * 0.65)
    pygame.draw.polygon(surface, GOLD, [
        (cx - s * 0.65, cy - s * 0.15), (cx + s * 0.65, cy - s * 0.15),
        (cx + s * 0.95, cy + s * 0.5), (cx - s * 0.95, cy + s * 0.5)])
    pygame.draw.circle(surface, (160, 120, 20), (cx, cy + s * 0.68), s * 0.18)
    pygame.draw.polygon(surface, (160, 120, 20), [
        (cx - s * 0.95, cy + s * 0.5), (cx + s * 0.95, cy + s * 0.5),
        (cx + s * 0.95, cy + s * 0.55), (cx - s * 0.95, cy + s * 0.55)], 2)
 
 
def _seven(surface, cx, cy, s):
    _outlined_text(surface, "7", int(s * 2.6), (cx, cy), (200, 40, 40))
 
 
def _diamond(surface, cx, cy, s):
    pts = [(cx, cy - s), (cx + s * 0.85, cy), (cx, cy + s), (cx - s * 0.85, cy)]
    pygame.draw.polygon(surface, (90, 210, 245), pts)
    pygame.draw.polygon(surface, (30, 120, 170), pts, 3)
    pygame.draw.line(surface, (200, 245, 255), (cx - s * 0.85, cy), (cx + s * 0.85, cy), 2)
    pygame.draw.line(surface, (200, 245, 255), (cx, cy - s), (cx - s * 0.3, cy), 2)
    pygame.draw.line(surface, (200, 245, 255), (cx, cy - s), (cx + s * 0.3, cy), 2)
 
 
# --------------------------------------------------------------------------
# Wild West
# --------------------------------------------------------------------------
 
def _horseshoe(surface, cx, cy, s):
    silver, edge = (175, 180, 190), (85, 90, 100)
    cy = cy - s * 0.05
    pygame.draw.polygon(surface, silver, _arc_poly(cx, cy, s * 0.98, s * 0.5, 145, 395))
    pygame.draw.polygon(surface, edge, _arc_poly(cx, cy, s * 0.98, s * 0.5, 145, 395), 2)
    for deg in (190, 230, 270, 310, 350):
        a = math.radians(deg)
        r = s * 0.74
        pygame.draw.circle(surface, edge, (cx + r * math.cos(a), cy - r * math.sin(a)), max(2, s * 0.07))
 
 
def _boot(surface, cx, cy, s):
    leather, dark = (145, 88, 38), (65, 38, 14)
    outline = [(-0.45, -1.0), (0.2, -1.0), (0.2, 0.15), (0.95, 0.4), (0.95, 0.85), (-0.45, 0.85)]
    pts = [(cx + x * s, cy + y * s) for x, y in outline]
    pygame.draw.polygon(surface, leather, pts)
    pygame.draw.polygon(surface, dark, pts, 3)
    pygame.draw.rect(surface, dark, (cx - 0.45 * s, cy + 0.85 * s, 1.4 * s, 0.2 * s))
    pygame.draw.rect(surface, dark, (cx - 0.45 * s, cy + 0.85 * s, 0.4 * s, 0.35 * s))
    pygame.draw.rect(surface, (205, 145, 65), (cx - 0.45 * s, cy - 1.0 * s, 0.65 * s, 0.22 * s))
    pygame.draw.line(surface, dark, (cx - 0.2 * s, cy - 0.6 * s), (cx - 0.2 * s, cy + 0.05 * s), 2)
 
 
def _hat(surface, cx, cy, s):
    tan, dark = (205, 150, 75), (120, 75, 30)
    crown = pygame.Rect(0, 0, int(1.15 * s), int(1.15 * s))
    crown.midbottom = (cx, cy + 0.45 * s)
    pygame.draw.rect(surface, tan, crown, border_top_left_radius=int(0.4 * s), border_top_right_radius=int(0.4 * s))
    pygame.draw.rect(surface, dark, crown, 2, border_top_left_radius=int(0.4 * s), border_top_right_radius=int(0.4 * s))
    pygame.draw.line(surface, dark, (cx, crown.top + 2), (cx, crown.top + 0.35 * s), 2)
    band = pygame.Rect(crown.left, crown.bottom - int(0.45 * s), crown.w, int(0.22 * s))
    pygame.draw.rect(surface, (150, 40, 30), band)
    brim = pygame.Rect(0, 0, int(2.2 * s), int(0.6 * s))
    brim.center = (cx, cy + 0.5 * s)
    pygame.draw.ellipse(surface, tan, brim)
    pygame.draw.ellipse(surface, dark, brim, 2)
 
 
def _revolver(surface, cx, cy, s):
    steel, light, dark, wood = (105, 110, 120), (150, 155, 165), (40, 42, 48), (135, 82, 36)
    cy = cy - s * 0.1
    barrel = pygame.Rect(cx - 1.05 * s, cy - 0.5 * s, 1.4 * s, 0.34 * s)
    pygame.draw.rect(surface, steel, barrel, border_radius=3)
    pygame.draw.rect(surface, dark, barrel, 2, border_radius=3)
    body = pygame.Rect(cx - 0.25 * s, cy - 0.62 * s, 1.0 * s, 0.7 * s)
    pygame.draw.rect(surface, steel, body, border_radius=5)
    pygame.draw.rect(surface, dark, body, 2, border_radius=5)
    pygame.draw.circle(surface, light, (cx + 0.05 * s, cy - 0.27 * s), s * 0.3)
    pygame.draw.circle(surface, dark, (cx + 0.05 * s, cy - 0.27 * s), s * 0.3, 2)
    grip = [(cx + 0.45 * s, cy + 0.05 * s), (cx + 0.85 * s, cy + 0.05 * s),
            (cx + 0.8 * s, cy + 1.0 * s), (cx + 0.4 * s, cy + 0.85 * s)]
    pygame.draw.polygon(surface, wood, grip)
    pygame.draw.polygon(surface, dark, grip, 2)
    pygame.draw.arc(surface, dark, pygame.Rect(cx - 0.05 * s, cy - 0.1 * s, 0.6 * s, 0.6 * s), math.pi, 2 * math.pi, 3)
 
 
def _badge(surface, cx, cy, s):
    gold, edge = (255, 205, 60), (150, 105, 10)
    pts = _star(cx, cy + s * 0.05, s * 1.1, s * 0.52)
    pygame.draw.polygon(surface, gold, pts)
    pygame.draw.polygon(surface, edge, pts, 3)
    for i in range(0, 10, 2):
        pygame.draw.circle(surface, (255, 235, 150), pts[i], max(2, s * 0.12))
    pygame.draw.circle(surface, (215, 160, 25), (cx, cy + s * 0.05), s * 0.3)
    pygame.draw.circle(surface, edge, (cx, cy + s * 0.05), s * 0.3, 2)
 
 
def _outlaw(surface, cx, cy, s):
    """The wild: a masked bandit with a red bandana."""
    face = (240, 195, 150)
    pygame.draw.circle(surface, face, (cx, cy - s * 0.15), s * 0.85)
    pygame.draw.circle(surface, (150, 105, 70), (cx, cy - s * 0.15), s * 0.85, 2)
    mask = pygame.Rect(0, 0, int(1.75 * s), int(0.42 * s))
    mask.center = (cx, cy - s * 0.4)
    pygame.draw.ellipse(surface, DARK, mask)
    for dx in (-0.32, 0.32):
        pygame.draw.circle(surface, WHITE, (cx + dx * s, cy - s * 0.4), s * 0.12)
        pygame.draw.circle(surface, DARK, (cx + dx * s, cy - s * 0.4), s * 0.05)
    bandana = [(cx - 0.82 * s, cy - 0.02 * s), (cx + 0.82 * s, cy - 0.02 * s), (cx, cy + 1.0 * s)]
    pygame.draw.polygon(surface, (190, 30, 30), bandana)
    pygame.draw.polygon(surface, (110, 15, 15), bandana, 2)
    _outlined_text(surface, "WILD", int(s * 0.62), (cx, cy + s * 0.28), WHITE)
 
 
def _saloon(surface, cx, cy, s):
    """The free spins symbol: swinging saloon doors under a FREE banner."""
    wood, dark = (150, 95, 45), (75, 45, 18)
    for x in (cx - 0.95 * s, cx + 0.05 * s):
        door = pygame.Rect(int(x), int(cy - 0.35 * s), int(0.9 * s), int(1.3 * s))
        pygame.draw.rect(surface, wood, door, border_top_left_radius=int(0.3 * s), border_top_right_radius=int(0.3 * s))
        pygame.draw.rect(surface, dark, door, 2, border_top_left_radius=int(0.3 * s), border_top_right_radius=int(0.3 * s))
        for i in range(1, 5):
            y = door.top + i * door.h // 5
            pygame.draw.line(surface, dark, (door.left + 4, y), (door.right - 4, y), 2)
    banner = pygame.Rect(0, 0, int(2.1 * s), int(0.62 * s))
    banner.center = (cx, cy - 0.7 * s)
    pygame.draw.rect(surface, (180, 30, 30), banner, border_radius=5)
    pygame.draw.rect(surface, GOLD, banner, 2, border_radius=5)
    label = get_font(max(12, int(s * 0.55)), True).render("FREE", True, GOLD)
    surface.blit(label, label.get_rect(center=banner.center))
 
 
# --------------------------------------------------------------------------
# Gold Rush
# --------------------------------------------------------------------------
 
def _pickaxe(surface, cx, cy, s):
    wood, steel, dark = (140, 90, 40), (140, 145, 155), (50, 52, 58)
    pygame.draw.line(surface, wood, (cx - 0.65 * s, cy + 0.95 * s), (cx + 0.2 * s, cy - 0.7 * s), 7)
    head = [(cx - 0.75 * s, cy - 0.4 * s), (cx - 0.1 * s, cy - 0.95 * s), (cx + 0.6 * s, cy - 0.95 * s),
            (cx + 1.0 * s, cy - 0.45 * s), (cx + 0.85 * s, cy - 0.35 * s), (cx + 0.5 * s, cy - 0.65 * s),
            (cx - 0.05 * s, cy - 0.62 * s), (cx - 0.6 * s, cy - 0.25 * s)]
    pygame.draw.polygon(surface, steel, head)
    pygame.draw.polygon(surface, dark, head, 2)
 
 
def _lantern(surface, cx, cy, s):
    metal, glass, flame = (60, 60, 66), (255, 228, 135), (255, 140, 30)
    pygame.draw.arc(surface, metal, pygame.Rect(cx - 0.5 * s, cy - 1.2 * s, 1.0 * s, 0.9 * s), 0, math.pi, 3)
    cap = [(cx - 0.6 * s, cy - 0.5 * s), (cx + 0.6 * s, cy - 0.5 * s), (cx + 0.4 * s, cy - 0.8 * s), (cx - 0.4 * s, cy - 0.8 * s)]
    pygame.draw.polygon(surface, metal, cap)
    body = pygame.Rect(cx - 0.5 * s, cy - 0.5 * s, 1.0 * s, 1.15 * s)
    pygame.draw.rect(surface, glass, body)
    pygame.draw.rect(surface, metal, body, 3)
    pygame.draw.ellipse(surface, flame, pygame.Rect(cx - 0.2 * s, cy - 0.2 * s, 0.4 * s, 0.75 * s))
    pygame.draw.ellipse(surface, (255, 235, 110), pygame.Rect(cx - 0.09 * s, cy + 0.05 * s, 0.18 * s, 0.4 * s))
    pygame.draw.rect(surface, metal, (cx - 0.62 * s, cy + 0.62 * s, 1.24 * s, 0.26 * s), border_radius=3)
 
 
def _nugget(surface, cx, cy, s):
    gold, edge = (240, 190, 40), (145, 100, 10)
    outline = [(-0.95, 0.3), (-0.65, -0.4), (-0.1, -0.75), (0.5, -0.55), (1.0, 0.05), (0.75, 0.7), (0.0, 0.85), (-0.65, 0.75)]
    pts = [(cx + x * s, cy + y * s) for x, y in outline]
    pygame.draw.polygon(surface, gold, pts)
    pygame.draw.polygon(surface, edge, pts, 3)
    shine = [(cx - 0.5 * s, cy - 0.15 * s), (cx - 0.15 * s, cy - 0.5 * s), (cx + 0.25 * s, cy - 0.4 * s), (cx - 0.1 * s, cy)]
    pygame.draw.polygon(surface, (255, 238, 150), shine)
 
 
def _dynamite(surface, cx, cy, s):
    red, band, dark = (200, 40, 40), (235, 215, 165), (90, 20, 20)
    for dx in (-0.5, 0.0, 0.5):
        stick = pygame.Rect(cx + (dx - 0.25) * s, cy - 0.4 * s, 0.5 * s, 1.35 * s)
        pygame.draw.rect(surface, red, stick, border_radius=4)
        pygame.draw.rect(surface, dark, stick, 2, border_radius=4)
    for y in (0.0, 0.6):
        pygame.draw.rect(surface, band, (cx - 0.75 * s, cy + y * s, 1.5 * s, 0.2 * s))
    pygame.draw.lines(surface, (60, 50, 40), False,
                      [(cx, cy - 0.4 * s), (cx + 0.1 * s, cy - 0.65 * s), (cx + 0.4 * s, cy - 0.8 * s)], 3)
    pygame.draw.polygon(surface, (255, 200, 40), _star(cx + 0.45 * s, cy - 0.85 * s, 0.32 * s, 0.13 * s, 4))
 
 
def _gold_bar(surface, cx, cy, s):
    gold, top, edge = (230, 175, 30), (255, 225, 110), (140, 95, 10)
    front = [(cx - 0.95 * s, cy + 0.65 * s), (cx + 0.95 * s, cy + 0.65 * s), (cx + 0.7 * s, cy - 0.05 * s), (cx - 0.7 * s, cy - 0.05 * s)]
    face = [(cx - 0.7 * s, cy - 0.05 * s), (cx + 0.7 * s, cy - 0.05 * s), (cx + 0.45 * s, cy - 0.6 * s), (cx - 0.45 * s, cy - 0.6 * s)]
    pygame.draw.polygon(surface, gold, front)
    pygame.draw.polygon(surface, edge, front, 3)
    pygame.draw.polygon(surface, top, face)
    pygame.draw.polygon(surface, edge, face, 3)
    _outlined_text(surface, "AU", max(12, int(s * 0.6)), (cx, cy + 0.3 * s), (150, 100, 10), outline=gold)
 
 
def _mine_cart(surface, cx, cy, s, gold=True):
    steel, rim, dark = (95, 100, 112), (150, 156, 168), (30, 32, 38)
    if gold:
        for dx, dy, r in ((-0.55, -0.5, 0.26), (-0.15, -0.72, 0.28), (0.3, -0.68, 0.27), (0.65, -0.48, 0.24), (0.05, -0.45, 0.25)):
            pygame.draw.circle(surface, (240, 190, 40), (cx + dx * s, cy + dy * s), s * r)
            pygame.draw.circle(surface, (150, 105, 10), (cx + dx * s, cy + dy * s), s * r, 2)
    body = [(cx - 1.0 * s, cy - 0.35 * s), (cx + 1.0 * s, cy - 0.35 * s), (cx + 0.78 * s, cy + 0.5 * s), (cx - 0.78 * s, cy + 0.5 * s)]
    pygame.draw.polygon(surface, steel, body)
    pygame.draw.polygon(surface, dark, body, 3)
    pygame.draw.rect(surface, rim, (cx - 1.08 * s, cy - 0.45 * s, 2.16 * s, 0.2 * s), border_radius=3)
    pygame.draw.rect(surface, dark, (cx - 1.08 * s, cy - 0.45 * s, 2.16 * s, 0.2 * s), 2, border_radius=3)
    for dx in (-0.45, 0.45):
        pygame.draw.circle(surface, dark, (cx + dx * s, cy + 0.72 * s), s * 0.26)
        pygame.draw.circle(surface, rim, (cx + dx * s, cy + 0.72 * s), s * 0.1)
    pygame.draw.line(surface, dark, (cx - 1.0 * s, cy + 1.0 * s), (cx + 1.0 * s, cy + 1.0 * s), 3)
 
 
def draw_mine_cart(surface, rect, gold=True, scale=0.35):
    """Mine cart centered in rect. Used by the Gold Rush bonus game."""
    _mine_cart(surface, rect.centerx, rect.centery, min(rect.w, rect.h) * scale, gold)
 
 
# --------------------------------------------------------------------------
# Lookup
# --------------------------------------------------------------------------
 
DRAWERS = {
    # Classic Fruit
    "cherry": _cherry, "lemon": _lemon, "bar": _bar, "bell": _bell, "seven": _seven, "diamond": _diamond,
    # Wild West
    "horseshoe": _horseshoe, "boot": _boot, "hat": _hat, "revolver": _revolver,
    "badge": _badge, "outlaw": _outlaw, "saloon": _saloon,
    # Gold Rush
    "pickaxe": _pickaxe, "lantern": _lantern, "nugget": _nugget, "dynamite": _dynamite,
    "gold_bar": _gold_bar, "mine_cart": _mine_cart,
}
 
 
def draw_symbol(surface, name, rect):
    """Draw one symbol centered in rect."""
    cx, cy = rect.center
    s = min(rect.w, rect.h) * 0.35
 
    drawer = DRAWERS.get(name)
    if drawer:
        drawer(surface, cx, cy, s)
    else:
        # Unknown symbol: show its name so a missing drawing is easy to spot
        label = get_font(int(s * 0.8), True).render(name, True, DARK)
        surface.blit(label, label.get_rect(center=rect.center))