"""
 
Slots screen for the Casino App (Pygame).
 
    Flow:
    - Clicking a bet button ($1, $5, $10, $50, $100) takes the bet and spins at once.
    - The bet is settled and saved immediately (Slots.deal + determine_winner),
      so the result is final before any animation plays.
    - The reels then animate toward that result. The chip count and the win
      message are revealed when the last reel stops.
 
    The screen only draws and handles input; all game logic lives in Slots.
 
"""
 
import pygame
from functools import lru_cache
import random
import math
from .screenUI import Screen
from UI.widgets import Button
from Classes.player import Player
from Classes.Slots.fruits import Fruits
from UI.constants import (WIDTH, FELT_GREEN, WHITE, GOLD, LIGHT_RED, FONT_NAME, FONT_SIZE_TITLE, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL,)
 
BETS = [1, 5, 10, 50, 100]
DARK = (15, 15, 15)
GREY = (90, 90, 90)
REEL_BG = (245, 240, 225)
 
 
@lru_cache(maxsize=None)
def get_font(size, bold=False):
    font = pygame.font.Font(FONT_NAME, size)
    font.set_bold(bold)
    return font
 
 
# --------------------------------------------------------------------------
# Symbols (drawn with pygame shapes, no images)
# --------------------------------------------------------------------------
 
def draw_symbol(surface, name, rect):
    cx, cy = rect.center
    s = min(rect.w, rect.h) * 0.35
 
    if name == "cherry":
        pygame.draw.line(surface, (40, 120, 40), (cx - s * 0.45, cy + s * 0.2), (cx + s * 0.1, cy - s * 0.9), 4)
        pygame.draw.line(surface, (40, 120, 40), (cx + s * 0.45, cy + s * 0.2), (cx + s * 0.1, cy - s * 0.9), 4)
        pygame.draw.circle(surface, (200, 40, 40), (cx - s * 0.45, cy + s * 0.4), s * 0.5)
        pygame.draw.circle(surface, (200, 40, 40), (cx + s * 0.45, cy + s * 0.4), s * 0.5)
        pygame.draw.circle(surface, (255, 150, 150), (cx - s * 0.6, cy + s * 0.25), s * 0.12)
        pygame.draw.circle(surface, (255, 150, 150), (cx + s * 0.3, cy + s * 0.25), s * 0.12)
 
    elif name == "lemon":
        body = pygame.Rect(0, 0, int(s * 1.9), int(s * 1.25))
        body.center = (cx, cy)
        pygame.draw.ellipse(surface, (250, 225, 50), body)
        pygame.draw.ellipse(surface, (200, 170, 20), body, 3)
 
    elif name == "bar":
        body = pygame.Rect(0, 0, int(s * 1.95), int(s * 1.0))
        body.center = (cx, cy)
        pygame.draw.rect(surface, DARK, body, border_radius=8)
        pygame.draw.rect(surface, GOLD, body, 3, border_radius=8)
        label = get_font(int(s * 0.85), True).render("BAR", True, GOLD)
        surface.blit(label, label.get_rect(center=body.center))
 
    elif name == "bell":
        pygame.draw.circle(surface, GOLD, (cx, cy - s * 0.15), s * 0.65)
        pygame.draw.polygon(surface, GOLD, [
            (cx - s * 0.65, cy - s * 0.15), (cx + s * 0.65, cy - s * 0.15),
            (cx + s * 0.95, cy + s * 0.5), (cx - s * 0.95, cy + s * 0.5)])
        pygame.draw.circle(surface, (160, 120, 20), (cx, cy + s * 0.68), s * 0.18)
        pygame.draw.polygon(surface, (160, 120, 20), [
            (cx - s * 0.95, cy + s * 0.5), (cx + s * 0.95, cy + s * 0.5),
            (cx + s * 0.95, cy + s * 0.55), (cx - s * 0.95, cy + s * 0.55)], 2)
 
    elif name == "seven":
        text = get_font(int(s * 2.6), True).render("7", True, (200, 40, 40))
        outline = get_font(int(s * 2.6), True).render("7", True, DARK)
        r = text.get_rect(center=(cx, cy))
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            surface.blit(outline, r.move(dx, dy))
        surface.blit(text, r)
 
    elif name == "diamond":
        pts = [(cx, cy - s), (cx + s * 0.85, cy), (cx, cy + s), (cx - s * 0.85, cy)]
        pygame.draw.polygon(surface, (90, 210, 245), pts)
        pygame.draw.polygon(surface, (30, 120, 170), pts, 3)
        pygame.draw.line(surface, (200, 245, 255), (cx - s * 0.85, cy), (cx + s * 0.85, cy), 2)
        pygame.draw.line(surface, (200, 245, 255), (cx, cy - s), (cx - s * 0.3, cy), 2)
        pygame.draw.line(surface, (200, 245, 255), (cx, cy - s), (cx + s * 0.3, cy), 2)
 
 
