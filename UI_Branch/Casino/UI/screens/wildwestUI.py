"""
Wild West slot-machine screen for the Casino App.

The WildWest backend owns all game rules and settles the round before the
animation begins. This screen only animates the returned grids and displays
the result, including any free spins already resolved by the backend.
"""

import math
import random
from functools import lru_cache
import pygame
from .screenUI import Screen
from UI.widgets import Button
from Classes.player import Player
from Classes.Slots.wildwest import WildWest
from UI.slots_helper import Reel, draw_slot_panel
from UI.symbols import draw_symbol
from UI.constants import (
    WIDTH,
    HEIGHT,
    FELT_GREEN,
    DARK_GREEN,
    WHITE,
    GOLD,
    LIGHT_RED,
    GRAY,
    FONT_NAME,
    FONT_SIZE_TITLE,
    FONT_SIZE_LARGE,
    FONT_SIZE_MEDIUM,
    FONT_SIZE_SMALL,
)

BETS = [1, 5, 10, 50, 100]

DARK = (15, 15, 15)
REEL_BG = (245, 240, 225)
CELL_BORDER = (185, 170, 135)
WIN_GOLD = (255, 210, 70)
SCATTER_RED = (150, 35, 35)

CELL_W = 118
CELL_H = 72
CELL_GAP = 8
COL_GAP = 10
GRID_ROWS = 4
GRID_COLS = 3


@lru_cache(maxsize=None)
def get_font(size, bold=False):
    font = pygame.font.Font(FONT_NAME, size)
    font.set_bold(bold)
    return font


class ReelColumn:
    """Animates one vertical column toward four predetermined symbols."""

    EXTRA_SYMBOLS = 12

    def __init__(self, rect, rng, machine):
        self.rect = pygame.Rect(rect)
        self.rng = rng
        self.machine = machine
        self.symbols = [next(iter(machine.SYMBOLS)) for _ in range(GRID_ROWS)]
        self.strip = list(self.symbols)
        self.position = 0.0
        self.target_position = 0.0
        self.start_ms = 0
        self.duration_ms = 1000
        self.spinning = False

    @property
    def pitch(self):
        return CELL_H + CELL_GAP

    def _random_symbol(self):
        names = list(self.machine.SYMBOLS.keys())
        weights = list(self.machine.SYMBOLS.values())
        return self.rng.choices(names, weights=weights, k=1)[0]

    def start(self, final_symbols, duration_ms, now):
        self.strip = (
            [self._random_symbol() for _ in range(self.EXTRA_SYMBOLS)]
            + list(final_symbols)
        )
        self.position = 0.0
        self.target_position = float(self.EXTRA_SYMBOLS)
        self.start_ms = now
        self.duration_ms = duration_ms
        self.spinning = True
        self.symbols = list(final_symbols)

    def update(self, now):
        if not self.spinning:
            return

        progress = min((now - self.start_ms) / self.duration_ms, 1.0)
        eased = 1 - (1 - progress) ** 3
        self.position = self.target_position * eased

        if progress >= 1.0:
            self.position = self.target_position
            self.spinning = False

    def draw(self, surface):
        old_clip = surface.get_clip()
        surface.set_clip(self.rect)

        first_index = max(0, int(self.position) - 1)
        last_index = min(
            len(self.strip) - 1,
            int(self.position) + GRID_ROWS,
        )

        for index in range(first_index, last_index + 1):
            y = self.rect.y + (index - self.position) * self.pitch
            cell = pygame.Rect(
                self.rect.x,
                int(y),
                self.rect.w,
                CELL_H,
            )
            if cell.bottom < self.rect.top or cell.top > self.rect.bottom:
                continue

            pygame.draw.rect(surface, REEL_BG, cell, border_radius=6)
            draw_symbol(surface, self.strip[index], cell)
            pygame.draw.rect(surface, CELL_BORDER, cell, 1, border_radius=6)

        surface.set_clip(old_clip)


