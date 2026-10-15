"""
Cows Gone Wild slot-machine screen for the Casino App.

Features:
    - 4x3 Base Game with 3 horizontal paylines.
    - 4+ Golden Jugs triggers the Barnyard Respin bonus.
    - Bonus expands vertically upward to 4x4, then 4x5 upon collecting +4 jugs.
    - Fixed bottom anchor so the grid grows upward without covering the bottom panel.
    - Dynamic spinning animation on unlocked cells during bonus respins.
    - Sequential column-major laser beam animation when the Boss Cow lands.
"""

import math
import random
from functools import lru_cache
import pygame

from .screenUI import Screen
from UI.widgets import Button
from Classes.player import Player
from Classes.Slots.cowsgonewild import CowsGoneWild
from UI.slots_helper import Reel, draw_slot_panel, draw_paytable_panel
from UI.symbols import draw_symbol, draw_golden_jug, get_font
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
CYAN_LASER = (50, 240, 255)

CELL_W = 104
CELL_H = 72
COL_GAP = 8

BASE_ROWS = 3
BASE_COLS = 4

# Bottom baseline for reel area (anchor so grid expands strictly UPWARD)
GRID_BOTTOM_ANCHOR = 500


class CowsGoneWildUI(Screen):
    """4x3 base game expanding vertically upward to 4x5 in the Barnyard Respins bonus."""

    def __init__(self, app, menu, machine=CowsGoneWild):
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

        # Geometry anchors
        self.base_w = BASE_COLS * CELL_W + (BASE_COLS - 1) * COL_GAP
        self.grid_x = (WIDTH - self.base_w) // 2
        self.base_grid_h = BASE_ROWS * CELL_H
        self.base_grid_y = GRID_BOTTOM_ANCHOR - self.base_grid_h

        self.grid_rect = pygame.Rect(self.grid_x, self.base_grid_y, self.base_w, self.base_grid_h)

        # 4 Base Reels
        self.columns = [
            Reel(
                rect=pygame.Rect(self.grid_x + c * (CELL_W + COL_GAP), self.base_grid_y, CELL_W, self.base_grid_h),
                rng=self.rng,
                machine=self.game,
                rows=BASE_ROWS,
                cell_height=CELL_H,
                cell_gap=0,
                reel_bg=REEL_BG,
                cell_border=CELL_BORDER,
                border_radius=6,
            )
            for c in range(BASE_COLS)
        ]

        # Buttons
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

        self.start_bonus_btn = Button(WIDTH // 2 - 95, 410, 190, 50, "Enter Barnyard", font_size=22)
        self.collect_bonus_btn = Button(WIDTH // 2 - 90, 410, 180, 50, "Collect Win", font_size=24)

        # State Machine
        self.state = "IDLE"
        self.bet = 0
        self.last_win = 0
        self.result = None
        self.current_grid = None
        self.current_wins = []
        self.shown_chips = app.player["chips"]
        self.message = "Choose a bet to spin"
        self.message_color = WHITE
        self.bonus_modal_delay_until = 0

        # Respin Engine State
        self.bonus_events = []
        self.event_idx = 0
        self.bonus_cols = 4
        self.bonus_rows = 4
        self.respins_left = 3
        self.locked_jugs = {}        # (row, col) -> multiplier
        self.unlocked_symbols = {}   # (row, col) -> final settled symbol name
        self.flashing_cells = {}     # (row, col) -> expiration_ms
        self.pending_new_jugs = []
        self.respin_delay_until = 0
        self.bonus_total_payout = 0

        # Respin active spinning animation
        self.respin_spinning = False
        self.respin_spin_until = 0

        # Boss Cow Beam Animation Sub-Engine
        self.beam_anim_active = False
        self.boss_pos = None
        self.boss_multiplier = 1
        self.beam_targets = []
        self.current_target_idx = 0
        self.beam_timer = 0

    def _go_to_menu(self):
        self.app.change_screen(self.menu)

    def _grid_column(self, grid, col):
        return [grid[row][col] for row in range(BASE_ROWS)]

    def _start_grid_animation(self, grid, now, duration_base=1050):
        self.current_grid = grid
        self.current_wins = []
        for col, reel in enumerate(self.columns):
            reel.start(
                self._grid_column(grid, col),
                duration_ms=duration_base + col * 320,
                now=now,
                extra_spins=10 + col * 4,
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
        self.message = "Spinning..."
        self.message_color = WHITE

        now = pygame.time.get_ticks()
        self._start_grid_animation(self.result["grid"], now)
        self.state = "SPIN"

    def handle_event(self, event):
        if self.state == "BONUS_MODAL":
            if self.start_bonus_btn.handle_event(event):
                self._enter_bonus_mode()
            return

        if self.state == "BONUS_SUMMARY":
            if self.collect_bonus_btn.handle_event(event):
                self._finish_round()
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

        elif self.state == "BONUS_PENDING" and now >= self.bonus_modal_delay_until:
            self.state = "BONUS_MODAL"

        elif self.state == "BONUS_ACTIVE":
            self._update_bonus_engine(now)

    def _finish_grid_animation(self):
        self.current_wins = self.result.get("wins", []) or []
        main_payout = sum(
            w.get("payout", w.get("multiplier", 0) * self.bet)
            for w in self.current_wins
        )
        self.shown_chips += main_payout
        self.last_win += main_payout

        features = self.result.get("features", {}) or {}
        respins_data = features.get("respins")

        if respins_data:
            self.bonus_events = respins_data.get("events", [])
            self.state = "BONUS_PENDING"
            self.bonus_modal_delay_until = pygame.time.get_ticks() + 1400
        else:
            self._finish_round()

    def _enter_bonus_mode(self):
        self.state = "BONUS_ACTIVE"
        self.event_idx = 0
        self.bonus_cols = 4
        self.bonus_rows = 4
        self.respins_left = 3
        self.locked_jugs.clear()
        self.pending_new_jugs.clear()
        self.unlocked_symbols.clear()
        self.flashing_cells.clear()
        self.beam_anim_active = False
        self.respin_spinning = False
        self.respin_delay_until = pygame.time.get_ticks() + 600

    def _update_bonus_engine(self, now):
        # 1. Sequential Boss Cow target beam lock
        if self.beam_anim_active:
            if now >= self.beam_timer:
                if self.current_target_idx < len(self.beam_targets):
                    target = self.beam_targets[self.current_target_idx]
                    pos = tuple(target["pos"])
                    new_val = target["new_val"]

                    self.locked_jugs[pos] = new_val
                    self.flashing_cells[pos] = now + 650
                    self.current_target_idx += 1
                    self.beam_timer = now + 900
                else:
                    self.beam_anim_active = False
                    self.boss_pos = None
                    self.respin_delay_until = now + 950
            return

        # 2. Respin spinning animation timing
        if self.respin_spinning:
            if now >= self.respin_spin_until:
                self.respin_spinning = False
                
                # Lock and reveal newly landed jugs NOW that the reels have settled
                for item in self.pending_new_jugs:
                    pos = tuple(item["pos"])
                    self.locked_jugs[pos] = item["val"]
                    self.flashing_cells[pos] = now + 600
                    self.unlocked_symbols.pop(pos, None)
                self.pending_new_jugs.clear()
            return

        if now < self.respin_delay_until:
            return

        if self.event_idx >= len(self.bonus_events):
            return

        evt = self.bonus_events[self.event_idx]
        self.event_idx += 1
        evt_type = evt.get("type")

        if evt_type == "INIT_BONUS":
            self.bonus_cols = evt.get("cols", 4)
            self.bonus_rows = evt.get("rows", 4)
            self.respins_left = evt.get("respins_left", 3)
            raw_jugs = evt.get("locked_jugs", {})
            for key, val in raw_jugs.items():
                r, c = map(int, key.split(","))
                self.locked_jugs[(r, c)] = val
            self.respin_delay_until = now + 1000

        elif evt_type == "NEW_JUGS_LOCKED":
            self.respins_left = evt.get("respins_left", 3)
            raw_syms = evt.get("unlocked_symbols", {})
            for key, sym in raw_syms.items():
                r, c = map(int, key.split(","))
                self.unlocked_symbols[(r, c)] = sym

            for item in evt.get("new_jugs", []):
                pos = tuple(item["pos"])
                self.locked_jugs[pos] = item["val"]
                self.flashing_cells[pos] = now + 600
                self.unlocked_symbols.pop(pos, None)

            # Stage the new jugs — DO NOT put them in locked_jugs yet
            self.pending_new_jugs = evt.get("new_jugs", [])

            # Trigger a short spin roll before settling
            self.respin_spinning = True
            self.respin_spin_until = now + 1200
            self.respin_delay_until = now + 2400

        elif evt_type == "BOSS_COW_STRIKE":
            self.beam_anim_active = True
            self.boss_pos = tuple(evt.get("boss_pos"))
            self.boss_multiplier = evt.get("multiplier", 2)
            self.beam_targets = evt.get("targets", [])
            self.current_target_idx = 0
            self.beam_timer = now + 750

        elif evt_type == "EXPAND_GRID":
            self.bonus_rows = evt.get("rows", 5)
            self.respins_left = evt.get("respins_left", 3)
            self.respin_delay_until = now + 1300

        elif evt_type == "BLANK_RESPIN":
            self.respins_left = evt.get("respins_left", 0)
            raw_syms = evt.get("unlocked_symbols", {})
            for key, sym in raw_syms.items():
                r, c = map(int, key.split(","))
                self.unlocked_symbols[(r, c)] = sym

            self.respin_spinning = True
            self.respin_spin_until = now + 600
            self.respin_delay_until = now + 950

        elif evt_type == "BONUS_COMPLETE":
            total_mult = evt.get("total_multiplier", 0)
            self.bonus_total_payout = total_mult * self.bet
            self.shown_chips += self.bonus_total_payout
            self.last_win += self.bonus_total_payout
            self.state = "BONUS_SUMMARY"

    def _finish_round(self):
        self.state = "IDLE"
        self.shown_chips = self.app.player["chips"]
        self.locked_jugs.clear()
        self.pending_new_jugs.clear()
        self.unlocked_symbols.clear()
        self.flashing_cells.clear()

    def _get_bonus_grid_y(self, total_rows):
        """Top-left Y coordinate anchored so bottom never moves."""
        return GRID_BOTTOM_ANCHOR - (total_rows * CELL_H)

    def _get_cell_rect(self, r, c, total_rows):
        start_y = self._get_bonus_grid_y(total_rows)
        rx = self.grid_x + c * (CELL_W + COL_GAP)
        ry = start_y + r * CELL_H
        return pygame.Rect(rx, ry, CELL_W, CELL_H)

    def draw(self, surface):
        surface.fill(FELT_GREEN)

        name = self.med.render(self.app.player["username"], True, WHITE)
        surface.blit(name, (30, 24))

        chips = self.med.render(f"Chips: {self.shown_chips}", True, GOLD)
        surface.blit(chips, chips.get_rect(topright=(WIDTH - 30, 24)))

        title = self.title_font.render("COWS GONE WILD", True, GOLD)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 45)))

        subtitle_text = "Match symbols across rows. 4+ Golden Jugs triggers the Barnyard Respin!"
        subtitle = self.tiny.render(subtitle_text, True, WHITE)
        surface.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 75)))

        self._draw_paytable(surface)

        if self.state == "BONUS_ACTIVE":
            self._draw_bonus_board(surface)
        else:
            self._draw_base_board(surface)

        draw_slot_panel(surface, WIDTH // 2, GRID_BOTTOM_ANCHOR + 12, self.shown_chips, self.bet, self.last_win)
        self._draw_status(surface)
        self._draw_bet_controls(surface)

        if self.state == "IDLE":
            self.menu_button.draw(surface)

        if self.state == "BONUS_MODAL":
            self._draw_modal(
                surface,
                title="BARNYARD RESPIN!",
                line1="4+ Golden Jugs Discovered!",
                line2="Reels expand to 4x4 with 3 Respins!",
                button=self.start_bonus_btn,
            )
        elif self.state == "BONUS_SUMMARY":
            self._draw_modal(
                surface,
                title="BONUS COMPLETE!",
                line1=f"Total Locked Jugs: {len(self.locked_jugs)}",
                line2=f"Total Bonus Won: ${self.bonus_total_payout}",
                button=self.collect_bonus_btn,
            )

    def _draw_base_board(self, surface):
        outer = self.grid_rect.inflate(16, 16)
        pygame.draw.rect(surface, DARK_GREEN, outer, border_radius=14)
        for reel in self.columns:
            reel.draw(surface, draw_symbol)

        if self.state == "IDLE" and self.current_grid is not None:
            self._draw_winning_rows(surface)

        if self.state in ("BONUS_PENDING", "BONUS_MODAL"):
            self._draw_initial_jug_highlights(surface)

        pygame.draw.rect(surface, GRAY, outer, 2, border_radius=14)

    def _draw_bonus_board(self, surface):
            now = pygame.time.get_ticks()
            total_rows = self.bonus_rows
            grid_y = self._get_bonus_grid_y(total_rows)
            total_h = total_rows * CELL_H
            outer_bounds = pygame.Rect(self.grid_x, grid_y, self.base_w, total_h).inflate(16, 16)

            # 1. Matching outer frame (DARK_GREEN and GRAY border like base game)
            pygame.draw.rect(surface, DARK_GREEN, outer_bounds, border_radius=14)

            # Header: Respins left
            info_font = get_font(20, True)
            respin_txt = f"RESPINS REMAINING: {self.respins_left}"
            info_surf = info_font.render(respin_txt, True, WIN_GOLD)
            surface.blit(info_surf, info_surf.get_rect(center=(WIDTH // 2, grid_y - 18)))

            # 2. Draw each column with REEL_BG and CELL_BORDER
            for c in range(self.bonus_cols):
                col_x = self.grid_x + c * (CELL_W + COL_GAP)
                col_rect = pygame.Rect(col_x, grid_y, CELL_W, total_h)

                # Reel column background
                pygame.draw.rect(surface, REEL_BG, col_rect, border_radius=6)

                for r in range(total_rows):
                    rect = pygame.Rect(col_x, grid_y + r * CELL_H, CELL_W, CELL_H)
                    pos = (r, c)

                    if pos in self.locked_jugs:
                        # Locked Jug cell: crisp and stationary
                        mult = self.locked_jugs[pos]
                        draw_golden_jug(surface, rect, multiplier=mult)

                        if pos in self.flashing_cells and now < self.flashing_cells[pos]:
                            flash_s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                            flash_s.fill((255, 255, 255, 140))
                            surface.blit(flash_s, rect.topleft)
                        pygame.draw.rect(surface, GOLD, rect, 2)

                    elif self.boss_pos == pos:
                        # Boss cow cell
                        draw_symbol(surface, "boss_cow", rect)
                        pygame.draw.rect(surface, CYAN_LASER, rect, 3)

                    else:
                        # Unlocked cell
                        old_clip = surface.get_clip()
                        surface.set_clip(rect)

                        if self.respin_spinning:
                            # Smooth continuous vertical scroll
                            scroll_speed = 0.55  # pixels per millisecond
                            scroll_offset = int((now * scroll_speed + (c * 37)) % CELL_H)

                            symbols_list = self.game.NON_BONUS_SYMBOLS
                            sym1_idx = (r + now // 180 + c * 2) % len(symbols_list)
                            sym2_idx = (sym1_idx + 1) % len(symbols_list)

                            # Draw current and incoming rolling symbols
                            r1 = rect.move(0, scroll_offset)
                            r2 = rect.move(0, scroll_offset - CELL_H)
                            draw_symbol(surface, symbols_list[sym1_idx], r1)
                            draw_symbol(surface, symbols_list[sym2_idx], r2)
                        elif pos in self.unlocked_symbols:
                            draw_symbol(surface, self.unlocked_symbols[pos], rect)

                        surface.set_clip(old_clip)

                    # Shared horizontal divider line between stacked cells
                    if r < total_rows - 1:
                        pygame.draw.line(surface, CELL_BORDER, (rect.left, rect.bottom), (rect.right, rect.bottom), 1)

                # Outer border per column
                pygame.draw.rect(surface, CELL_BORDER, col_rect, 3, border_radius=6)

            # Outer casing border matching base game
            pygame.draw.rect(surface, GRAY, outer_bounds, 2, border_radius=14)

            # 3. Boss Cow Laser Beam
            if self.beam_anim_active and self.boss_pos and self.current_target_idx < len(self.beam_targets):
                target_pos = tuple(self.beam_targets[self.current_target_idx]["pos"])
                start_rect = self._get_cell_rect(self.boss_pos[0], self.boss_pos[1], total_rows)
                end_rect = self._get_cell_rect(target_pos[0], target_pos[1], total_rows)

                p1 = start_rect.center
                p2 = end_rect.center

                pygame.draw.line(surface, (30, 180, 255), p1, p2, 6)
                pygame.draw.line(surface, (255, 255, 255), p1, p2, 2)
                pygame.draw.circle(surface, (255, 255, 255), p2, 9)
                pygame.draw.circle(surface, CYAN_LASER, p2, 14, 2)
                
    def _draw_initial_jug_highlights(self, surface):
        if not self.current_grid:
            return
        now = pygame.time.get_ticks()
        pulse = 2 + int(abs(math.sin(now * 0.008)) * 2)

        for r_idx, row in enumerate(self.current_grid):
            for c_idx, symbol in enumerate(row):
                if symbol == self.machine.BONUS:
                    x = self.grid_x + c_idx * (CELL_W + COL_GAP)
                    y = self.base_grid_y + r_idx * CELL_H
                    cell = pygame.Rect(x, y, CELL_W, CELL_H)
                    pygame.draw.rect(surface, WIN_GOLD, cell.inflate(6, 6), pulse, border_radius=6)

    def _draw_winning_rows(self, surface):
        for win in self.current_wins:
            row = win.get("row")
            if not isinstance(row, int) or not 0 <= row < BASE_ROWS:
                continue
            y = self.base_grid_y + row * CELL_H
            row_rect = pygame.Rect(self.grid_rect.x - 3, y - 3, self.grid_rect.w + 6, CELL_H + 6)
            pygame.draw.rect(surface, WIN_GOLD, row_rect, width=3, border_radius=8)

    def _draw_paytable(self, surface):
        lines = [
            f"4x {symbol.title()}  {mult}:1"
            for symbol, mult in self.machine.PAYTABLE.items()
        ]
        lines.append("4 Jugs = Respins")

        draw_paytable_panel(
            surface,
            rect=(18, 175, 235, 255),
            title="ROW PAYS",
            lines=lines,
            text_color=WHITE,
        )

    def _draw_modal(self, surface, title, line1, line2, button):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        modal_rect = pygame.Rect(0, 0, 480, 260)
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
        status_y = GRID_BOTTOM_ANCHOR + 72
        if self.state == "BONUS_ACTIVE":
            status = f"Locked Jugs: {len(self.locked_jugs)} / {self.bonus_cols * self.bonus_rows}"
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
        elif self.state in ("SPIN", "BONUS_PENDING", "BONUS_MODAL"):
            prompt_text = "Milking the reels..."
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