# --------------------------------------------------------------------------
# One spinning reel (timed with pygame.time.get_ticks, like the other screens)
# --------------------------------------------------------------------------
 
class Reel:
 
    CELL = 120   # height of one symbol cell
 
    def __init__(self, rect, rng):
        self.rect = rect
        self.rng = rng
        self.strip = [self._random_symbol()]
        self.pos = 0.0           # which strip index is currently centered
        self.target = 0
        self.start_ms = 0
        self.duration = 1000
        self.spinning = False
 
    def _random_symbol(self):
        return self.rng.choices(list(Fruits.SYMBOLS), weights=list(Fruits.SYMBOLS.values()))[0]
 
    # Scroll from the symbol currently showing to the final one
    def start(self, final, rows, duration_ms, now):
        current = self.strip[int(round(self.pos))]
        self.strip = [current] + [self._random_symbol() for _ in range(rows - 1)] + [final]
        self.target = rows
        self.pos = 0.0
        self.start_ms = now
        self.duration = duration_ms
        self.spinning = True
 
    def update(self, now):
        if not self.spinning:
            return
        p = min((now - self.start_ms) / self.duration, 1.0)
        eased = 1 - (1 - p) ** 3          # ease-out: fast at first, settles gently
        self.pos = self.target * eased
        if p >= 1.0:
            self.pos = float(self.target)
            self.spinning = False
 
    def draw(self, surface):
        pygame.draw.rect(surface, REEL_BG, self.rect, border_radius=10)
 
        old_clip = surface.get_clip()
        surface.set_clip(self.rect)
        first = int(self.pos) - 1
        for i in range(first, first + 4):
            if 0 <= i < len(self.strip):
                cy = self.rect.centery + (self.pos - i) * self.CELL
                cell = pygame.Rect(self.rect.x, 0, self.rect.w, self.CELL)
                cell.centery = int(cy)
                draw_symbol(surface, self.strip[i], cell)
        surface.set_clip(old_clip)
 
        pygame.draw.rect(surface, DARK, self.rect, 3, border_radius=10)
 
 
# --------------------------------------------------------------------------
# The screen
# --------------------------------------------------------------------------
 
