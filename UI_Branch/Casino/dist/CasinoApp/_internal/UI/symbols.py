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
from UI.constants import GOLD, WHITE, FONT_NAME, DARK
 
DARK = (15, 15, 15)
REEL_BG = (245, 240, 225)

# Color palette accents
SHADOW = (0, 0, 0, 45)
HIGHLIGHT_WHITE = (255, 255, 255, 120)
 
 
@lru_cache(maxsize=None)
def get_font(size, bold=False):
    font = pygame.font.Font(FONT_NAME, size)
    font.set_bold(bold)
    return font


def _supersample_draw(surface, cx, cy, w, h, draw_fn):
    """Render at 2x resolution and scale down with smoothscale to eliminate jagged lines."""
    scale = 2
    pad = 12
    sw, sh = int(w * scale + pad * 2), int(h * scale + pad * 2)
    sub = pygame.Surface((sw, sh), pygame.SRCALPHA)

    # Re-center for 2x scale
    sub_cx = sw // 2
    sub_cy = sh // 2
    draw_fn(sub, sub_cx, sub_cy, scale)

    downscaled = pygame.transform.smoothscale(sub, (sw // scale, sh // scale))
    surface.blit(downscaled, (cx - downscaled.get_width() // 2, cy - downscaled.get_height() // 2))
 
 
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
    def _draw(surf, x, y, k):
        sk = s * k
        stem_color = (45, 120, 40)
        stem_dark = (25, 75, 20)
        leaf_color = (65, 165, 50)
        ruby_dark = (145, 15, 25)
        ruby_base = (215, 25, 38)
        ruby_light = (255, 80, 95)
        dark = (35, 12, 18)

        # 1. Graceful Curved Stems
        stem_pts_l = [
            (x - 0.45 * sk, y + 0.15 * sk),
            (x - 0.32 * sk, y - 0.45 * sk),
            (x + 0.08 * sk, y - 0.90 * sk),
        ]
        stem_pts_r = [
            (x + 0.42 * sk, y + 0.28 * sk),
            (x + 0.22 * sk, y - 0.40 * sk),
            (x + 0.08 * sk, y - 0.90 * sk),
        ]
        pygame.draw.lines(surf, (0, 0, 0, 45), False, [(px + 2 * k, py + 2 * k) for px, py in stem_pts_l], max(1, int(4 * k)))
        pygame.draw.lines(surf, (0, 0, 0, 45), False, [(px + 2 * k, py + 2 * k) for px, py in stem_pts_r], max(1, int(4 * k)))
        pygame.draw.lines(surf, stem_color, False, stem_pts_l, max(1, int(3.5 * k)))
        pygame.draw.lines(surf, stem_color, False, stem_pts_r, max(1, int(3.5 * k)))

        # 2. Leaf at Top Union
        leaf_pts = [
            (x + 0.08 * sk, y - 0.90 * sk),
            (x + 0.48 * sk, y - 1.05 * sk),
            (x + 0.72 * sk, y - 0.82 * sk),
            (x + 0.32 * sk, y - 0.75 * sk),
        ]
        pygame.draw.polygon(surf, leaf_color, leaf_pts)
        pygame.draw.polygon(surf, stem_dark, leaf_pts, max(1, int(1.5 * k)))

        # 3. Plump Cherries (Left, then Right overlapping)
        cherries = [(-0.45 * sk, 0.35 * sk, 0.48 * sk), (0.40 * sk, 0.42 * sk, 0.46 * sk)]
        for cx_c, cy_c, cr in cherries:
            px_c, py_c = x + cx_c, y + cy_c

            # Drop shadow
            pygame.draw.circle(surf, (0, 0, 0, 50), (px_c + 2 * k, py_c + 3 * k), cr)

            # Base sphere with depth shading
            pygame.draw.circle(surf, ruby_dark, (px_c, py_c), cr)
            pygame.draw.circle(surf, ruby_base, (px_c - cr * 0.1, py_c - cr * 0.1), cr * 0.90)
            pygame.draw.circle(surf, ruby_light, (px_c - cr * 0.25, py_c - cr * 0.25), cr * 0.55)

            # Indent dimple where stem joins
            pygame.draw.arc(surf, stem_dark, pygame.Rect(px_c - cr * 0.35, py_c - cr * 0.95, cr * 0.7, cr * 0.4), 0, math.pi, max(1, int(2 * k)))

            # Curved glossy specular highlight
            pygame.draw.circle(surf, (255, 235, 240), (px_c - cr * 0.38, py_c - cr * 0.38), cr * 0.20)
            pygame.draw.circle(surf, (255, 255, 255), (px_c - cr * 0.40, py_c - cr * 0.40), cr * 0.09)

            # Outline rim
            pygame.draw.circle(surf, dark, (px_c, py_c), cr, max(1, int(2 * k)))

    _supersample_draw(surface, cx, cy, s * 2.6, s * 2.6, _draw)


def _lemon(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        rind_dark = (195, 145, 15)
        rind_base = (252, 222, 45)
        rind_light = (255, 246, 120)
        dark = (45, 35, 10)

        # Angled citrus body with pointed tips
        lemon_pts = [
            (x - 1.15 * sk, y - 0.05 * sk),  # Left tip nip
            (x - 0.75 * sk, y - 0.60 * sk),
            (x + 0.15 * sk, y - 0.68 * sk),
            (x + 1.10 * sk, y - 0.12 * sk),  # Right stem tip nip
            (x + 0.75 * sk, y + 0.55 * sk),
            (x - 0.25 * sk, y + 0.68 * sk),
        ]

        # Drop shadow
        pygame.draw.polygon(surf, (0, 0, 0, 45), [(px + 2 * k, py + 3 * k) for px, py in lemon_pts])

        # Rind body
        pygame.draw.polygon(surf, rind_dark, lemon_pts)

        # Soft inner highlight curve
        inner_pts = [
            (x - 0.95 * sk, y - 0.05 * sk),
            (x - 0.65 * sk, y - 0.45 * sk),
            (x + 0.15 * sk, y - 0.52 * sk),
            (x + 0.85 * sk, y - 0.10 * sk),
            (x + 0.55 * sk, y + 0.38 * sk),
            (x - 0.20 * sk, y + 0.48 * sk),
        ]
        pygame.draw.polygon(surf, rind_base, inner_pts)

        # Curved glossy gleam
        pygame.draw.ellipse(surf, rind_light, pygame.Rect(x - 0.50 * sk, y - 0.48 * sk, 0.95 * sk, 0.45 * sk))

        # Green leaf on stem end
        leaf = [(x + 0.95 * sk, y - 0.10 * sk), (x + 1.25 * sk, y - 0.38 * sk), (x + 1.35 * sk, y - 0.15 * sk)]
        pygame.draw.polygon(surf, (60, 150, 45), leaf)
        pygame.draw.polygon(surf, (30, 80, 20), leaf, max(1, int(1.2 * k)))

        pygame.draw.polygon(surf, dark, lemon_pts, max(1, int(2 * k)))

    _supersample_draw(surface, cx, cy, s * 2.8, s * 2.4, _draw)


def _bar(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        gold_edge = (165, 115, 20)
        gold_base = (245, 195, 45)
        gold_light = (255, 240, 140)
        dark_bar = (22, 24, 28)
        gloss = (55, 60, 70)

        # Outer beveled gold slab
        outer_rect = pygame.Rect(x - 1.15 * sk, y - 0.55 * sk, 2.30 * sk, 1.10 * sk)
        pygame.draw.rect(surf, (0, 0, 0, 50), outer_rect.move(2 * k, 3 * k), border_radius=int(6 * k))
        pygame.draw.rect(surf, gold_edge, outer_rect, border_radius=int(6 * k))
        pygame.draw.rect(surf, gold_base, outer_rect.inflate(-2 * k, -2 * k), border_radius=int(5 * k))
        pygame.draw.line(surf, gold_light, (outer_rect.left + 6 * k, outer_rect.top + 2 * k), (outer_rect.right - 6 * k, outer_rect.top + 2 * k), max(1, int(1.5 * k)))

        # Enameled inner black container
        inner_rect = outer_rect.inflate(-0.24 * sk, -0.24 * sk)
        pygame.draw.rect(surf, dark_bar, inner_rect, border_radius=int(4 * k))
        pygame.draw.line(surf, gloss, (inner_rect.left + 4 * k, inner_rect.top + 2 * k), (inner_rect.right - 4 * k, inner_rect.top + 2 * k), max(1, int(2 * k)))

        # Embossed Gold "BAR" Text with drop shadow
        _outlined_text(surf, "BAR", int(sk * 0.72), (x, y + 0.02 * sk), gold_base, outline=dark_bar)

    _supersample_draw(surface, cx, cy, s * 2.8, s * 2.2, _draw)


def _bell(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        dark = (42, 30, 8)
        gold_shadow = (150, 105, 15)
        gold_base = (235, 175, 30)
        gold_light = (255, 225, 95)
        gold_gleam = (255, 248, 185)

        # 1. Clapper ball hanging underneath
        clapper_y = y + 0.68 * sk
        pygame.draw.circle(surf, (0, 0, 0, 45), (x + 2 * k, clapper_y + 2 * k), sk * 0.20)
        pygame.draw.circle(surf, gold_shadow, (x, clapper_y), sk * 0.20)
        pygame.draw.circle(surf, gold_light, (x - 2 * k, clapper_y - 2 * k), sk * 0.10)
        pygame.draw.circle(surf, dark, (x, clapper_y), sk * 0.20, max(1, int(1.8 * k)))

        # 2. Top mounting bracket / crown
        hanger = pygame.Rect(x - 0.22 * sk, y - 0.88 * sk, 0.44 * sk, 0.22 * sk)
        pygame.draw.rect(surf, (85, 90, 100), hanger, border_radius=int(2 * k))
        pygame.draw.rect(surf, dark, hanger, max(1, int(1.5 * k)), border_radius=int(2 * k))

        # 3. Flared Bell Body
        bell_pts = [
            (x - 0.32 * sk, y - 0.70 * sk),  # Dome top left
            (x + 0.32 * sk, y - 0.70 * sk),  # Dome top right
            (x + 0.55 * sk, y - 0.05 * sk),  # Upper flare right
            (x + 1.05 * sk, y + 0.52 * sk),  # Bottom flare corner right
            (x - 1.05 * sk, y + 0.52 * sk),  # Bottom flare corner left
            (x - 0.55 * sk, y - 0.05 * sk),  # Upper flare left
        ]
        pygame.draw.polygon(surf, (0, 0, 0, 50), [(px + 2 * k, py + 3 * k) for px, py in bell_pts])
        pygame.draw.polygon(surf, gold_base, bell_pts)

        # Right side depth shadow
        pygame.draw.polygon(surf, gold_shadow, [
            (x + 0.15 * sk, y - 0.70 * sk),
            (x + 0.32 * sk, y - 0.70 * sk),
            (x + 0.55 * sk, y - 0.05 * sk),
            (x + 1.05 * sk, y + 0.52 * sk),
            (x + 0.40 * sk, y + 0.52 * sk),
        ])

        # Left specular highlight bar
        highlight_streak = [
            (x - 0.20 * sk, y - 0.65 * sk),
            (x - 0.10 * sk, y - 0.65 * sk),
            (x - 0.25 * sk, y + 0.48 * sk),
            (x - 0.42 * sk, y + 0.48 * sk),
        ]
        pygame.draw.polygon(surf, gold_gleam, highlight_streak)
        pygame.draw.polygon(surf, dark, bell_pts, max(1, int(2 * k)))

        # 4. Heavy Bottom Rim Bead
        lip_rect = pygame.Rect(x - 1.12 * sk, y + 0.48 * sk, 2.24 * sk, 0.18 * sk)
        pygame.draw.rect(surf, gold_light, lip_rect, border_radius=int(3 * k))
        pygame.draw.line(surf, (255, 255, 255), (lip_rect.left + 4 * k, lip_rect.top + 2 * k), (lip_rect.right - 4 * k, lip_rect.top + 2 * k), max(1, int(1.5 * k)))
        pygame.draw.rect(surf, dark, lip_rect, max(1, int(2 * k)), border_radius=int(3 * k))

    _supersample_draw(surface, cx, cy, s * 2.8, s * 2.6, _draw)


def _seven(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        ruby_dark = (135, 12, 25)
        ruby_base = (225, 30, 48)
        ruby_light = (255, 115, 130)
        gold_trim = (245, 195, 40)
        dark = (35, 10, 15)

        # Bold classic 7 polygon with beveled serifs
        seven_pts = [
            (x - 0.85 * sk, y - 0.95 * sk),
            (x + 0.90 * sk, y - 0.95 * sk),
            (x + 0.90 * sk, y - 0.55 * sk),
            (x + 0.15 * sk, y + 0.95 * sk),
            (x - 0.35 * sk, y + 0.95 * sk),
            (x + 0.30 * sk, y - 0.50 * sk),
            (x - 0.85 * sk, y - 0.50 * sk),
        ]

        # 1. Drop shadow & gold backer
        pygame.draw.polygon(surf, (0, 0, 0, 50), [(px + 2 * k, py + 3 * k) for px, py in seven_pts])
        pygame.draw.polygon(surf, gold_trim, seven_pts)
        pygame.draw.polygon(surf, dark, seven_pts, max(1, int(2 * k)))

        # 2. Inner Ruby Body
        inner_pts = [
            (x - 0.75 * sk, y - 0.88 * sk),
            (x + 0.80 * sk, y - 0.88 * sk),
            (x + 0.80 * sk, y - 0.60 * sk),
            (x + 0.10 * sk, y + 0.85 * sk),
            (x - 0.25 * sk, y + 0.85 * sk),
            (x + 0.35 * sk, y - 0.58 * sk),
            (x - 0.75 * sk, y - 0.58 * sk),
        ]
        pygame.draw.polygon(surf, ruby_base, inner_pts)

        # Diagonal depth shade on lower stem
        pygame.draw.polygon(surf, ruby_dark, [
            (x + 0.35 * sk, y - 0.58 * sk),
            (x + 0.80 * sk, y - 0.60 * sk),
            (x + 0.10 * sk, y + 0.85 * sk),
        ])

        # Glossy specular reflection on top bar
        pygame.draw.line(surf, ruby_light, (x - 0.70 * sk, y - 0.82 * sk), (x + 0.75 * sk, y - 0.82 * sk), max(1, int(2.5 * k)))

    _supersample_draw(surface, cx, cy, s * 2.5, s * 2.6, _draw)


def _diamond(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        dark = (25, 65, 85)
        cyan_deep = (45, 145, 195)
        cyan_mid = (95, 205, 245)
        cyan_light = (195, 240, 255)
        pure_white = (255, 255, 255)

        # Brilliant gem silhouette: Flat table top, flared crown, sharp pointed pavilion bottom
        table_w = 0.52 * sk
        girdle_w = 1.05 * sk
        y_table = y - 0.85 * sk
        y_girdle = y - 0.32 * sk
        y_culet = y + 0.95 * sk

        gem_pts = [
            (x - table_w, y_table),
            (x + table_w, y_table),
            (x + girdle_w, y_girdle),
            (x, y_culet),
            (x - girdle_w, y_girdle),
        ]

        # Drop shadow
        pygame.draw.polygon(surf, (0, 0, 0, 45), [(px + 2 * k, py + 3 * k) for px, py in gem_pts])

        # 1. Pavilion Facets (Bottom cone)
        # Left pavilion facet
        pygame.draw.polygon(surf, cyan_deep, [(x - girdle_w, y_girdle), (x, y_girdle), (x, y_culet)])
        # Right pavilion facet
        pygame.draw.polygon(surf, cyan_mid, [(x + girdle_w, y_girdle), (x, y_girdle), (x, y_culet)])

        # 2. Crown & Table Facets (Top bevels)
        # Center table trapezoid
        table_poly = [(x - table_w, y_table), (x + table_w, y_table), (x + 0.40 * sk, y_girdle), (x - 0.40 * sk, y_girdle)]
        pygame.draw.polygon(surf, cyan_light, table_poly)

        # Side crown triangular facets
        pygame.draw.polygon(surf, pure_white, [(x - table_w, y_table), (x - 0.40 * sk, y_girdle), (x - girdle_w, y_girdle)])
        pygame.draw.polygon(surf, cyan_mid, [(x + table_w, y_table), (x + 0.40 * sk, y_girdle), (x + girdle_w, y_girdle)])

        # 3. Specular Sparkle Star on upper corner
        sparkle = _star(x - 0.45 * sk, y_table + 0.05 * sk, 0.32 * sk, 0.10 * sk, points=4)
        pygame.draw.polygon(surf, pure_white, sparkle)

        # Outlines
        pygame.draw.polygon(surf, dark, gem_pts, max(1, int(2 * k)))
        pygame.draw.line(surf, dark, (x - girdle_w, y_girdle), (x + girdle_w, y_girdle), max(1, int(1.5 * k)))
        pygame.draw.line(surf, dark, (x, y_girdle), (x, y_culet), max(1, int(1.5 * k)))

    _supersample_draw(surface, cx, cy, s * 2.6, s * 2.6, _draw)
 
 
 
# --------------------------------------------------------------------------
# Wild West
# --------------------------------------------------------------------------
 
def _horseshoe(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        silver, highlight, dark = (195, 200, 210), (240, 245, 255), (60, 65, 72)
        poly = _arc_poly(x, y - sk * 0.05, sk * 1.02, sk * 0.52, 140, 400)
        
        # Soft drop shadow
        shadow_pts = [(px + 2 * k, py + 3 * k) for px, py in poly]
        pygame.draw.polygon(surf, (0, 0, 0, 50), shadow_pts)
        
        # Body and inner highlight ring
        pygame.draw.polygon(surf, silver, poly)
        pygame.draw.polygon(surf, highlight, _arc_poly(x, y - sk * 0.05, sk * 0.95, sk * 0.72, 145, 395))
        pygame.draw.polygon(surf, dark, poly, int(2 * k))
        
        # Nail studs & calkins (heels)
        for deg in (185, 225, 270, 315, 355):
            a = math.radians(deg)
            r = sk * 0.76
            sx = x + r * math.cos(a)
            sy = (y - sk * 0.05) - r * math.sin(a)
            pygame.draw.circle(surf, dark, (sx, sy), max(2 * k, sk * 0.08))
            pygame.draw.circle(surf, highlight, (sx - 1 * k, sy - 1 * k), max(1 * k, sk * 0.03))

    _supersample_draw(surface, cx, cy, s * 2.4, s * 2.4, _draw)


def _boot(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        leather, dark, stitch = (155, 95, 45), (55, 30, 12), (215, 175, 110)
        
        # Natural angled boot silhouette
        outline = [
            (-0.55 * sk, -1.05 * sk), (0.25 * sk, -1.05 * sk),
            (0.18 * sk, -0.05 * sk), (0.4 * sk, 0.25 * sk),
            (1.05 * sk, 0.45 * sk), (1.05 * sk, 0.85 * sk),
            (-0.45 * sk, 0.85 * sk), (-0.55 * sk, 0.3 * sk)
        ]
        pts = [(x + px, y + py) for px, py in outline]
        
        # Shadow & boot base
        pygame.draw.polygon(surf, (0, 0, 0, 50), [(px + 2 * k, py + 3 * k) for px, py in pts])
        pygame.draw.polygon(surf, leather, pts)
        
        # Top cuff collar
        cuff = pygame.Rect(x - 0.58 * sk, y - 1.1 * sk, 0.86 * sk, 0.24 * sk)
        pygame.draw.rect(surf, (190, 130, 70), cuff, border_radius=int(2 * k))
        pygame.draw.rect(surf, dark, cuff, int(1.5 * k), border_radius=int(2 * k))
        
        # Heavy sole & heel
        sole = pygame.Rect(x - 0.48 * sk, y + 0.85 * sk, 1.55 * sk, 0.16 * sk)
        heel = pygame.Rect(x - 0.48 * sk, y + 0.85 * sk, 0.45 * sk, 0.3 * sk)
        pygame.draw.rect(surf, dark, sole, border_radius=int(2 * k))
        pygame.draw.rect(surf, dark, heel, border_radius=int(2 * k))
        
        # Decorative stitching line & outline
        pygame.draw.lines(surf, stitch, False, [
            (x - 0.2 * sk, y - 0.7 * sk),
            (x - 0.1 * sk, y - 0.1 * sk),
            (x + 0.35 * sk, y + 0.45 * sk)
        ], int(1.5 * k))
        pygame.draw.polygon(surf, dark, pts, int(2 * k))

    _supersample_draw(surface, cx, cy, s * 2.4, s * 2.6, _draw)


def _hat(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        tan, tan_light, dark = (210, 155, 80), (235, 185, 115), (95, 55, 20)
        
        # Crown with pinched top center
        crown = pygame.Rect(x - 0.55 * sk, y - 0.75 * sk, 1.1 * sk, 1.05 * sk)
        pygame.draw.rect(surf, tan, crown, border_top_left_radius=int(0.35 * sk), border_top_right_radius=int(0.35 * sk))
        pygame.draw.rect(surf, tan_light, crown.inflate(-0.3 * sk, -0.3 * sk), border_radius=int(0.2 * sk))
        
        # Crease in cowboy crown
        pygame.draw.line(surf, dark, (x, crown.top + 2), (x, crown.top + 0.32 * sk), int(2.5 * k))
        
        # Red leather band
        band = pygame.Rect(crown.left, crown.bottom - int(0.22 * sk), crown.w, int(0.18 * sk))
        pygame.draw.rect(surf, (160, 35, 25), band)
        pygame.draw.rect(surf, GOLD, (x - 0.1 * sk, band.y + 0.01 * sk, 0.2 * sk, band.h), border_radius=1)
        
        # Curved sweeping brim
        brim = pygame.Rect(x - 1.15 * sk, y + 0.25 * sk, 2.3 * sk, 0.55 * sk)
        pygame.draw.ellipse(surf, (0, 0, 0, 50), brim.move(0, 3 * k))
        pygame.draw.ellipse(surf, tan, brim)
        pygame.draw.ellipse(surf, dark, brim, int(2 * k))
        pygame.draw.rect(surf, dark, crown, int(2 * k), border_top_left_radius=int(0.35 * sk), border_top_right_radius=int(0.35 * sk))

    _supersample_draw(surface, cx, cy, s * 2.8, s * 2.4, _draw)


def _revolver(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        steel = (130, 135, 145)
        light_steel = (185, 190, 205)
        dark = (35, 38, 44)
        wood = (145, 82, 38)
        wood_dark = (85, 45, 18)

        # 1. Drop shadow for the entire silhouette
        shadow_grip = [
            (x + 0.18 * sk + 2 * k, y - 0.05 * sk + 3 * k),
            (x + 0.58 * sk + 2 * k, y + 0.05 * sk + 3 * k),
            (x + 0.48 * sk + 2 * k, y + 0.95 * sk + 3 * k),
            (x + 0.08 * sk + 2 * k, y + 0.82 * sk + 3 * k),
        ]
        pygame.draw.polygon(surf, (0, 0, 0, 45), shadow_grip)
        pygame.draw.rect(surf, (0, 0, 0, 45), pygame.Rect(x - 1.15 * sk + 2 * k, y - 0.42 * sk + 3 * k, 1.85 * sk, 0.58 * sk), border_radius=int(3 * k))

        # 2. Main Receiver / Frame (Solid core bridging barrel, cylinder, and grip)
        # Top strap + rear frame
        frame_rect = pygame.Rect(x - 0.45 * sk, y - 0.42 * sk, 1.05 * sk, 0.55 * sk)
        pygame.draw.rect(surf, steel, frame_rect, border_top_right_radius=int(5 * k))

        # 3. Barrel (extends directly out of the front edge of the frame)
        barrel_rect = pygame.Rect(x - 1.15 * sk, y - 0.38 * sk, 0.75 * sk, 0.22 * sk)
        pygame.draw.rect(surf, steel, barrel_rect, border_top_left_radius=int(2 * k), border_bottom_left_radius=int(2 * k))
        # Front sight blade on top of muzzle
        pygame.draw.polygon(surf, dark, [
            (x - 1.12 * sk, y - 0.38 * sk),
            (x - 1.04 * sk, y - 0.48 * sk),
            (x - 1.04 * sk, y - 0.38 * sk)
        ])
        # Barrel top reflection streak
        pygame.draw.line(surf, light_steel, (barrel_rect.left + 2 * k, barrel_rect.top + 2 * k), (barrel_rect.right, barrel_rect.top + 2 * k), int(1.5 * k))

        # 4. Cylinder (set recessed into the frame center)
        cyl_rect = pygame.Rect(x - 0.38 * sk, y - 0.35 * sk, 0.55 * sk, 0.42 * sk)
        pygame.draw.rect(surf, steel, cyl_rect, border_radius=int(3 * k))
        # Cylinder chambers / flutes
        pygame.draw.line(surf, dark, (cyl_rect.left + 2 * k, cyl_rect.top + 0.12 * sk), (cyl_rect.right - 2 * k, cyl_rect.top + 0.12 * sk), int(2 * k))
        pygame.draw.line(surf, dark, (cyl_rect.left + 2 * k, cyl_rect.top + 0.28 * sk), (cyl_rect.right - 2 * k, cyl_rect.top + 0.28 * sk), int(2 * k))
        pygame.draw.rect(surf, dark, cyl_rect, int(2 * k), border_radius=int(3 * k))

        # 5. Wood Grip / Handle (welded directly to the back-bottom of the receiver)
        grip_pts = [
            (x + 0.18 * sk, y - 0.05 * sk),  # Upper-front joint to frame
            (x + 0.58 * sk, y + 0.05 * sk),  # Upper-rear hammer crest
            (x + 0.48 * sk, y + 0.95 * sk),  # Butt rear corner
            (x + 0.08 * sk, y + 0.82 * sk),  # Butt front corner
        ]
        pygame.draw.polygon(surf, wood, grip_pts)
        pygame.draw.polygon(surf, wood_dark, grip_pts, int(2 * k))
        # Grip screw / medallion
        pygame.draw.circle(surf, GOLD, (x + 0.32 * sk, y + 0.45 * sk), max(1 * k, 0.07 * sk))
        pygame.draw.circle(surf, dark, (x + 0.32 * sk, y + 0.45 * sk), max(1 * k, 0.07 * sk), int(1 * k))

        # 6. Trigger Guard & Trigger (anchored from under cylinder down to front of grip)
        guard_rect = pygame.Rect(x - 0.22 * sk, y + 0.05 * sk, 0.38 * sk, 0.32 * sk)
        pygame.draw.arc(surf, dark, guard_rect, math.pi * 0.95, math.pi * 2.05, int(2.5 * k))
        # Trigger blade curling inside the guard
        pygame.draw.line(surf, dark, (x - 0.06 * sk, y + 0.12 * sk), (x + 0.02 * sk, y + 0.24 * sk), int(2 * k))

        # 7. Hammer on top-rear of frame
        pygame.draw.polygon(surf, dark, [
            (x + 0.42 * sk, y - 0.38 * sk),
            (x + 0.58 * sk, y - 0.25 * sk),
            (x + 0.45 * sk, y - 0.15 * sk)
        ])

        # 8. Frame Outlines
        pygame.draw.rect(surf, dark, barrel_rect, int(2 * k), border_top_left_radius=int(2 * k), border_bottom_left_radius=int(2 * k))
        pygame.draw.line(surf, dark, (barrel_rect.right, frame_rect.top), (frame_rect.right, frame_rect.top), int(2 * k))
        pygame.draw.line(surf, dark, (frame_rect.right, frame_rect.top), (frame_rect.right, frame_rect.bottom), int(2 * k))

    _supersample_draw(surface, cx, cy, s * 2.8, s * 2.6, _draw)


def _badge(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        gold, gold_light, edge = (255, 210, 65), (255, 240, 150), (145, 95, 10)
        pts = _star(x, y, sk * 1.08, sk * 0.52)
        
        # Star drop shadow
        pygame.draw.polygon(surf, (0, 0, 0, 50), [(px + 2 * k, py + 2 * k) for px, py in pts])
        pygame.draw.polygon(surf, gold, pts)
        
        # Ball tips on points
        for i in range(0, 10, 2):
            pygame.draw.circle(surf, gold_light, pts[i], max(2 * k, sk * 0.14))
            pygame.draw.circle(surf, edge, pts[i], max(2 * k, sk * 0.14), int(1.5 * k))
            
        pygame.draw.polygon(surf, edge, pts, int(2 * k))
        
        # Center medallion
        pygame.draw.circle(surf, (225, 175, 40), (x, y), sk * 0.32)
        pygame.draw.circle(surf, gold_light, (x, y), sk * 0.22)
        pygame.draw.circle(surf, edge, (x, y), sk * 0.32, int(2 * k))

    _supersample_draw(surface, cx, cy, s * 2.5, s * 2.5, _draw)


def _outlaw(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        face, dark_skin = (245, 205, 160), (160, 110, 75)
        
        # Face base with shadow
        pygame.draw.circle(surf, (0, 0, 0, 45), (x, y - sk * 0.1 + 2 * k), sk * 0.85)
        pygame.draw.circle(surf, face, (x, y - sk * 0.15), sk * 0.85)
        pygame.draw.circle(surf, dark_skin, (x, y - sk * 0.15), sk * 0.85, int(2 * k))
        
        # Sleek bandit mask
        mask = pygame.Rect(x - 0.85 * sk, y - sk * 0.58, 1.7 * sk, 0.46 * sk)
        pygame.draw.ellipse(surf, DARK, mask)
        
        # Angled expressive eyes
        for dx in (-0.36, 0.36):
            ex, ey = x + dx * sk, y - sk * 0.36
            pygame.draw.circle(surf, WHITE, (ex, ey), sk * 0.13)
            pygame.draw.circle(surf, (20, 20, 20), (ex, ey), sk * 0.06)
            pygame.draw.circle(surf, WHITE, (ex - 0.03 * sk, ey - 0.03 * sk), sk * 0.03)
            
        # Bandana with folds
        bandana = [(x - 0.85 * sk, y - sk * 0.05), (x + 0.85 * sk, y - sk * 0.05), (x, y + 1.05 * sk)]
        pygame.draw.polygon(surf, (195, 30, 30), bandana)
        pygame.draw.polygon(surf, (130, 15, 15), bandana, int(2 * k))
        pygame.draw.lines(surf, (150, 20, 20), False, [(x - 0.5 * sk, y + 0.25 * sk), (x, y + 0.65 * sk), (x + 0.5 * sk, y + 0.25 * sk)], int(2 * k))
        
        _outlined_text(surf, "WILD", int(sk * 0.58), (x, y + sk * 0.28), WHITE)

    _supersample_draw(surface, cx, cy, s * 2.4, s * 2.6, _draw)


def _saloon(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        wood, wood_light, dark = (155, 95, 45), (185, 125, 70), (70, 40, 15)
        
        # Batwing doors
        for x_offset in (-0.98 * sk, 0.08 * sk):
            door = pygame.Rect(x + x_offset, y - 0.35 * sk, 0.9 * sk, 1.25 * sk)
            pygame.draw.rect(surf, (0, 0, 0, 45), door.move(2 * k, 2 * k), border_top_left_radius=int(0.25 * sk), border_top_right_radius=int(0.25 * sk))
            pygame.draw.rect(surf, wood, door, border_top_left_radius=int(0.25 * sk), border_top_right_radius=int(0.25 * sk))
            
            # Shaded horizontal slats
            for i in range(1, 5):
                sy = door.top + i * door.h // 5
                pygame.draw.line(surf, wood_light, (door.left + 4 * k, sy - 1 * k), (door.right - 4 * k, sy - 1 * k), int(1 * k))
                pygame.draw.line(surf, dark, (door.left + 4 * k, sy), (door.right - 4 * k, sy), int(2 * k))
                
            pygame.draw.rect(surf, dark, door, int(2 * k), border_top_left_radius=int(0.25 * sk), border_top_right_radius=int(0.25 * sk))
            
        # Top banner with gold border & drop shadow
        banner = pygame.Rect(0, 0, int(2.15 * sk), int(0.58 * sk))
        banner.center = (x, y - 0.72 * sk)
        pygame.draw.rect(surf, (0, 0, 0, 60), banner.move(2 * k, 2 * k), border_radius=int(4 * k))
        pygame.draw.rect(surf, (185, 25, 25), banner, border_radius=int(4 * k))
        pygame.draw.rect(surf, GOLD, banner, int(2 * k), border_radius=int(4 * k))
        
        label = get_font(max(12, int(sk * 0.48)), True).render("FREE", True, GOLD)
        surf.blit(label, label.get_rect(center=banner.center))

    _supersample_draw(surface, cx, cy, s * 2.6, s * 2.6, _draw)
 
 
# --------------------------------------------------------------------------
# Gold Rush
# --------------------------------------------------------------------------

def _pickaxe(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        wood = (145, 95, 45)
        wood_dark = (85, 48, 20)
        steel = (145, 152, 165)
        steel_light = (210, 218, 230)
        dark = (35, 38, 44)

        # 1. Wooden Handle angled diagonally
        pts_handle = [
            (x - 0.72 * sk, y + 0.95 * sk),
            (x - 0.58 * sk, y + 1.05 * sk),
            (x + 0.32 * sk, y - 0.65 * sk),
            (x + 0.20 * sk, y - 0.75 * sk),
        ]
        pygame.draw.polygon(surf, (0, 0, 0, 45), [(px + 2 * k, py + 3 * k) for px, py in pts_handle])
        pygame.draw.polygon(surf, wood, pts_handle)
        pygame.draw.polygon(surf, wood_dark, pts_handle, max(1, int(1.5 * k)))

        # Handle wrap / grip bands
        pygame.draw.line(surf, dark, (x - 0.65 * sk, y + 0.85 * sk), (x - 0.52 * sk, y + 0.95 * sk), max(1, int(2 * k)))
        pygame.draw.line(surf, dark, (x - 0.55 * sk, y + 0.70 * sk), (x - 0.42 * sk, y + 0.80 * sk), max(1, int(2 * k)))

        # 2. Pickaxe Head (Arched steel blade with sharp chisel ends)
        head_pts = [
            (x - 0.95 * sk, y - 0.25 * sk),  # Left pick point
            (x - 0.25 * sk, y - 0.85 * sk),
            (x + 0.45 * sk, y - 0.85 * sk),
            (x + 0.95 * sk, y - 0.35 * sk),  # Right broad chisel
            (x + 0.82 * sk, y - 0.25 * sk),
            (x + 0.32 * sk, y - 0.58 * sk),
            (x - 0.15 * sk, y - 0.58 * sk),
            (x - 0.80 * sk, y - 0.18 * sk),
        ]
        pygame.draw.polygon(surf, (0, 0, 0, 50), [(px + 2 * k, py + 3 * k) for px, py in head_pts])
        pygame.draw.polygon(surf, steel, head_pts)

        # Top ridge reflection
        pygame.draw.lines(surf, steel_light, False, [
            (x - 0.90 * sk, y - 0.25 * sk),
            (x + 0.10 * sk, y - 0.82 * sk),
            (x + 0.90 * sk, y - 0.35 * sk),
        ], max(1, int(1.5 * k)))

        # Center iron collar collar/sleeve
        collar = pygame.Rect(x + 0.05 * sk, y - 0.78 * sk, 0.32 * sk, 0.32 * sk)
        pygame.draw.rect(surf, dark, collar, border_radius=int(2 * k))
        pygame.draw.circle(surf, steel_light, (x + 0.21 * sk, y - 0.62 * sk), max(1 * k, 0.04 * sk))

        pygame.draw.polygon(surf, dark, head_pts, max(1, int(2 * k)))

    _supersample_draw(surface, cx, cy, s * 2.6, s * 2.6, _draw)


def _lantern(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        dark = (28, 30, 35)
        brass = (185, 135, 45)
        brass_light = (235, 195, 95)
        glass = (255, 235, 150)
        glow = (255, 150, 20)

        # 1. Hanging Wire Loop / Bail Handle
        pygame.draw.arc(surf, (0, 0, 0, 45), pygame.Rect(x - 0.6 * sk + 2 * k, y - 1.15 * sk + 2 * k, 1.2 * sk, 1.0 * sk), 0, math.pi, max(1, int(2.5 * k)))
        pygame.draw.arc(surf, dark, pygame.Rect(x - 0.6 * sk, y - 1.15 * sk, 1.2 * sk, 1.0 * sk), 0, math.pi, max(1, int(2.5 * k)))

        # 2. Vented Cap / Hood
        cap_poly = [
            (x - 0.62 * sk, y - 0.42 * sk),
            (x + 0.62 * sk, y - 0.42 * sk),
            (x + 0.38 * sk, y - 0.78 * sk),
            (x - 0.38 * sk, y - 0.78 * sk),
        ]
        pygame.draw.polygon(surf, brass, cap_poly)
        pygame.draw.line(surf, brass_light, (x - 0.35 * sk, y - 0.72 * sk), (x + 0.35 * sk, y - 0.72 * sk), max(1, int(1.5 * k)))
        pygame.draw.polygon(surf, dark, cap_poly, max(1, int(2 * k)))

        # 3. Glass Globe & Flame
        globe_rect = pygame.Rect(x - 0.52 * sk, y - 0.42 * sk, 1.04 * sk, 1.05 * sk)
        pygame.draw.rect(surf, glass, globe_rect, border_radius=int(6 * k))

        # Internal glowing flame
        pygame.draw.ellipse(surf, glow, pygame.Rect(x - 0.22 * sk, y - 0.15 * sk, 0.44 * sk, 0.65 * sk))
        pygame.draw.ellipse(surf, (255, 245, 180), pygame.Rect(x - 0.10 * sk, y + 0.05 * sk, 0.20 * sk, 0.35 * sk))

        # Vertical protective wire cage bars
        for wx in (-0.28 * sk, 0.28 * sk):
            pygame.draw.line(surf, dark, (x + wx, globe_rect.top), (x + wx, globe_rect.bottom), max(1, int(1.5 * k)))
        pygame.draw.rect(surf, dark, globe_rect, max(1, int(2 * k)), border_radius=int(6 * k))

        # 4. Fuel Reservoir Base
        base_rect = pygame.Rect(x - 0.68 * sk, y + 0.60 * sk, 1.36 * sk, 0.32 * sk)
        pygame.draw.rect(surf, (0, 0, 0, 45), base_rect.move(0, 2 * k), border_radius=int(3 * k))
        pygame.draw.rect(surf, brass, base_rect, border_radius=int(3 * k))
        pygame.draw.line(surf, brass_light, (base_rect.left + 3 * k, base_rect.top + 2 * k), (base_rect.right - 3 * k, base_rect.top + 2 * k), max(1, int(1.5 * k)))
        pygame.draw.rect(surf, dark, base_rect, max(1, int(2 * k)), border_radius=int(3 * k))

    _supersample_draw(surface, cx, cy, s * 2.4, s * 2.6, _draw)


def _nugget(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        gold_shadow = (145, 95, 10)
        gold_base = (242, 185, 30)
        gold_light = (255, 218, 70)
        gold_bright = (255, 248, 175)
        dark = (45, 30, 8)

        # Multi-faceted irregular polygon
        outer_pts = [
            (x - 0.95 * sk, y + 0.20 * sk),
            (x - 0.70 * sk, y - 0.50 * sk),
            (x - 0.15 * sk, y - 0.85 * sk),
            (x + 0.55 * sk, y - 0.65 * sk),
            (x + 0.98 * sk, y - 0.05 * sk),
            (x + 0.82 * sk, y + 0.65 * sk),
            (x + 0.15 * sk, y + 0.88 * sk),
            (x - 0.60 * sk, y + 0.78 * sk),
        ]
        pygame.draw.polygon(surf, (0, 0, 0, 50), [(px + 2 * k, py + 3 * k) for px, py in outer_pts])
        pygame.draw.polygon(surf, gold_base, outer_pts)

        # Facets across surface
        facet_upper = [
            (x - 0.70 * sk, y - 0.50 * sk),
            (x - 0.15 * sk, y - 0.85 * sk),
            (x + 0.10 * sk, y - 0.40 * sk),
            (x - 0.40 * sk, y - 0.25 * sk),
        ]
        pygame.draw.polygon(surf, gold_light, facet_upper)

        facet_side = [
            (x + 0.15 * sk, y + 0.88 * sk),
            (x + 0.82 * sk, y + 0.65 * sk),
            (x + 0.40 * sk, y + 0.15 * sk),
        ]
        pygame.draw.polygon(surf, gold_shadow, facet_side)

        # Bright specular gleam
        pygame.draw.polygon(surf, gold_bright, [
            (x - 0.45 * sk, y - 0.25 * sk),
            (x - 0.15 * sk, y - 0.55 * sk),
            (x + 0.10 * sk, y - 0.40 * sk),
        ])

        # Dark rocky crevices
        pygame.draw.line(surf, dark, (x - 0.40 * sk, y - 0.25 * sk), (x + 0.10 * sk, y - 0.40 * sk), max(1, int(1.5 * k)))
        pygame.draw.line(surf, dark, (x + 0.10 * sk, y - 0.40 * sk), (x + 0.55 * sk, y - 0.65 * sk), max(1, int(1.5 * k)))
        pygame.draw.polygon(surf, dark, outer_pts, max(1, int(2 * k)))

    _supersample_draw(surface, cx, cy, s * 2.4, s * 2.4, _draw)


def _dynamite(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        dark_red = (145, 20, 20)
        bright_red = (215, 42, 42)
        band_cream = (235, 215, 175)
        dark = (35, 22, 22)

        # Drop shadow for the bundle
        shadow_rect = pygame.Rect(x - 0.82 * sk + 2 * k, y - 0.38 * sk + 3 * k, 1.64 * sk, 1.35 * sk)
        pygame.draw.rect(surf, (0, 0, 0, 50), shadow_rect, border_radius=int(4 * k))

        # 3 dynamite sticks
        offsets = [(-0.52 * sk, -0.05 * sk), (0.0, 0.05 * sk), (0.52 * sk, -0.05 * sk)]
        for dx, dy in offsets:
            stick = pygame.Rect(x + dx - 0.24 * sk, y + dy - 0.42 * sk, 0.48 * sk, 1.30 * sk)
            pygame.draw.rect(surf, bright_red, stick, border_radius=int(3 * k))
            pygame.draw.line(surf, (245, 100, 100), (stick.left + 2 * k, stick.top + 2 * k), (stick.left + 2 * k, stick.bottom - 2 * k), max(1, int(1.5 * k)))
            pygame.draw.rect(surf, dark, stick, max(1, int(1.5 * k)), border_radius=int(3 * k))

        # Cream tying bands
        for by in (-0.05 * sk, 0.52 * sk):
            b_rect = pygame.Rect(x - 0.80 * sk, y + by, 1.60 * sk, 0.18 * sk)
            pygame.draw.rect(surf, band_cream, b_rect, border_radius=int(1.5 * k))
            pygame.draw.rect(surf, dark, b_rect, max(1, int(1.2 * k)), border_radius=int(1.5 * k))

        # Braided fuses connecting into one
        fuse_pts = [(x, y - 0.35 * sk), (x + 0.15 * sk, y - 0.65 * sk), (x + 0.45 * sk, y - 0.85 * sk)]
        pygame.draw.lines(surf, (70, 55, 45), False, fuse_pts, max(1, int(2.5 * k)))

        # Sizzling spark star on tip
        spark_pts = _star(x + 0.50 * sk, y - 0.88 * sk, 0.34 * sk, 0.14 * sk, points=5)
        pygame.draw.polygon(surf, (255, 210, 40), spark_pts)
        pygame.draw.circle(surf, (255, 245, 200), (x + 0.50 * sk, y - 0.88 * sk), 0.10 * sk)

    _supersample_draw(surface, cx, cy, s * 2.5, s * 2.5, _draw)


def _gold_sack(surface, cx, cy, s):
    """Bulging canvas miner's ore sack filled with gold."""
    def _draw(surf, x, y, k):
        sk = s * k
        canvas = (205, 170, 125)
        canvas_dark = (160, 125, 85)
        rope = (95, 65, 35)
        gold = (255, 205, 45)
        dark = (42, 32, 22)

        # 1. Main sack silhouette
        sack_pts = [
            (x - 0.40 * sk, y - 0.55 * sk),  # Neck left
            (x - 0.95 * sk, y - 0.10 * sk),  # Upper belly left
            (x - 0.90 * sk, y + 0.68 * sk),  # Bottom left
            (x + 0.90 * sk, y + 0.68 * sk),  # Bottom right
            (x + 0.95 * sk, y - 0.10 * sk),  # Upper belly right
            (x + 0.40 * sk, y - 0.55 * sk),  # Neck right
        ]
        pygame.draw.polygon(surf, (0, 0, 0, 50), [(px + 2 * k, py + 3 * k) for px, py in sack_pts])
        pygame.draw.polygon(surf, canvas, sack_pts)

        # Shading folds along bottom & sides
        pygame.draw.polygon(surf, canvas_dark, [
            (x - 0.85 * sk, y + 0.45 * sk),
            (x, y + 0.68 * sk),
            (x - 0.88 * sk, y + 0.68 * sk)
        ])
        pygame.draw.polygon(surf, canvas_dark, [
            (x + 0.85 * sk, y + 0.45 * sk),
            (x, y + 0.68 * sk),
            (x + 0.88 * sk, y + 0.68 * sk)
        ])

        # 2. Tied neck ruffle
        ruffle_pts = [
            (x - 0.45 * sk, y - 0.55 * sk),
            (x - 0.60 * sk, y - 0.85 * sk),
            (x, y - 0.72 * sk),
            (x + 0.60 * sk, y - 0.85 * sk),
            (x + 0.45 * sk, y - 0.55 * sk),
        ]
        pygame.draw.polygon(surf, canvas, ruffle_pts)
        pygame.draw.polygon(surf, dark, ruffle_pts, max(1, int(1.5 * k)))

        # 3. Tying Rope Wrap
        neck_rect = pygame.Rect(x - 0.42 * sk, y - 0.58 * sk, 0.84 * sk, 0.14 * sk)
        pygame.draw.rect(surf, rope, neck_rect, border_radius=int(2 * k))
        pygame.draw.rect(surf, dark, neck_rect, max(1, int(1.5 * k)), border_radius=int(2 * k))

        # Sack outline
        pygame.draw.polygon(surf, dark, sack_pts, max(1, int(2 * k)))

        # 4. Gold '$' emblem stamped on belly
        _outlined_text(surf, "$", int(sk * 0.95), (x, y + 0.12 * sk), gold, outline=dark)

    _supersample_draw(surface, cx, cy, s * 2.5, s * 2.5, _draw)
 
def _mine_cart(surface, cx, cy, s, gold=True):
    def _draw(surf, x, y, k):
        sk = s * k
        dark = (28, 30, 36)
        steel_base = (75, 80, 92)
        steel_light = (130, 138, 155)
        steel_dark = (50, 54, 62)
        iron_band = (40, 44, 52)
        wood_tie = (110, 70, 35)
        rail_steel = (165, 172, 185)

        # 1. Mine Track Rails and Wooden Cross-Tie
        # Wooden tie underneath
        tie_rect = pygame.Rect(x - 1.25 * sk, y + 0.9 * sk, 2.5 * sk, 0.18 * sk)
        pygame.draw.rect(surf, (0, 0, 0, 45), tie_rect.move(0, 2 * k), border_radius=int(2 * k))
        pygame.draw.rect(surf, wood_tie, tie_rect, border_radius=int(2 * k))
        pygame.draw.rect(surf, dark, tie_rect, int(1.5 * k), border_radius=int(2 * k))

        # Parallel steel rails
        pygame.draw.rect(surf, rail_steel, pygame.Rect(x - 1.35 * sk, y + 0.82 * sk, 2.7 * sk, 0.09 * sk), border_radius=int(1.5 * k))
        pygame.draw.line(surf, dark, (x - 1.35 * sk, y + 0.91 * sk), (x + 1.35 * sk, y + 0.91 * sk), int(1.5 * k))

        # 2. Heaped Gold Ore & Nuggets overflowing top rim
        if gold:
            nugget_specs = [
                (-0.62, -0.42, 0.28, (230, 175, 25)),
                (0.60, -0.42, 0.26, (225, 170, 20)),
                (-0.35, -0.62, 0.34, (255, 205, 45)),
                (0.35, -0.60, 0.32, (250, 195, 35)),
                (-0.05, -0.78, 0.38, (255, 220, 65)),
                (0.12, -0.52, 0.30, (245, 190, 30)),
            ]
            for dx, dy, r, col in nugget_specs:
                nx, ny, nr = x + dx * sk, y + dy * sk, r * sk
                pts = [
                    (nx - nr * 0.9, ny + nr * 0.2),
                    (nx - nr * 0.5, ny - nr * 0.8),
                    (nx + nr * 0.3, ny - nr * 0.9),
                    (nx + nr * 0.85, ny - nr * 0.2),
                    (nx + nr * 0.6, ny + nr * 0.7),
                    (nx - nr * 0.4, ny + nr * 0.8),
                ]
                # Faceted nugget body and shadow
                pygame.draw.polygon(surf, col, pts)
                pygame.draw.polygon(surf, (155, 105, 10), pts, max(1, int(1.5 * k)))
                # Inner sparkle / specular highlight
                pygame.draw.polygon(surf, (255, 245, 180), [
                    (nx - nr * 0.2, ny - nr * 0.6),
                    (nx + nr * 0.2, ny - nr * 0.6),
                    (nx, ny - nr * 0.2)
                ])

        # 3. Main Bucket Drop Shadow
        bucket_poly = [
            (x - 1.05 * sk, y - 0.32 * sk),
            (x + 1.05 * sk, y - 0.32 * sk),
            (x + 0.78 * sk, y + 0.48 * sk),
            (x - 0.78 * sk, y + 0.48 * sk),
        ]
        pygame.draw.polygon(surf, (0, 0, 0, 50), [(px + 2 * k, py + 3 * k) for px, py in bucket_poly])

        # 4. Main Steel Bucket Body
        pygame.draw.polygon(surf, steel_base, bucket_poly)

        # Subtle steel gradient highlight across upper face
        highlight_poly = [
            (x - 1.0 * sk, y - 0.28 * sk),
            (x + 1.0 * sk, y - 0.28 * sk),
            (x + 0.86 * sk, y + 0.05 * sk),
            (x - 0.86 * sk, y + 0.05 * sk),
        ]
        pygame.draw.polygon(surf, steel_light, highlight_poly)

        # 5. Heavy Iron Support Bands and Corner Rivets
        # Diagonal / Center support band
        pygame.draw.polygon(surf, steel_dark, [
            (x - 0.18 * sk, y - 0.3 * sk), (x + 0.18 * sk, y - 0.3 * sk),
            (x + 0.14 * sk, y + 0.46 * sk), (x - 0.14 * sk, y + 0.46 * sk)
        ])
        # Rivets along center and bottom edge
        for ry_offset in (-0.15, 0.1, 0.35):
            pygame.draw.circle(surf, dark, (x, y + ry_offset * sk), max(1 * k, sk * 0.05))
            pygame.draw.circle(surf, steel_light, (x - 1 * k, y + (ry_offset - 0.02) * sk), max(1 * k, sk * 0.02))

        # Bottom bumper plate
        pygame.draw.polygon(surf, iron_band, [
            (x - 0.84 * sk, y + 0.38 * sk), (x + 0.84 * sk, y + 0.38 * sk),
            (x + 0.76 * sk, y + 0.48 * sk), (x - 0.76 * sk, y + 0.48 * sk)
        ])

        # Bucket outer outline
        pygame.draw.polygon(surf, dark, bucket_poly, max(1, int(2 * k)))

        # 6. Upper Rolled Steel Lip / Rim
        rim_rect = pygame.Rect(x - 1.14 * sk, y - 0.42 * sk, 2.28 * sk, 0.18 * sk)
        pygame.draw.rect(surf, (0, 0, 0, 45), rim_rect.move(0, 2 * k), border_radius=int(3 * k))
        pygame.draw.rect(surf, steel_light, rim_rect, border_radius=int(3 * k))
        pygame.draw.line(surf, (240, 245, 255), (rim_rect.left + 3 * k, rim_rect.top + 2 * k), (rim_rect.right - 3 * k, rim_rect.top + 2 * k), max(1, int(1.5 * k)))
        pygame.draw.rect(surf, dark, rim_rect, max(1, int(2 * k)), border_radius=int(3 * k))

        # 7. Heavy Flanged Wheels & Axle Mounts
        for wx in (-0.52 * sk, 0.52 * sk):
            cx_wheel = x + wx
            cy_wheel = y + 0.65 * sk

            # Wheel drop shadow
            pygame.draw.circle(surf, (0, 0, 0, 50), (cx_wheel + 2 * k, cy_wheel + 2 * k), sk * 0.28)
            # Outer flange
            pygame.draw.circle(surf, dark, (cx_wheel, cy_wheel), sk * 0.28)
            # Wheel tire ring
            pygame.draw.circle(surf, steel_light, (cx_wheel, cy_wheel), sk * 0.24)
            pygame.draw.circle(surf, steel_dark, (cx_wheel, cy_wheel), sk * 0.17)
            # Wheel spokes (4 cross notches)
            for angle in (0, 45, 90, 135):
                rad = math.radians(angle)
                dx_s, dy_s = math.cos(rad) * (sk * 0.16), math.sin(rad) * (sk * 0.16)
                pygame.draw.line(surf, dark, (cx_wheel - dx_s, cy_wheel - dy_s), (cx_wheel + dx_s, cy_wheel + dy_s), max(1, int(1.5 * k)))
            # Axle center nut with highlight
            pygame.draw.circle(surf, dark, (cx_wheel, cy_wheel), sk * 0.08)
            pygame.draw.circle(surf, (220, 225, 235), (cx_wheel - 1 * k, cy_wheel - 1 * k), max(1, sk * 0.035))

    _supersample_draw(surface, cx, cy, s * 2.8, s * 2.6, _draw)
 
def draw_mine_cart(surface, rect, gold=True, scale=0.35):
    """Mine cart centered in rect. Used by the Gold Rush bonus game."""
    _mine_cart(surface, rect.centerx, rect.centery, min(rect.w, rect.h) * scale, gold)
 
 
 
# --------------------------------------------------------------------------
# Cows Gone Wild
# --------------------------------------------------------------------------

def _milk_carton(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        carton_blue = (50, 125, 220)
        carton_white = (248, 250, 255)
        carton_shade = (215, 222, 235)
        dark = (32, 38, 52)

        # Drop shadow
        body_rect = pygame.Rect(x - 0.55 * sk, y - 0.25 * sk, 1.10 * sk, 1.20 * sk)
        pygame.draw.rect(surf, (0, 0, 0, 45), body_rect.move(2 * k, 3 * k), border_radius=int(3 * k))

        # Main lower body (Paper carton)
        pygame.draw.rect(surf, carton_white, body_rect, border_radius=int(3 * k))
        # Blue lower brand banner
        banner_rect = pygame.Rect(body_rect.left, y + 0.15 * sk, body_rect.w, 0.80 * sk)
        pygame.draw.rect(surf, carton_blue, banner_rect, border_bottom_left_radius=int(3 * k), border_bottom_right_radius=int(3 * k))

        # Carton Gabled Gable Peak (Roof)
        roof_pts = [
            (x - 0.55 * sk, y - 0.25 * sk),
            (x - 0.40 * sk, y - 0.70 * sk),
            (x + 0.40 * sk, y - 0.70 * sk),
            (x + 0.55 * sk, y - 0.25 * sk),
        ]
        pygame.draw.polygon(surf, carton_white, roof_pts)
        pygame.draw.polygon(surf, carton_shade, [
            (x, y - 0.70 * sk), (x + 0.40 * sk, y - 0.70 * sk),
            (x + 0.55 * sk, y - 0.25 * sk), (x, y - 0.25 * sk)
        ])

        # Top sealed spout clip / crimp ridge
        crimp_rect = pygame.Rect(x - 0.45 * sk, y - 0.88 * sk, 0.90 * sk, 0.18 * sk)
        pygame.draw.rect(surf, carton_blue, crimp_rect, border_radius=int(2 * k))
        pygame.draw.rect(surf, dark, crimp_rect, max(1, int(1.5 * k)), border_radius=int(2 * k))

        # Cow spot graphic on carton face
        pygame.draw.ellipse(surf, dark, pygame.Rect(x - 0.32 * sk, y + 0.32 * sk, 0.35 * sk, 0.22 * sk))
        pygame.draw.ellipse(surf, dark, pygame.Rect(x + 0.05 * sk, y + 0.42 * sk, 0.28 * sk, 0.20 * sk))

        # Text label
        _outlined_text(surf, "MILK", int(sk * 0.42), (x, y - 0.05 * sk), carton_blue, outline=carton_white)

        # Outlines
        pygame.draw.rect(surf, dark, body_rect, max(1, int(2 * k)), border_radius=int(3 * k))
        pygame.draw.polygon(surf, dark, roof_pts, max(1, int(2 * k)))

    _supersample_draw(surface, cx, cy, s * 2.4, s * 2.6, _draw)


def _barn(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        barn_red = (195, 35, 35)
        barn_dark = (140, 20, 20)
        roof_gray = (75, 80, 92)
        roof_light = (120, 128, 145)
        white_trim = (245, 245, 250)
        dark = (35, 20, 22)

        # Drop shadow
        base_rect = pygame.Rect(x - 0.95 * sk, y - 0.05 * sk, 1.90 * sk, 0.95 * sk)
        pygame.draw.rect(surf, (0, 0, 0, 50), base_rect.move(2 * k, 3 * k))

        # Red Barn Walls
        pygame.draw.rect(surf, barn_red, base_rect)
        # Vertical wall plank lines
        for px_off in (-0.65, -0.35, 0.35, 0.65):
            pygame.draw.line(surf, barn_dark, (x + px_off * sk, base_rect.top), (x + px_off * sk, base_rect.bottom), max(1, int(1.2 * k)))

        # Mansard / Gambrel Barn Roof (Two-slope polygon)
        roof_pts = [
            (x - 1.10 * sk, y - 0.02 * sk),  # Eaves left
            (x - 0.85 * sk, y - 0.50 * sk),  # Lower slope knuckle left
            (x, y - 0.92 * sk),              # Apex ridge
            (x + 0.85 * sk, y - 0.50 * sk),  # Lower slope knuckle right
            (x + 1.10 * sk, y - 0.02 * sk),  # Eaves right
        ]
        pygame.draw.polygon(surf, roof_gray, roof_pts)
        pygame.draw.line(surf, roof_light, (x, y - 0.90 * sk), (x - 0.85 * sk, y - 0.48 * sk), max(1, int(2 * k)))
        pygame.draw.polygon(surf, dark, roof_pts, max(1, int(2 * k)))

        # White X Barn Doors
        door_w, door_h = 0.65 * sk, 0.70 * sk
        door_rect = pygame.Rect(x - door_w / 2, base_rect.bottom - door_h, door_w, door_h)
        pygame.draw.rect(surf, white_trim, door_rect)
        pygame.draw.rect(surf, barn_dark, door_rect.inflate(-4 * k, -4 * k))
        # Criss-cross X beams
        pygame.draw.line(surf, white_trim, (door_rect.left + 2 * k, door_rect.top + 2 * k), (door_rect.right - 2 * k, door_rect.bottom - 2 * k), max(1, int(2.5 * k)))
        pygame.draw.line(surf, white_trim, (door_rect.left + 2 * k, door_rect.bottom - 2 * k), (door_rect.right - 2 * k, door_rect.top + 2 * k), max(1, int(2.5 * k)))
        pygame.draw.rect(surf, dark, door_rect, max(1, int(2 * k)))

        # Hayloft Window
        loft = pygame.Rect(x - 0.22 * sk, y - 0.52 * sk, 0.44 * sk, 0.35 * sk)
        pygame.draw.rect(surf, dark, loft, border_top_left_radius=int(6 * k), border_top_right_radius=int(6 * k))
        pygame.draw.rect(surf, white_trim, loft, max(1, int(1.5 * k)), border_top_left_radius=int(6 * k), border_top_right_radius=int(6 * k))

        pygame.draw.rect(surf, dark, base_rect, max(1, int(2 * k)))

    _supersample_draw(surface, cx, cy, s * 2.6, s * 2.5, _draw)


def _tractor(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        green_body = (35, 145, 55)
        green_light = (65, 185, 85)
        yellow_rim = (252, 212, 35)
        tire_rubber = (38, 42, 48)
        dark = (22, 26, 30)

        # 1. Big Rear Tire & Rim
        rw_r = 0.48 * sk
        rx_c, ry_c = x - 0.45 * sk, y + 0.38 * sk
        pygame.draw.circle(surf, (0, 0, 0, 50), (rx_c + 2 * k, ry_c + 3 * k), rw_r)
        pygame.draw.circle(surf, tire_rubber, (rx_c, ry_c), rw_r)
        # Deep tire treads (radial ticks)
        for deg in range(0, 360, 40):
            rad = math.radians(deg)
            pygame.draw.line(surf, dark, (rx_c + math.cos(rad) * (rw_r * 0.72), ry_c + math.sin(rad) * (rw_r * 0.72)),
                             (rx_c + math.cos(rad) * rw_r, ry_c + math.sin(rad) * rw_r), max(1, int(2 * k)))
        pygame.draw.circle(surf, yellow_rim, (rx_c, ry_c), rw_r * 0.58)
        pygame.draw.circle(surf, dark, (rx_c, ry_c), rw_r * 0.58, max(1, int(1.5 * k)))
        pygame.draw.circle(surf, dark, (rx_c, ry_c), rw_r * 0.18)

        # 2. Green Hood & Engine Block
        hood = pygame.Rect(x - 0.35 * sk, y - 0.05 * sk, 1.25 * sk, 0.45 * sk)
        pygame.draw.rect(surf, green_body, hood, border_top_right_radius=int(6 * k))
        pygame.draw.line(surf, green_light, (hood.left, hood.top + 2 * k), (hood.right - 4 * k, hood.top + 2 * k), max(1, int(2 * k)))
        # Grille bars
        pygame.draw.rect(surf, dark, (hood.right - 0.18 * sk, hood.top + 0.08 * sk, 0.14 * sk, hood.h - 0.16 * sk), border_radius=int(2 * k))

        # 3. Open Cab Roll-Bar & Roof
        pygame.draw.line(surf, dark, (rx_c - 0.15 * sk, ry_c - rw_r), (rx_c - 0.15 * sk, y - 0.85 * sk), max(1, int(2.5 * k)))
        pygame.draw.line(surf, dark, (x + 0.05 * sk, hood.top), (x + 0.05 * sk, y - 0.85 * sk), max(1, int(2.5 * k)))
        cab_roof = pygame.Rect(rx_c - 0.28 * sk, y - 0.92 * sk, 0.72 * sk, 0.14 * sk)
        pygame.draw.rect(surf, green_body, cab_roof, border_radius=int(2 * k))
        pygame.draw.rect(surf, dark, cab_roof, max(1, int(1.5 * k)), border_radius=int(2 * k))

        # 4. Vertical Exhaust Pipe
        pygame.draw.line(surf, dark, (x + 0.55 * sk, hood.top), (x + 0.55 * sk, y - 0.65 * sk), max(1, int(2.5 * k)))
        pygame.draw.circle(surf, dark, (x + 0.55 * sk, y - 0.67 * sk), max(1 * k, sk * 0.05))

        # 5. Small Front Tire
        fw_r = 0.26 * sk
        fx_c, fy_c = x + 0.65 * sk, y + 0.60 * sk
        pygame.draw.circle(surf, tire_rubber, (fx_c, fy_c), fw_r)
        pygame.draw.circle(surf, yellow_rim, (fx_c, fy_c), fw_r * 0.55)
        pygame.draw.circle(surf, dark, (fx_c, fy_c), fw_r * 0.55, max(1, int(1.5 * k)))
        pygame.draw.circle(surf, dark, (fx_c, fy_c), fw_r * 0.18)

        pygame.draw.rect(surf, dark, hood, max(1, int(2 * k)), border_top_right_radius=int(6 * k))

    _supersample_draw(surface, cx, cy, s * 2.6, s * 2.5, _draw)


def _farmer(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        face = (248, 205, 168)
        dark_skin = (175, 120, 85)
        denim = (55, 95, 165)
        straw = (235, 195, 80)
        straw_dark = (145, 105, 30)
        dark = (35, 30, 28)

        # 1. Denim Overalls / Shoulders
        body_pts = [
            (x - 0.90 * sk, y + 0.95 * sk),
            (x - 0.65 * sk, y + 0.40 * sk),
            (x + 0.65 * sk, y + 0.40 * sk),
            (x + 0.90 * sk, y + 0.95 * sk),
        ]
        pygame.draw.polygon(surf, denim, body_pts)
        # Red flannel collar peek
        pygame.draw.polygon(surf, (200, 35, 35), [(x - 0.35 * sk, y + 0.40 * sk), (x + 0.35 * sk, y + 0.40 * sk), (x, y + 0.60 * sk)])
        # Overall strap buckles
        for bx in (-0.32 * sk, 0.32 * sk):
            pygame.draw.circle(surf, (225, 185, 45), (x + bx, y + 0.55 * sk), max(1 * k, sk * 0.07))
        pygame.draw.polygon(surf, dark, body_pts, max(1, int(2 * k)))

        # 2. Friendly Head & Ears
        for ex in (-0.52 * sk, 0.52 * sk):
            pygame.draw.circle(surf, face, (x + ex, y + 0.05 * sk), sk * 0.18)
            pygame.draw.circle(surf, dark_skin, (x + ex, y + 0.05 * sk), sk * 0.18, max(1, int(1.2 * k)))
        pygame.draw.circle(surf, face, (x, y + 0.02 * sk), sk * 0.54)

        # Rosy cheeks & cheerful smile
        pygame.draw.circle(surf, (255, 150, 150), (x - 0.30 * sk, y + 0.15 * sk), sk * 0.10)
        pygame.draw.circle(surf, (255, 150, 150), (x + 0.30 * sk, y + 0.15 * sk), sk * 0.10)
        # Smile arc
        pygame.draw.arc(surf, dark, pygame.Rect(x - 0.22 * sk, y + 0.05 * sk, 0.44 * sk, 0.30 * sk), math.pi * 1.1, math.pi * 1.9, max(1, int(2.5 * k)))
        # Cheerful eyes
        pygame.draw.circle(surf, dark, (x - 0.18 * sk, y - 0.02 * sk), sk * 0.07)
        pygame.draw.circle(surf, dark, (x + 0.18 * sk, y - 0.02 * sk), sk * 0.07)

        # 3. Straw Hat (Wide brim + crown)
        brim = pygame.Rect(x - 1.10 * sk, y - 0.38 * sk, 2.20 * sk, 0.42 * sk)
        pygame.draw.ellipse(surf, straw, brim)
        pygame.draw.ellipse(surf, straw_dark, brim, max(1, int(1.8 * k)))

        crown = pygame.Rect(x - 0.48 * sk, y - 0.88 * sk, 0.96 * sk, 0.65 * sk)
        pygame.draw.rect(surf, straw, crown, border_top_left_radius=int(8 * k), border_top_right_radius=int(8 * k))
        # Blue hat band
        band = pygame.Rect(crown.left, crown.bottom - int(0.18 * sk), crown.w, int(0.16 * sk))
        pygame.draw.rect(surf, denim, band)
        pygame.draw.rect(surf, straw_dark, crown, max(1, int(1.8 * k)), border_top_left_radius=int(8 * k), border_top_right_radius=int(8 * k))

    _supersample_draw(surface, cx, cy, s * 2.6, s * 2.6, _draw)


def _ufo(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        saucer_top = (175, 185, 205)
        saucer_glow = (225, 235, 255)
        saucer_base = (75, 82, 100)
        dome_glass = (110, 235, 245)
        dome_glow = (215, 255, 255)
        neon_cyan = (40, 240, 255)
        dark = (22, 25, 35)

        # 1. Cockpit Glass Dome (Hemisphere with reflection)
        dome_rect = pygame.Rect(x - 0.46 * sk, y - 0.68 * sk, 0.92 * sk, 0.72 * sk)
        pygame.draw.ellipse(surf, dome_glass, dome_rect)
        pygame.draw.ellipse(surf, dome_glow, dome_rect.inflate(-0.25 * sk, -0.25 * sk).move(-0.05 * sk, -0.05 * sk))
        pygame.draw.ellipse(surf, dark, dome_rect, max(1, int(1.8 * k)))

        # 2. Main Saucer Disk Silhouette (Top flare and bottom rim)
        disk_shadow = pygame.Rect(x - 1.15 * sk, y - 0.12 * sk, 2.30 * sk, 0.75 * sk)
        pygame.draw.ellipse(surf, (0, 0, 0, 50), disk_shadow.move(0, 3 * k))
        pygame.draw.ellipse(surf, saucer_base, disk_shadow)

        upper_disk = pygame.Rect(x - 1.15 * sk, y - 0.28 * sk, 2.30 * sk, 0.60 * sk)
        pygame.draw.ellipse(surf, saucer_top, upper_disk)
        pygame.draw.ellipse(surf, saucer_glow, upper_disk.inflate(-0.35 * sk, -0.15 * sk))
        pygame.draw.ellipse(surf, dark, upper_disk, max(1, int(2 * k)))

        # 3. Glowing Cyan Porch Thrusters / Lights
        for lx in (-0.75, -0.40, 0.0, 0.40, 0.75):
            pos = (x + lx * sk, y + 0.18 * sk)
            pygame.draw.circle(surf, neon_cyan, pos, max(2 * k, sk * 0.10))
            pygame.draw.circle(surf, (255, 255, 255), pos, max(1 * k, sk * 0.04))

        pygame.draw.ellipse(surf, dark, disk_shadow, max(1, int(2 * k)))

    _supersample_draw(surface, cx, cy, s * 2.8, s * 2.4, _draw)


def _golden_jug(surface, cx, cy, s, multiplier=None):
    def _draw(surf, x, y, k):
        sk = s * k
        gold_shadow = (145, 95, 12)
        gold_base = (245, 185, 30)
        gold_light = (255, 225, 90)
        gold_gleam = (255, 250, 195)
        dark = (42, 30, 8)

        # 1. Milk Can Handles on both shoulders
        for hx, rot in ((-0.62 * sk, -1), (0.62 * sk, 1)):
            h_rect = pygame.Rect(x + hx - 0.12 * sk, y - 0.35 * sk, 0.24 * sk, 0.40 * sk)
            pygame.draw.rect(surf, dark, h_rect, border_radius=int(2 * k))
            pygame.draw.rect(surf, gold_shadow, h_rect.inflate(-2 * k, -2 * k), border_radius=int(2 * k))

        # 2. Main Milk Jug Canister Body
        body_poly = [
            (x - 0.55 * sk, y - 0.22 * sk),  # Neck joint left
            (x - 0.72 * sk, y + 0.05 * sk),  # Shoulder flare left
            (x - 0.68 * sk, y + 0.85 * sk),  # Base left
            (x + 0.68 * sk, y + 0.85 * sk),  # Base right
            (x + 0.72 * sk, y + 0.05 * sk),  # Shoulder flare right
            (x + 0.55 * sk, y - 0.22 * sk),  # Neck joint right
        ]
        pygame.draw.polygon(surf, (0, 0, 0, 50), [(px + 2 * k, py + 3 * k) for px, py in body_poly])
        pygame.draw.polygon(surf, gold_base, body_poly)

        # Shading highlight curve
        pygame.draw.polygon(surf, gold_light, [
            (x - 0.40 * sk, y - 0.20 * sk),
            (x - 0.25 * sk, y - 0.20 * sk),
            (x - 0.35 * sk, y + 0.80 * sk),
            (x - 0.52 * sk, y + 0.80 * sk),
        ])
        pygame.draw.polygon(surf, gold_shadow, [
            (x + 0.40 * sk, y - 0.15 * sk),
            (x + 0.70 * sk, y + 0.05 * sk),
            (x + 0.68 * sk, y + 0.85 * sk),
            (x + 0.45 * sk, y + 0.85 * sk),
        ])
        pygame.draw.polygon(surf, dark, body_poly, max(1, int(2 * k)))

        # 3. Top Neck Collar & Lid
        collar = pygame.Rect(x - 0.52 * sk, y - 0.50 * sk, 1.04 * sk, 0.30 * sk)
        pygame.draw.rect(surf, gold_base, collar, border_radius=int(2 * k))
        pygame.draw.line(surf, gold_gleam, (collar.left + 2 * k, collar.top + 2 * k), (collar.right - 2 * k, collar.top + 2 * k), max(1, int(1.5 * k)))
        pygame.draw.rect(surf, dark, collar, max(1, int(1.8 * k)), border_radius=int(2 * k))

        lid = pygame.Rect(x - 0.35 * sk, y - 0.70 * sk, 0.70 * sk, 0.22 * sk)
        pygame.draw.rect(surf, gold_light, lid, border_radius=int(2 * k))
        pygame.draw.rect(surf, dark, lid, max(1, int(1.8 * k)), border_radius=int(2 * k))

        # Center embossed label / multiplier text
        if multiplier is not None:
            _outlined_text(surf, f"{multiplier}x", int(sk * 0.52), (x, y + 0.35 * sk), (255, 255, 255), outline=dark)
        else:
            _outlined_text(surf, "$", int(sk * 0.60), (x, y + 0.35 * sk), gold_gleam, outline=dark)

    _supersample_draw(surface, cx, cy, s * 2.5, s * 2.6, _draw)


def _boss_cow(surface, cx, cy, s):
    def _draw(surf, x, y, k):
        sk = s * k
        cow_white = (248, 250, 255)
        cow_spot = (28, 30, 36)
        snout_pink = (255, 175, 185)
        horn_color = (235, 215, 165)
        shades_black = (15, 18, 24)
        gold = (255, 210, 45)
        dark = (25, 28, 32)

        # 1. Pointed Horns on Top
        horn_l = [(x - 0.45 * sk, y - 0.45 * sk), (x - 0.85 * sk, y - 0.85 * sk), (x - 0.32 * sk, y - 0.65 * sk)]
        horn_r = [(x + 0.45 * sk, y - 0.45 * sk), (x + 0.85 * sk, y - 0.85 * sk), (x + 0.32 * sk, y - 0.65 * sk)]
        pygame.draw.polygon(surf, horn_color, horn_l)
        pygame.draw.polygon(surf, horn_color, horn_r)
        pygame.draw.polygon(surf, dark, horn_l, max(1, int(1.5 * k)))
        pygame.draw.polygon(surf, dark, horn_r, max(1, int(1.5 * k)))

        # 2. Floppy Ears
        for ex, rot in ((-0.75 * sk, -1), (0.75 * sk, 1)):
            ear = pygame.Rect(x + ex - 0.20 * sk, y - 0.25 * sk, 0.40 * sk, 0.22 * sk)
            pygame.draw.ellipse(surf, cow_white, ear)
            pygame.draw.ellipse(surf, snout_pink, ear.inflate(-0.12 * sk, -0.06 * sk))
            pygame.draw.ellipse(surf, dark, ear, max(1, int(1.5 * k)))

        # 3. Main Cow Head Silhouette & Spots
        head_rect = pygame.Rect(x - 0.62 * sk, y - 0.58 * sk, 1.24 * sk, 1.10 * sk)
        pygame.draw.ellipse(surf, (0, 0, 0, 50), head_rect.move(2 * k, 3 * k))
        pygame.draw.ellipse(surf, cow_white, head_rect)

        # Black Holstein patch over left eye
        pygame.draw.circle(surf, cow_spot, (x - 0.35 * sk, y - 0.20 * sk), sk * 0.35)

        # 4. Wide Pink Snout / Muzzle
        snout = pygame.Rect(x - 0.55 * sk, y + 0.08 * sk, 1.10 * sk, 0.55 * sk)
        pygame.draw.ellipse(surf, snout_pink, snout)
        # Nostrils
        pygame.draw.ellipse(surf, dark, pygame.Rect(x - 0.28 * sk, y + 0.24 * sk, 0.16 * sk, 0.22 * sk))
        pygame.draw.ellipse(surf, dark, pygame.Rect(x + 0.12 * sk, y + 0.24 * sk, 0.16 * sk, 0.22 * sk))
        pygame.draw.ellipse(surf, dark, snout, max(1, int(1.8 * k)))

        # 5. Slick Wayfarer / Aviator Sunglasses ("Boss Cow")
        # Thick black sunglasses frames
        lens_l = pygame.Rect(x - 0.58 * sk, y - 0.32 * sk, 0.52 * sk, 0.35 * sk)
        lens_r = pygame.Rect(x + 0.06 * sk, y - 0.32 * sk, 0.52 * sk, 0.35 * sk)
        pygame.draw.rect(surf, shades_black, lens_l, border_radius=int(4 * k))
        pygame.draw.rect(surf, shades_black, lens_r, border_radius=int(4 * k))
        # Bridge
        pygame.draw.rect(surf, shades_black, (x - 0.08 * sk, y - 0.28 * sk, 0.16 * sk, 0.10 * sk))
        # Specular glint reflection on lenses
        pygame.draw.line(surf, (220, 240, 255), (lens_l.left + 4 * k, lens_l.top + 3 * k), (lens_l.left + 0.28 * sk, lens_l.bottom - 4 * k), max(1, int(2 * k)))
        pygame.draw.line(surf, (220, 240, 255), (lens_r.left + 4 * k, lens_r.top + 3 * k), (lens_r.left + 0.28 * sk, lens_r.bottom - 4 * k), max(1, int(2 * k)))

        # 6. Gold Horseshoe Chain / Medallion at collar
        pygame.draw.circle(surf, gold, (x, y + 0.72 * sk), sk * 0.18)
        pygame.draw.circle(surf, dark, (x, y + 0.72 * sk), sk * 0.18, max(1, int(1.5 * k)))

        pygame.draw.ellipse(surf, dark, head_rect, max(1, int(2 * k)))

    _supersample_draw(surface, cx, cy, s * 2.6, s * 2.6, _draw)
 
 
def draw_golden_jug(surface, rect, multiplier=None, scale=0.35):
    """Draw a golden milk jug with an optional multiplier centered in rect."""
    cx, cy = rect.center
    s = min(rect.w, rect.h) * scale
    _golden_jug(surface, cx, cy, s, multiplier=multiplier)
 
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
    "gold_sack": _gold_sack, "mine_cart": _mine_cart,
    
    # Cows Gone Wild
    "milk_carton": _milk_carton, "barn": _barn, "tractor": _tractor, "farmer": _farmer,
    "ufo": _ufo, "boss_cow": _boss_cow,
    "golden_jug": _golden_jug
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