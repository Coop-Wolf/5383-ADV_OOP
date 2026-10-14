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
import random
import math
from .screenUI import Screen
from UI.widgets import Button
from Classes.player import Player
from Classes.Slots.fruits import Fruits
from UI.slots_helper import Reel, draw_slot_panel, draw_paytable_panel
from UI.symbols import draw_symbol, get_font
from UI.constants import (
    WIDTH,
    FELT_GREEN,
    WHITE,
    GOLD,
    LIGHT_RED,
    FONT_SIZE_TITLE,
    FONT_SIZE_LARGE,
    FONT_SIZE_MEDIUM,
    FONT_SIZE_SMALL,
    BETS,
    DARK,
    GREY,
    REEL_BG,
)


class FruitsUI(Screen):

    def __init__(self, app, menu, machine=Fruits):
        super().__init__(app)
        self.menu = menu

        self.title_font = get_font(FONT_SIZE_TITLE, True)
        self.large = get_font(FONT_SIZE_LARGE, True)
        self.med = get_font(FONT_SIZE_MEDIUM)
        self.small = get_font(FONT_SIZE_SMALL)

        casino_player = Player(app.player["username"], app.player["chips"], app.player["id"])

        # GAME
        self.machine = machine
        self.game = machine(casino_player, db=app.db)
        self.rng = random.Random()

        # REELS
        reel_w, gap = 130, 16
        total = 3 * reel_w + 2 * gap
        left = (WIDTH - total) // 2
        top = 200
        self.reels = [
            Reel(
                rect=pygame.Rect(left + i * (reel_w + gap), top, reel_w, 120),
                rng=self.rng,
                machine=self.game,
                rows=1,
                cell_height=120,
                reel_bg=REEL_BG,
                cell_border=DARK,
            )
            for i in range(3)
        ]

        self.frame = pygame.Rect(left, top, total, 120).inflate(28, 28)

        # BUTTONS
        self.menu_button = Button(30, 630, 120, 45, "Menu", font_size=FONT_SIZE_SMALL)

        btn_w, btn_h, btn_gap = 110, 55, 14
        row_w = len(BETS) * btn_w + (len(BETS) - 1) * btn_gap
        row_x = (WIDTH - row_w) // 2
        self.bet_buttons = [
            (bet, Button(row_x + i * (btn_w + btn_gap), 530, btn_w, btn_h, f"${bet}"))
            for i, bet in enumerate(BETS)
        ]

        # Variables
        self.state = "IDLE"  # IDLE <-> SPIN
        self.bet = 0
        self.result = None
        self.shown_chips = app.player["chips"]
        self.message = ""
        self.message_color = WHITE
        self.result_ms = 0
        self.last_win = 0

    def _go_to_menu(self):
        self.app.change_screen(self.menu)

    def _spin(self, bet):
        chips_before = self.game.game_player.chips
        self.last_win = 0

        try:
            self.game.deal(bet)
        except ValueError:
            return

        self.result = self.game.determine_winner()
        self.app.player["chips"] = self.game.game_player.chips

        self.bet = bet
        self.shown_chips = chips_before - bet
        self.message = ""

        now = pygame.time.get_ticks()
        for i, reel in enumerate(self.reels):
            reel.start(
                self.result["reels"][i],
                duration_ms=1200 + 500 * i,
                now=now,
                extra_spins=14 + 4 * i,
            )

        self.state = "SPIN"

    def handle_event(self, event):
        if self.state == "SPIN":
            return

        if self.menu_button.handle_event(event):
            self._go_to_menu()
            return

        chips = self.shown_chips
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
        gross_win = self.result.get("net_change", 0) + self.bet if self.result.get("multiplier", 0) > 0 else 0
        self.last_win = max(0, gross_win)

    def draw(self, surface):
        surface.fill(FELT_GREEN)

        name = self.med.render(self.app.player["username"], True, WHITE)
        surface.blit(name, (30, 25))

        chips = self.med.render(f"Chips: {self.shown_chips}", True, GOLD)
        surface.blit(chips, chips.get_rect(topright=(WIDTH - 30, 25)))

        title = self.title_font.render("CLASSIC FRUITS", True, GOLD)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 110)))

        rules = self.small.render("Match three symbols to win. Two cherries on the left pay 1 to 1.", True, WHITE)
        surface.blit(rules, rules.get_rect(center=(WIDTH // 2, 165)))

        self._draw_paytable(surface)

        # Reels and frame
        pygame.draw.rect(surface, DARK, self.frame, border_radius=16)
        for reel in self.reels:
            reel.draw(surface, draw_symbol)

        if self.state == "IDLE" and self.result and self.result["multiplier"] > 0:
            pulse = math.sin((pygame.time.get_ticks() - self.result_ms) / 1000 * 8)
            width = 4 + int(3 * (1 + pulse) / 2)
            pygame.draw.rect(surface, GOLD, self.frame, width, border_radius=16)
        else:
            pygame.draw.rect(surface, GREY, self.frame, 3, border_radius=16)

        # Readout Panel
        draw_slot_panel(surface, WIDTH // 2, self.frame.bottom + 12, self.shown_chips, self.bet, self.last_win)

        # Bet controls
        chips_now = self.shown_chips
        if chips_now < 1 and self.state == "IDLE":
            prompt = self.small.render("You're out of chips!", True, LIGHT_RED)
        elif self.state != "IDLE":
            prompt = self.small.render("Reels spinning...", True, WHITE)
        else:
            prompt = self.small.render("Click a bet to spin", True, WHITE)
        surface.blit(prompt, prompt.get_rect(center=(WIDTH // 2, 508)))

        for bet, button in self.bet_buttons:
            if self.state == "IDLE" and bet <= chips_now:
                button.draw(surface)
            else:
                self._draw_disabled(surface, button.rect, f"${bet}")

        if self.state == "IDLE":
            self.menu_button.draw(surface)

    def _draw_paytable(self, surface):
        
        lines = [f"2x Cherry  {self.machine.TWO_CHERRY_PAYOUT}:1"]
        lines.extend(
            f"3x {symbol.title()}  {mult}:1"
            for symbol, mult in self.machine.PAYTABLE.items()
        )

        draw_paytable_panel(
            surface,
            rect=(20, 205, 225, 245),
            title=" ROW PAYS",
            lines=lines,
            text_color=WHITE,
        )

    def _draw_disabled(self, surface, rect, label):
        pygame.draw.rect(surface, GREY, rect, border_radius=10)
        pygame.draw.rect(surface, DARK, rect, 3, border_radius=10)
        text = self.med.render(label, True, DARK)
        surface.blit(text, text.get_rect(center=rect.center))