class FruitsUI(Screen):
 
    def __init__(self, app, menu, machine=Fruits):
        super().__init__(app)
        self.menu = menu
 
        self.title_font = pygame.font.Font(FONT_NAME, FONT_SIZE_TITLE)
        self.large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.med = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.small = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)
 
        casino_player = Player(app.player["username"], app.player["chips"], app.player["id"])
 
        # GAME
        self.game = machine(casino_player, db=app.db)
        self.rng = random.Random()
 
        # REELS
        reel_w, gap = 130, 16
        total = 3 * reel_w + 2 * gap
        left = (WIDTH - total) // 2
        top = 200
        self.reels = [
            Reel(pygame.Rect(left + i * (reel_w + gap), top, reel_w, Reel.CELL), self.rng)
            for i in range(3)
        ]
        self.frame = pygame.Rect(left, top, total, Reel.CELL).inflate(28, 28)
 
        # BUTTONS
        self.menu_button = Button(30, 630, 120, 45, "Menu", font_size=FONT_SIZE_SMALL)
 
        btn_w, btn_h, btn_gap = 110, 55, 14
        row_w = len(BETS) * btn_w + (len(BETS) - 1) * btn_gap
        row_x = (WIDTH - row_w) // 2
        self.bet_buttons = [
            (bet, Button(row_x + i * (btn_w + btn_gap), 500, btn_w, btn_h, f"${bet}"))
            for i, bet in enumerate(BETS)
        ]
 
        # Variables
        self.state = "IDLE"            # IDLE <-> SPIN
        self.bet = 0
        self.result = None
        self.shown_chips = app.player["chips"]
        self.message = ""
        self.message_color = WHITE
        self.result_ms = 0
 
    def _go_to_menu(self):
        self.app.change_screen(self.menu)
 
    def _spin(self, bet):
        chips_before = self.game.game_player.chips
 
        # Backend takes the bet and picks the reels
        try:
            self.game.deal(bet)
        except ValueError:
            return
 
        # Settle now; the animation only reveals the result
        self.result = self.game.determine_winner()
        self.app.player["chips"] = self.game.game_player.chips
 
        self.bet = bet
        self.shown_chips = chips_before - bet
        self.message = ""
 
        now = pygame.time.get_ticks()
        for i, reel in enumerate(self.reels):
            reel.start(self.result["reels"][i], rows=12 + 5 * i, duration_ms=1200 + 500 * i, now=now)
 
        self.state = "SPIN"
 
    def handle_event(self, event):
        if self.state == "SPIN":
            return
 
        if self.menu_button.handle_event(event):
            self._go_to_menu()
            return
 
        chips = self.game.game_player.chips
        for bet, button in self.bet_buttons:
            if bet <= chips and button.handle_event(event):
                self._spin(bet)
                return
 
    def update(self):
        now = pygame.time.get_ticks()
 
        for reel in self.reels:
            reel.update(now)
 
        if self.state == "SPIN" and not any(r.spinning for r in self.reels):
            self._finish_spin(now)
 
    def _finish_spin(self, now):
        self.state = "IDLE"
        self.result_ms = now
        self.shown_chips = self.app.player["chips"]
 
        if self.result["multiplier"] > 0:
            self.message = f"You win!  +${self.result['net_change']}"
            self.message_color = GOLD
        else:
            self.message = f"No match  -${self.bet}"
            self.message_color = LIGHT_RED
 
    def draw(self, surface):
        surface.fill(FELT_GREEN)
 
        name = self.med.render(self.app.player["username"], True, WHITE)
        surface.blit(name, (30, 25))
 
        chips = self.med.render(f"Chips: {self.shown_chips}", True, GOLD)
        surface.blit(chips, chips.get_rect(topright=(WIDTH - 30, 25)))
 
        title = self.title_font.render("SLOTS", True, GOLD)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 110)))
 
        rules = self.small.render("Match three symbols to win. Two cherries on the left pay 1 to 1.", True, WHITE)
        surface.blit(rules, rules.get_rect(center=(WIDTH // 2, 165)))
 
        self._draw_paytable(surface)
 
        # Reels and frame (the frame pulses gold after a win)
        pygame.draw.rect(surface, DARK, self.frame, border_radius=16)
        for reel in self.reels:
            reel.draw(surface)
 
        if self.state == "IDLE" and self.result and self.result["multiplier"] > 0:
            pulse = math.sin((pygame.time.get_ticks() - self.result_ms) / 1000 * 8)
            width = 4 + int(3 * (1 + pulse) / 2)
            pygame.draw.rect(surface, GOLD, self.frame, width, border_radius=16)
        else:
            pygame.draw.rect(surface, GREY, self.frame, 3, border_radius=16)
 
        # Result message and last bet
        if self.state == "IDLE" and self.message:
            msg = self.large.render(self.message, True, self.message_color)
            surface.blit(msg, msg.get_rect(center=(WIDTH // 2, self.frame.bottom + 40)))
 
        if self.result:
            bet = self.med.render(f"Bet: ${self.bet}", True, GOLD)
            surface.blit(bet, bet.get_rect(center=(WIDTH // 2, self.frame.bottom + 85)))
 
        # Bet buttons
        chips_now = self.game.game_player.chips
        if chips_now < 1 and self.state == "IDLE":
            out = self.med.render("You're out of chips!", True, LIGHT_RED)
            surface.blit(out, out.get_rect(center=(WIDTH // 2, 450)))
        else:
            prompt = self.med.render("Click a bet to spin", True, WHITE)
            surface.blit(prompt, prompt.get_rect(center=(WIDTH // 2, 450)))
 
        for bet, button in self.bet_buttons:
            if self.state == "IDLE" and bet <= chips_now:
                button.draw(surface)
            else:
                self._draw_disabled(surface, button.rect, f"${bet}")
 
        if self.state == "IDLE":
            self.menu_button.draw(surface)
 
    def _draw_paytable(self, surface):
        x, y = 30, 215
        head = self.small.render("PAYS", True, GOLD)
        surface.blit(head, (x, y))
        y += 28
        for symbol, mult in Fruits.PAYTABLE.items():
            line = self.small.render(f"3x {symbol.title()}  {mult}:1", True, WHITE)
            surface.blit(line, (x, y))
            y += 24
        line = self.small.render(f"2x Cherry  {Fruits.TWO_CHERRY_PAYOUT}:1", True, WHITE)
        surface.blit(line, (x, y))
 
    def _draw_disabled(self, surface, rect, label):
        pygame.draw.rect(surface, GREY, rect, border_radius=10)
        pygame.draw.rect(surface, DARK, rect, 3, border_radius=10)
        text = self.med.render(label, True, DARK)
        surface.blit(text, text.get_rect(center=rect.center))