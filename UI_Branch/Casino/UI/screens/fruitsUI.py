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
from UI.reel import Reel
from UI.symbols import draw_symbol
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
        self.reels = [Reel(
                rect=pygame.Rect(left + i * (reel_w + gap),top,reel_w,120,),
                rng=self.rng,machine=self.game,rows=1,cell_height=120,
                reel_bg=REEL_BG,cell_border=DARK,) for i in range(3)]

        self.frame = pygame.Rect(left, top, total, 120).inflate(28, 28)

        # BUTTONS
        self.menu_button = Button(30, 630, 120, 45, "Menu", font_size=FONT_SIZE_SMALL)
 
        btn_w, btn_h, btn_gap = 110, 55, 14
        row_w = len(BETS) * btn_w + (len(BETS) - 1) * btn_gap
        row_x = (WIDTH - row_w) // 2
        self.bet_buttons = [
            (bet, Button(row_x + i * (btn_w + btn_gap), 500, btn_w, btn_h, f"${bet}"))
            for i, bet in enumerate(BETS)]
 
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
            reel.draw(surface, draw_symbol)
 
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