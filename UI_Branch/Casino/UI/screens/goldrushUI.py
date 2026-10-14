"""
Gold Rush slot-machine screen for the Casino App.

Features a 4x3 grid with row-based pays and a pick-a-mine-cart bonus round
revealing pre-determined backend multipliers over a 3x2 cart grid.
"""

import math
import random
import pygame
from .screenUI import Screen
from UI.widgets import Button
from Classes.player import Player
from Classes.Slots.goldrush import GoldRush
from UI.slots_helper import Reel, draw_slot_panel, draw_paytable_panel
from UI.symbols import draw_symbol, draw_mine_cart, get_font
from UI.constants import (
    WIDTH,
    HEIGHT,
    FELT_GREEN,
    DARK_GREEN,
    WHITE,
    GOLD,
    LIGHT_RED,
    GRAY,
    FONT_SIZE_TITLE,
    FONT_SIZE_LARGE,
    FONT_SIZE_MEDIUM,
    FONT_SIZE_SMALL,
    BETS,
    DARK,
    REEL_BG,
    CELL_BORDER,
)

WIN_GOLD = (255, 210, 70)
MUTED_PRIZE = (170, 175, 185)

CELL_W = 118
CELL_H = 75
CELL_GAP = 0
COL_GAP = 10
GRID_ROWS = 4
GRID_COLS = 3

FADE_SPEED = 14  # Alpha increment/decrement per frame