class WildWestUI(Screen):
    """Four-row, three-column Wild West slot screen."""

    def __init__(self, app, menu, machine=WildWest):
        super().__init__(app)
        self.menu = menu
        self.machine = machine

        self.title_font = get_font(FONT_SIZE_TITLE, True)
        self.large = get_font(FONT_SIZE_LARGE, True)
        self.med = get_font(FONT_SIZE_MEDIUM)
        self.small = get_font(FONT_SIZE_SMALL)
        self.tiny = get_font(16)

        casino_player = Player(
            app.player["username"],
            app.player["chips"],
            app.player["id"],
        )
        self.game = machine(casino_player, db=app.db)
        self.rng = random.Random()

        grid_w = GRID_COLS * CELL_W + (GRID_COLS - 1) * COL_GAP
        grid_h = GRID_ROWS * CELL_H + (GRID_ROWS - 1) * CELL_GAP
        grid_x = (WIDTH - grid_w) // 2
        grid_y = 178

        self.grid_rect = pygame.Rect(grid_x, grid_y, grid_w, grid_h)
        self.columns = [
            ReelColumn(
                pygame.Rect(
                    grid_x + col * (CELL_W + COL_GAP),
                    grid_y,
                    CELL_W,
                    grid_h,
                ),
                self.rng,
                machine,
            )
            for col in range(GRID_COLS)
        ]

        self.menu_button = Button(
            30, 630, 120, 45, "Menu", font_size=FONT_SIZE_SMALL
        )

        btn_w, btn_h, btn_gap = 90, 45, 10
        buttons_width = len(BETS) * btn_w + (len(BETS) - 1) * btn_gap
        buttons_x = (WIDTH - buttons_width) // 2
        self.bet_buttons = [
            (
                bet,
                Button(
                    buttons_x + i * (btn_w + btn_gap),
                    610,
                    btn_w,
                    btn_h,
                    f"${bet}",
                    font_size=FONT_SIZE_SMALL,
                ),
            )
            for i, bet in enumerate(BETS)
        ]

        # Pop-up dialog buttons
        self.start_bonus_btn = Button(
            WIDTH // 2 - 80, 410, 160, 50, "Start Spins", font_size=FONT_SIZE_SMALL
        )
        self.collect_bonus_btn = Button(
            WIDTH // 2 - 80, 410, 160, 50, "Continue", font_size=FONT_SIZE_SMALL
        )

        # States: IDLE, SPIN, BONUS_MODAL, FREE_SPIN, FREE_SPIN_RESULT, BONUS_SUMMARY_MODAL
        self.state = "IDLE"
        self.bet = 0
        self.result = None
        self.current_grid = None
        self.current_wins = []
        self.features = {}
        self.free_spins = []
        self.free_spin_index = -1
        self.free_spin_accumulated_win = 0
        self.shown_chips = app.player["chips"]
        self.message = "Choose a bet to spin"
        self.message_color = WHITE
        self.result_ms = 0
        self.result_pause_until = 0

    def _go_to_menu(self):
        self.app.change_screen(self.menu)

    def _grid_column(self, grid, col):
        return [grid[row][col] for row in range(GRID_ROWS)]

    def _start_grid_animation(self, grid, now, duration_base=1050):
        self.current_grid = grid
        self.current_wins = []
        for col, reel in enumerate(self.columns):
            reel.start(
                self._grid_column(grid, col),
                duration_ms=duration_base + col * 350,
                now=now,
            )

    def _spin(self, bet):
        chips_before = self.game.game_player.chips

        try:
            self.game.deal(bet)
        except ValueError:
            self.message = "Not enough chips for that bet"
            self.message_color = LIGHT_RED
            return

        self.result = self.game.determine_winner()
        self.app.player["chips"] = self.game.game_player.chips

        self.bet = bet
        # Deduct bet visually right away, but hold back winnings until reels finish
        self.shown_chips = chips_before - bet
        self.features = self.result.get("features", {}) or {}
        self.free_spins = self.features.get("free_spins", []) or []
        self.free_spin_index = -1
        self.free_spin_accumulated_win = 0
        self.message = "Spinning..."
        self.message_color = WHITE

        now = pygame.time.get_ticks()
        self._start_grid_animation(self.result["grid"], now)
        self.state = "SPIN"

    def handle_event(self, event):
        if self.state == "BONUS_MODAL":
            if self.start_bonus_btn.handle_event(event):
                now = pygame.time.get_ticks()
                self.free_spin_index = 0
                self.state = "FREE_SPIN"
                self._start_free_spin(now)
            return

        if self.state == "BONUS_SUMMARY_MODAL":
            if self.collect_bonus_btn.handle_event(event):
                now = pygame.time.get_ticks()
                self._finish_round(now)
            return

        if self.state != "IDLE":
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
        for reel in self.columns:
            reel.update(now)

        if self.state in ("SPIN", "FREE_SPIN") and not any(
            reel.spinning for reel in self.columns
        ):
            self._finish_grid_animation(now)

        elif self.state == "FREE_SPIN_RESULT" and now >= self.result_pause_until:
            self.free_spin_index += 1
            if self.free_spin_index < len(self.free_spins):
                self.state = "FREE_SPIN"
                self._start_free_spin(now)
            else:
                # All free spins done: open summary popup
                self.state = "BONUS_SUMMARY_MODAL"

    def _finish_grid_animation(self, now):
        if self.state == "SPIN":
            self.current_wins = self.result.get("wins", []) or []

            # Add main spin payout to shown chips only now that reels stopped
            main_payout = sum(w.get("payout", 0) for w in self.current_wins)
            self.shown_chips += main_payout

            if self.free_spins:
                self.state = "BONUS_MODAL"
                return

            self._finish_round(now)
            return

        # Free spin settled
        free_spin = self.free_spins[self.free_spin_index]
        self.current_wins = free_spin.get("wins", []) or []
        spin_win = sum(w.get("payout", 0) for w in self.current_wins)
        self.free_spin_accumulated_win += spin_win
        self.shown_chips += spin_win

        self.state = "FREE_SPIN_RESULT"
        self.result_pause_until = now + 900

    def _start_free_spin(self, now):
        free_spin = self.free_spins[self.free_spin_index]
        self.current_wins = []
        self.message = (
            f"Free spin {self.free_spin_index + 1}/{len(self.free_spins)}"
        )
        self.message_color = WIN_GOLD
        self._start_grid_animation(
            free_spin["grid"],
            now,
            duration_base=800,
        )

    def _finish_round(self, now):
        self.state = "IDLE"
        self.result_ms = now
        self.shown_chips = self.app.player["chips"]
        self.current_wins = self.result.get("wins", []) or []

        net_change = self.result.get("net_change", 0)
        if net_change > 0:
            self.message = f"Round win! +${net_change}"
            self.message_color = WIN_GOLD
        else:
            self.message = f"No win  -${self.bet}"
            self.message_color = LIGHT_RED

        if self.free_spins:
            self.message += f"   ({len(self.free_spins)} free spins)"

    def draw(self, surface):
            surface.fill(FELT_GREEN)

            name = self.med.render(self.app.player["username"], True, WHITE)
            surface.blit(name, (30, 24))

            chips = self.med.render(f"Chips: {self.shown_chips}", True, GOLD)
            surface.blit(chips, chips.get_rect(topright=(WIDTH - 30, 24)))

            title = self.title_font.render("WILD WEST", True, GOLD)
            surface.blit(title, title.get_rect(center=(WIDTH // 2, 100)))

            subtitle_text = "Match symbols across a row. Outlaw is wild; 3 Saloon symbols trigger 8 free spins."
            subtitle = self.tiny.render(subtitle_text, True, WHITE)
            surface.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 145)))

            self._draw_paytable(surface)

            # Board backing and column reels
            pygame.draw.rect(
                surface,
                DARK_GREEN,
                self.grid_rect.inflate(16, 16),
                border_radius=14,
            )
            for reel in self.columns:
                reel.draw(surface)

            # Highlight only winning rows after the grid stops
            if self.state in ("IDLE", "FREE_SPIN_RESULT") and self.current_grid is not None:
                self._draw_winning_rows(surface)

            # Static outer border around the grid (no pulsing full-grid highlight)
            pygame.draw.rect(
                surface,
                GRAY,
                self.grid_rect.inflate(16, 16),
                2,
                border_radius=14,
            )

            self._draw_status(surface)
            self._draw_bet_controls(surface)

            if self.state == "IDLE":
                self.menu_button.draw(surface)

            # Modal Popups
            if self.state == "BONUS_MODAL":
                self._draw_modal(
                    surface,
                    title="SALOON BONUS!",
                    line1=f"You won {len(self.free_spins)} Free Spins!",
                    line2="All line wins are active during bonus rounds.",
                    button=self.start_bonus_btn,
                )
            elif self.state == "BONUS_SUMMARY_MODAL":
                self._draw_modal(
                    surface,
                    title="BONUS COMPLETE!",
                    line1=f"Total Free Spins: {len(self.free_spins)}",
                    line2=f"Total Bonus Won: ${self.free_spin_accumulated_win}",
                    button=self.collect_bonus_btn,
                )

    def _draw_modal(self, surface, title, line1, line2, button):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        modal_rect = pygame.Rect(0, 0, 460, 260)
        modal_rect.center = (WIDTH // 2, HEIGHT // 2)

        pygame.draw.rect(surface, DARK, modal_rect, border_radius=16)
        pygame.draw.rect(surface, GOLD, modal_rect, width=3, border_radius=16)

        t_surf = self.large.render(title, True, WIN_GOLD)
        surface.blit(t_surf, t_surf.get_rect(center=(WIDTH // 2, modal_rect.y + 45)))

        l1_surf = self.med.render(line1, True, WHITE)
        surface.blit(l1_surf, l1_surf.get_rect(center=(WIDTH // 2, modal_rect.y + 105)))

        l2_surf = self.small.render(line2, True, GOLD)
        surface.blit(l2_surf, l2_surf.get_rect(center=(WIDTH // 2, modal_rect.y + 145)))

        button.rect.center = (WIDTH // 2, modal_rect.bottom - 45)
        button.draw(surface)

    def _draw_winning_rows(self, surface):
        for win in self.current_wins:
            row = win.get("row")
            if not isinstance(row, int) or not 0 <= row < GRID_ROWS:
                continue

            y = self.grid_rect.y + row * (CELL_H + CELL_GAP)
            row_rect = pygame.Rect(
                self.grid_rect.x - 3,
                y - 3,
                self.grid_rect.w + 6,
                CELL_H + 6,
            )
            pygame.draw.rect(
                surface,
                WIN_GOLD,
                row_rect,
                width=3,
                border_radius=8,
            )

    def _draw_paytable(self, surface):
        x, y = 24, 205
        heading = self.small.render("ROW PAYS", True, GOLD)
        surface.blit(heading, (x, y))
        y += 30

        for symbol, multiplier in self.machine.PAYTABLE.items():
            label = f"{symbol.replace('_', ' ').title()}: {multiplier}x"
            line = self.tiny.render(label, True, WHITE)
            surface.blit(line, (x, y))
            y += 24

        scatter = self.tiny.render("3 Saloon = 8 free spins", True, WIN_GOLD)
        surface.blit(scatter, (x, y + 4))
        wild = self.tiny.render("Outlaw = Wild", True, WHITE)
        surface.blit(wild, (x, y + 28))

    def _draw_status(self, surface):
        status_y = self.grid_rect.bottom + 32

        if self.state in ("FREE_SPIN", "FREE_SPIN_RESULT") and self.free_spins:
            free_spin = self.free_spins[self.free_spin_index]
            spin_payout = sum(w.get("payout", 0) for w in free_spin.get("wins", []))
            status = (
                f"Free spin {self.free_spin_index + 1}/{len(self.free_spins)}"
                f"  |  Spin Win: ${spin_payout}"
            )
            color = WIN_GOLD
        elif self.result is not None and self.state == "IDLE":
            status = f"Bet: ${self.bet}"
            color = GOLD
        elif self.state in ("SPIN", "BONUS_MODAL"):
            status = f"Bet: ${self.bet}  |  Good luck, partner!"
            color = WHITE
        else:
            status = "Select a bet below"
            color = WHITE

        status_surface = self.small.render(status, True, color)
        surface.blit(
            status_surface,
            status_surface.get_rect(center=(WIDTH // 2, status_y)),
        )

        if self.state == "IDLE" and self.message:
            msg = self.small.render(self.message, True, self.message_color)
            surface.blit(
                msg,
                msg.get_rect(center=(WIDTH // 2, status_y + 28)),
            )

    def _draw_bet_controls(self, surface):
        chips = self.shown_chips
        can_bet = self.state == "IDLE" and chips > 0

        if self.state == "IDLE" and chips < 1:
            prompt_text = "You're out of chips!"
            prompt_color = LIGHT_RED
        elif self.state != "IDLE":
            prompt_text = "Reels spinning..."
            prompt_color = WHITE
        else:
            prompt_text = "Choose your bet"
            prompt_color = WHITE

        prompt = self.small.render(prompt_text, True, prompt_color)
        surface.blit(prompt, prompt.get_rect(center=(WIDTH // 2, 580)))

        for bet, button in self.bet_buttons:
            if can_bet and bet <= chips:
                button.draw(surface)
            else:
                self._draw_disabled(surface, button.rect, f"${bet}")

    def _draw_disabled(self, surface, rect, label):
        pygame.draw.rect(surface, GRAY, rect, border_radius=8)
        pygame.draw.rect(surface, DARK, rect, 2, border_radius=8)
        text = self.small.render(label, True, DARK)
        surface.blit(text, text.get_rect(center=rect.center))