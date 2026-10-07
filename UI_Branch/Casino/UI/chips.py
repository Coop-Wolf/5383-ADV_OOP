import math
import pygame
from UI.widgets import Button
from UI.constants import (
    WIDTH, HEIGHT, FELT_GREEN, WHITE, BLACK, GOLD, GRAY, LIGHT_GRAY, DARK_GREEN,
    FONT_NAME, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL,)
 
 
# (value, chip color, edge stripe color, label color)
CHIP_TYPES = [
    (1,   (240, 240, 240), (150, 150, 160), BLACK),   # white
    (10,  (30, 140, 60),   WHITE,           WHITE),   # green
    (50,  (190, 35, 35),   WHITE,           WHITE),   # red
    (100, (35, 85, 200),   WHITE,           WHITE),   # blue
    (500, (30, 30, 30),    WHITE,           WHITE),   # black
]
 
 
def draw_chip(surface, center, radius, chip, font, dimmed=False):
    """
    Draw one casino chip using only pygame shapes.
    chip is a tuple from CHIP_TYPES.
    """
 
    value, color, stripe, text_color = chip
    cx, cy = center
 
    # Drop shadow
    pygame.draw.circle(surface, DARK_GREEN, (cx + 2, cy + 3), radius)
 
    # Chip body
    pygame.draw.circle(surface, color, center, radius)
 
    # Edge stripes: 8 small blocks around the rim
    inner_edge = radius * 0.78
    half_width = math.radians(11)
    for i in range(8):
        angle = math.radians(i * 45)
        a1, a2 = angle - half_width, angle + half_width
        points = [
            (cx + radius * math.cos(a1), cy + radius * math.sin(a1)),
            (cx + radius * math.cos(a2), cy + radius * math.sin(a2)),
            (cx + inner_edge * math.cos(a2), cy + inner_edge * math.sin(a2)),
            (cx + inner_edge * math.cos(a1), cy + inner_edge * math.sin(a1)),
        ]
        pygame.draw.polygon(surface, stripe, points)
 
    # Outer border and inner ring
    pygame.draw.circle(surface, stripe, center, radius, width=2)
    pygame.draw.circle(surface, stripe, center, int(radius * 0.68), width=2)
 
    # Value label
    label = font.render(f"${value}", True, text_color)
    surface.blit(label, label.get_rect(center=center))
 
    # Dim the chip if the player can't afford it
    if dimmed:
        size = radius * 2
        shade = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(shade, (0, 0, 0, 140), (radius, radius), radius)
        surface.blit(shade, (cx - radius, cy - radius))
 
 
def _draw_disabled(surface, button):
    pygame.draw.rect(surface, GRAY, button.rect, border_radius=8)
    pygame.draw.rect(surface, LIGHT_GRAY, button.rect, width=2, border_radius=8)
    label = button.font.render(button.text, True, LIGHT_GRAY)
    surface.blit(label, label.get_rect(center=button.rect.center))
 
 