class GoldRushUI(Screen):
    """Four-row, three-column Gold Rush slot screen with pick-a-cart bonus."""

    def __init__(self, app, menu, machine=GoldRush):
        super().__init__(app)
        self.menu = menu
        self.machine = machine

        self.title_font = get_font(FONT_SIZE_TITLE, True)
        self.large = get_font(FONT_SIZE_LARGE, True)
        self.med = get_font(FONT_SIZE_MEDIUM)
        self.small = get_font(FONT_SIZE_SMALL)
        self.tiny = get_font(16)

        casino_player = Player(app.player["username"], app.player["chips"], app.player["id"])
        self.game = machine(casino_player, db=app.db)
        self.rng = random.Random()

        grid_w = GRID_COLS * CELL_W + (GRID_COLS - 1) * COL_GAP
        grid_h = GRID_ROWS * CELL_H + (GRID_ROWS - 1) * CELL_GAP
        grid_x = (WIDTH - grid_w) // 2
        grid_y = 158

        self.grid_rect = pygame.Rect(grid_x, grid_y, grid_w, grid_h)
        self.overlay_rect = self.grid_rect.inflate(16, 16)

        self.columns = [
            Reel(
                rect=pygame.Rect(grid_x + col * (CELL_W + COL_GAP), grid_y, CELL_W, grid_h),
                rng=self.rng,
                machine=self.game,
                rows=GRID_ROWS,
                cell_height=CELL_H,
                cell_gap=CELL_GAP,
                reel_bg=REEL_BG,
                cell_border=CELL_BORDER,
                border_radius=6,
            )
            for col in range(GRID_COLS)
        ]

        self.menu_button = Button(30, 630, 120, 45, "Menu", font_size=FONT_SIZE_SMALL)

        btn_w, btn_h, btn_gap = 90, 45, 10
        buttons_width = len(BETS) * btn_w + (len(BETS) - 1) * btn_gap
        buttons_x = (WIDTH - buttons_width) // 2
        self.bet_buttons = [
            (
                bet,
                Button(
                    buttons_x + i * (btn_w + btn_gap),
                    626,
                    btn_w,
                    btn_h,
                    f"${bet}",
                    font_size=FONT_SIZE_SMALL,
                ),
            )
            for i, bet in enumerate(BETS)
        ]

        self.start_bonus_btn = Button(WIDTH // 2 - 85, 410, 170, 50, "Enter Mine", font_size=24)

        # 6 cart bounding rects in a 3 rows x 2 cols layout over overlay_rect
        self.cart_rects = self._generate_cart_rects()

        # States: IDLE, SPIN, BONUS_MODAL, FADE_IN, BONUS_PICK, BONUS_REVEAL, FADE_OUT
        self.state = "IDLE"
        self.bet = 0
        self.last_win = 0
        self.result = None
        self.current_grid = None
        self.current_wins = []
        self.bonus_feature = None
        self.shown_chips = app.player["chips"]
        self.message = "Choose a bet to spin"
        self.message_color = WHITE

        # Bonus screen internals
        self.fade_alpha = 0
        self.picked_cart_idx = None
        self.cart_values = {}
        self.bonus_stage = 0  # 0: waiting for pick, 1: picked, 2: others revealed
        self.reveal_timer = 0
        self.bonus_win_amount = 0
        self.bonus_modal_delay_until = 0

    def _generate_cart_rects(self):
        """Build 6 rects formatted in 3 rows and 2 columns inside the reel overlay."""
        rects = []
        rows, cols = 3, 2
        cw, ch = 150, 85
        pad_x = (self.overlay_rect.w - cols * cw) // (cols + 1)
        pad_y = (self.overlay_rect.h - 55 - rows * ch) // (rows + 1)
        top_offset = self.overlay_rect.y + 45

        for r in range(rows):
            for c in range(cols):
                rx = self.overlay_rect.x + pad_x + c * (cw + pad_x)
                ry = top_offset + pad_y + r * (ch + pad_y)
                rects.append(pygame.Rect(rx, ry, cw, ch))
        return rects

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
                extra_spins=12 + col * 4,
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
        self.last_win = 0
        self.shown_chips = chips_before - bet
        features = self.result.get("features", {}) or {}
        self.bonus_feature = features.get("bonus")
        self.message = "Spinning..."
        self.message_color = WHITE

        now = pygame.time.get_ticks()
        self._start_grid_animation(self.result["grid"], now)
        self.state = "SPIN"

    def handle_event(self, event):
        if self.state == "BONUS_MODAL":
            if self.start_bonus_btn.handle_event(event):
                self.state = "FADE_IN"
            return

        if self.state == "BONUS_PICK" and self.bonus_stage == 0:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_pos = event.pos
                for idx, r in enumerate(self.cart_rects):
                    if r.collidepoint(mouse_pos):
                        self._handle_cart_pick(idx)
                        break
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

        if self.state == "SPIN" and not any(reel.spinning for reel in self.columns):
            self._finish_grid_animation()

        elif self.state == "FADE_IN":
            self.fade_alpha = min(255, self.fade_alpha + FADE_SPEED)
            if self.fade_alpha >= 255:
                self._setup_bonus_game()
                self.state = "BONUS_PICK"

        elif self.state == "BONUS_REVEAL":
            if self.bonus_stage == 1 and now >= self.reveal_timer:
                # Stage 2: Reveal the remaining unpicked carts
                self._reveal_remaining_carts()
                self.bonus_stage = 2
                self.reveal_timer = now + 1600
            elif self.bonus_stage == 2 and now >= self.reveal_timer:
                self.state = "FADE_OUT"

        elif self.state == "FADE_OUT":
            self.fade_alpha = max(0, self.fade_alpha - FADE_SPEED)
            if self.fade_alpha <= 0:
                self._finish_round()

    def _finish_grid_animation(self):
        self.current_wins = self.result.get("wins", []) or []
        main_payout = sum(
            w.get("payout", w.get("multiplier", 0) * self.bet)
            for w in self.current_wins
        )
        self.shown_chips += main_payout
        self.last_win += main_payout

        if self.bonus_feature:
            self.state = "BONUS_MODAL"
            self.bonus_modal_delay_until = pygame.time.get_ticks() + 1800
        else:
            self._finish_round()

    def _setup_bonus_game(self):
        self.picked_cart_idx = None
        self.cart_values = {}
        self.bonus_stage = 0
        self.bonus_win_amount = 0

    def _handle_cart_pick(self, idx):
        self.picked_cart_idx = idx
        prize_mult = self.bonus_feature["prize"]
        self.cart_values[idx] = prize_mult
        self.bonus_win_amount = prize_mult * self.bet
        self.shown_chips += self.bonus_win_amount
        self.last_win += self.bonus_win_amount

        self.bonus_stage = 1
        self.reveal_timer = pygame.time.get_ticks() + 750
        self.state = "BONUS_REVEAL"

    def _reveal_remaining_carts(self):
        others = list(self.bonus_feature["others"])
        for i in range(len(self.cart_rects)):
            if i != self.picked_cart_idx:
                self.cart_values[i] = others.pop() if others else 0

    def _finish_round(self):
        self.state = "IDLE"
        self.fade_alpha = 0
        self.bonus_feature = None
        self.shown_chips = self.app.player["chips"]
        self.current_wins = self.result.get("wins", []) or []

    def draw(self, surface):
        surface.fill(FELT_GREEN)

        name = self.med.render(self.app.player["username"], True, WHITE)
        surface.blit(name, (30, 24))

        chips = self.med.render(f"Chips: {self.shown_chips}", True, GOLD)
        surface.blit(chips, chips.get_rect(topright=(WIDTH - 30, 24)))

        title = self.title_font.render("GOLD RUSH", True, GOLD)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 85)))

        subtitle_text = "Match symbols across 4 rows. 3+ Mine Carts unlock the Cart Bonus!"
        subtitle = self.tiny.render(subtitle_text, True, WHITE)
        surface.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 125)))

        self._draw_paytable(surface)

        # Base reel frame and reels
        pygame.draw.rect(surface, DARK_GREEN, self.overlay_rect, border_radius=14)
        for reel in self.columns:
            reel.draw(surface, draw_symbol)

        if self.state == "IDLE" and self.current_grid is not None:
            self._draw_winning_rows(surface)

        if self.bonus_feature and self.state == "BONUS_MODAL":
            self._draw_cart_highlights(surface)

        pygame.draw.rect(surface, GRAY, self.overlay_rect, 2, border_radius=14)

        # Bottom panel and bet controls
        draw_slot_panel(surface, WIDTH // 2, self.grid_rect.bottom + 12, self.shown_chips, self.bet, self.last_win)
        self._draw_status(surface)
        self._draw_bet_controls(surface)

        if self.state == "IDLE":
            self.menu_button.draw(surface)

        # Bonus overlay rendering
        if self.state in ("FADE_IN", "BONUS_PICK", "BONUS_REVEAL", "FADE_OUT"):
            self._draw_bonus_layer(surface)

        if self.state == "BONUS_MODAL":
            self._draw_modal(
                surface,
                title="GOLD RUSH BONUS!",
                line1="3+ Mine Carts Discovered!",
                line2="Pick a cart to strike gold!",
                button=self.start_bonus_btn,
            )

    def _draw_bonus_layer(self, surface):
        """Render the mine cart pick panel smoothly masked over the reels."""
        sub = pygame.Surface((self.overlay_rect.w, self.overlay_rect.h), pygame.SRCALPHA)
        sub.fill((20, 20, 22, self.fade_alpha))

        # Panel header
        if self.fade_alpha > 120:
            hdr_text = "PICK A MINE CART" if self.bonus_stage == 0 else "BONUS WIN!"
            hdr_font = get_font(20, True)
            hdr_surf = hdr_font.render(hdr_text, True, WIN_GOLD)
            sub.blit(hdr_surf, hdr_surf.get_rect(center=(self.overlay_rect.w // 2, 24)))

        mouse_pos = pygame.mouse.get_pos()
        for idx, rect in enumerate(self.cart_rects):
            local_rect = rect.move(-self.overlay_rect.x, -self.overlay_rect.y)
            is_hovered = (
                self.state == "BONUS_PICK"
                and self.bonus_stage == 0
                and rect.collidepoint(mouse_pos)
            )

            # Cart slot background
            bg_col = (45, 45, 52) if is_hovered else (30, 30, 35)
            pygame.draw.rect(sub, bg_col, local_rect, border_radius=10)

            # Highlight border
            if is_hovered:
                pygame.draw.rect(sub, WIN_GOLD, local_rect, 2, border_radius=10)
            elif idx == self.picked_cart_idx:
                pygame.draw.rect(sub, GOLD, local_rect, 3, border_radius=10)
            else:
                pygame.draw.rect(sub, (60, 60, 65), local_rect, 1, border_radius=10)

            # Draw the cart
            draw_mine_cart(sub, local_rect, gold=(idx in self.cart_values))

            # Reveal multipliers
            if idx in self.cart_values:
                val = self.cart_values[idx]
                is_player_pick = idx == self.picked_cart_idx
                txt_color = WIN_GOLD if is_player_pick else MUTED_PRIZE
                label = f"{val}x" if not is_player_pick else f"+${val * self.bet}"
                val_surf = get_font(18, True).render(label, True, txt_color)
                sub.blit(val_surf, val_surf.get_rect(center=(local_rect.centerx, local_rect.bottom - 16)))

        surface.blit(sub, self.overlay_rect)
        pygame.draw.rect(surface, GOLD, self.overlay_rect, 3, border_radius=14)

    def _draw_cart_highlights(self, surface):
        """Pulsing gold outline around landing Mine Carts on the grid."""
        if not self.current_grid:
            return
        now = pygame.time.get_ticks()
        pulse = 2 + int(abs(math.sin(now * 0.008)) * 2)

        for r_idx, row in enumerate(self.current_grid):
            for c_idx, symbol in enumerate(row):
                if symbol == self.machine.BONUS:
                    x = self.grid_rect.x + c_idx * (CELL_W + COL_GAP)
                    y = self.grid_rect.y + r_idx * (CELL_H + CELL_GAP)
                    cell = pygame.Rect(x, y, CELL_W, CELL_H)
                    pygame.draw.rect(surface, WIN_GOLD, cell.inflate(6, 6), pulse, border_radius=6)

    def _draw_winning_rows(self, surface):
        for win in self.current_wins:
            row = win.get("row")
            if not isinstance(row, int) or not 0 <= row < GRID_ROWS:
                continue

            y = self.grid_rect.y + row * (CELL_H + CELL_GAP)
            row_rect = pygame.Rect(self.grid_rect.x - 3, y - 3, self.grid_rect.w + 6, CELL_H + 6)
            pygame.draw.rect(surface, WIN_GOLD, row_rect, width=3, border_radius=8)

    def _draw_paytable(self, surface):
        lines = [
            f"3x {symbol.title()}  {mult}:1"
            for symbol, mult in self.machine.PAYTABLE.items()
        ]
        lines.append("3 Carts = Mine Bonus")

        draw_paytable_panel(
            surface,
            rect=(18, 175, 235, 260),
            title="ROW PAYS",
            lines=lines,
            text_color=WHITE,
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

    def _draw_status(self, surface):
        status_y = self.grid_rect.bottom + 72
        if self.state in ("BONUS_PICK", "BONUS_REVEAL"):
            status = "Select a cart to find hidden treasure!" if self.bonus_stage == 0 else f"Won +${self.bonus_win_amount}!"
            status_surf = self.small.render(status, True, WIN_GOLD)
            surface.blit(status_surf, status_surf.get_rect(center=(WIDTH // 2, status_y)))

    def _draw_bet_controls(self, surface):
        chips = self.shown_chips
        can_bet = self.state == "IDLE" and chips > 0

        prompt_y = 600
        if self.state == "IDLE":
            if chips < 1:
                prompt_text = "You're out of chips!"
                prompt_color = LIGHT_RED
            else:
                prompt_text = "Choose your bet"
                prompt_color = WHITE
        elif self.state in ("SPIN", "BONUS_MODAL"):
            prompt_text = "Digging for gold..."
            prompt_color = WHITE
        else:
            prompt_text = ""
            prompt_color = WHITE

        if prompt_text:
            prompt = self.small.render(prompt_text, True, prompt_color)
            surface.blit(prompt, prompt.get_rect(center=(WIDTH // 2, prompt_y)))

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