class BetPanel:
    """
    Clickable chip betting area, shared by every game screen.
 
    - Click a chip in the tray to add it to the bet.
    - Click a stack on the table to take one chip back off.
    - handle_event() returns True when the Deal button is clicked.
    - Read the final wager from panel.bet.
    """
 
    CHIP_RADIUS = 38        # chips in the tray
    STACK_RADIUS = 34       # chips on the table
    STACK_OFFSET = 6        # vertical spacing inside a stack
    MAX_DRAWN = 8           # most chips drawn per stack (count label covers the rest)
    STACK_SPACING = 90
 
    TRAY_Y = 625
    STACK_BASE_Y = 400
 
    def __init__(self, balance, min_bet=1):
        self.min_bet = min_bet
        self.font = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)
        self.big_font = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
 
        # Chip tray along the bottom
        self.tray = []
        middle = (len(CHIP_TYPES) - 1) / 2
        for i, chip in enumerate(CHIP_TYPES):
            x = int(WIDTH // 2 + (i - middle) * 110)
            self.tray.append((chip, (x, self.TRAY_Y)))
 
        self.clear_button = Button(WIDTH // 2 - 170, 515, 150, 50, "Clear")
        self.deal_button = Button(WIDTH // 2 + 20, 515, 150, 50, "Deal")
 
        self.reset(balance)
 
    # State
    def reset(self, balance):
        """Start a fresh bet. Call this at the start of every round."""
        self.balance = balance
        self.counts = {chip[0]: 0 for chip in CHIP_TYPES}
 
    @property
    def bet(self):
        return sum(value * count for value, count in self.counts.items())
 
    @property
    def remaining(self):
        return self.balance - self.bet
 
    @property
    def can_deal(self):
        return self.bet >= self.min_bet
 
    # Layout helpers
    def _stack_layout(self):
        """Return [(chip, center_x, count)] for each denomination in the bet."""
        active = [(chip, self.counts[chip[0]]) for chip in CHIP_TYPES if self.counts[chip[0]] > 0]
        layout = []
        for i, (chip, count) in enumerate(active):
            x = int(WIDTH // 2 + (i - (len(active) - 1) / 2) * self.STACK_SPACING)
            layout.append((chip, x, count))
        return layout
 
    def _stack_rect(self, cx, count):
        drawn = min(count, self.MAX_DRAWN)
        r = self.STACK_RADIUS
        height = (drawn - 1) * self.STACK_OFFSET + 2 * r
        top = self.STACK_BASE_Y - (drawn - 1) * self.STACK_OFFSET - r
        return pygame.Rect(cx - r, top, 2 * r, height)
 
    @staticmethod
    def _in_circle(pos, center, radius):
        return (pos[0] - center[0]) ** 2 + (pos[1] - center[1]) ** 2 <= radius ** 2
 
    # Events
    def handle_event(self, event):
        """Returns True if Deal was clicked with a valid bet."""
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
 
        # Add a chip from the tray (only if the player can afford it)
        for chip, center in self.tray:
            if self._in_circle(event.pos, center, self.CHIP_RADIUS) and chip[0] <= self.remaining:
                self.counts[chip[0]] += 1
                return False
 
        # Take a chip back off a stack
        for chip, cx, count in self._stack_layout():
            if self._stack_rect(cx, count).collidepoint(event.pos):
                self.counts[chip[0]] -= 1
                return False
 
        if self.bet > 0 and self.clear_button.handle_event(event):
            self.counts = {chip[0]: 0 for chip in CHIP_TYPES}
            return False
 
        if self.can_deal and self.deal_button.handle_event(event):
            return True
 
        return False
 
    # Drawing
    def draw(self, surface):
        # Bet total
        total = self.big_font.render(f"Bet: ${self.bet}", True, GOLD)
        surface.blit(total, total.get_rect(center=(WIDTH // 2, 250)))
 
        # Chips on the table
        layout = self._stack_layout()
        if not layout:
            hint = self.font.render("Click the chips below to place your bet", True, LIGHT_GRAY)
            surface.blit(hint, hint.get_rect(center=(WIDTH // 2, self.STACK_BASE_Y)))
 
        for chip, cx, count in layout:
            for i in range(min(count, self.MAX_DRAWN)):
                y = self.STACK_BASE_Y - i * self.STACK_OFFSET
                draw_chip(surface, (cx, y), self.STACK_RADIUS, chip, self.font)
            if count > 1:
                num = self.font.render(f"x{count}", True, WHITE)
                surface.blit(num, num.get_rect(center=(cx, self.STACK_BASE_Y + self.STACK_RADIUS + 16)))
 
        # Buttons
        if self.bet > 0:
            self.clear_button.draw(surface)
        else:
            _draw_disabled(surface, self.clear_button)
 
        if self.can_deal:
            self.deal_button.draw(surface)
        else:
            _draw_disabled(surface, self.deal_button)
 
        # Chip tray
        mouse = pygame.mouse.get_pos()
        for chip, center in self.tray:
            affordable = chip[0] <= self.remaining
            if affordable and self._in_circle(mouse, center, self.CHIP_RADIUS):
                pygame.draw.circle(surface, GOLD, center, self.CHIP_RADIUS + 4, width=3)
            draw_chip(surface, center, self.CHIP_RADIUS, chip, self.font, dimmed=not affordable)
 
 
# Quick visual check: run from the project root with  python -m UI.chips
if __name__ == "__main__":
    pygame.init()
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    panel = BetPanel(balance=1250)
 
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif panel.handle_event(event):
                print(f"Deal clicked with a bet of ${panel.bet}")
 
        window.fill(FELT_GREEN)
        panel.draw(window)
        pygame.display.flip()
        clock.tick(60)
 
    pygame.quit()