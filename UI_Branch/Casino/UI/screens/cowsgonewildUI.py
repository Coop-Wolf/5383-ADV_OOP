"""
Cows Gone Wild slot-machine screen for the Casino App.

Features:
    - 4x3 Base Game with 3 horizontal paylines.
    - Golden Jugs trigger the Barnyard Respin bonus.
    - Bonus expands vertically upward from 4x3 to 4x4, then to 4x5.
    - Fixed bottom anchor so the grid grows upward without covering the bottom panel.
    - True staggered reel animations during bonus respins with column-by-column stops.
    - Traveling laser bolt, elastic scale bounce, and floating multiplier tags for Boss Cow boosts.
"""

import math
import random
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
        self.bonus_cols = BASE_COLS
        self.bonus_rows = BASE_ROWS
        self.respins_left = 3
        self.locked_jugs = {}        # (r, c) -> multiplier
        self.unlocked_symbols = {}   # (r, c) -> symbol
        self.pending_new_jugs = {}   # (r, c) -> multiplier waiting for reel stop
        self.respin_delay_until = 0
        self.bonus_total_payout = 0

        # Dedicated animated reels for bonus respins
        self.bonus_reels = []
        self._rebuild_bonus_reels(self.bonus_rows)

        # Boss Cow Beam & Visual Pop Engine
        self.beam_anim_active = False
        self.boss_pos = None
        self.boss_mult = 1
        self.beam_targets = []
        self.current_target_idx = 0
        self.target_phase = "IDLE"   # "TRAVEL", "POP", "PAUSE"
        self.target_timer = 0
        self.target_start_time = 0
        self.target_travel_duration = 140
        self.target_pop_duration = 320
        self.popping_jugs = {}       # (r, c) -> {start_time, duration, mult_text}

    def _go_to_menu(self):
        self.app.change_screen(self.menu)

    def _grid_column(self, grid, col, rows=BASE_ROWS):
        return [grid[row][col] for row in range(rows)]

    def _rebuild_bonus_reels(self, total_rows):
        """Creates staggered animated reels matching the dynamic bonus grid height."""
        start_y = self._get_bonus_grid_y(total_rows)
        grid_h = total_rows * CELL_H
        self.bonus_reels = [
            Reel(
                rect=pygame.Rect(self.grid_x + c * (CELL_W + COL_GAP), start_y, CELL_W, grid_h),
                rng=self.rng,
                machine=self.game,
                rows=total_rows,
                cell_height=CELL_H,
                cell_gap=0,
                reel_bg=REEL_BG,
                cell_border=CELL_BORDER,
                border_radius=6,
            )
            for c in range(BASE_COLS)
        ]

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

        if self.state == "SPIN":
            for reel in self.columns:
                reel.update(now)
            if not any(reel.spinning for reel in self.columns):
                self._finish_grid_animation()

        elif self.state == "BONUS_PENDING" and now >= self.bonus_modal_delay_until:
            self.state = "BONUS_MODAL"

        elif self.state == "BONUS_ACTIVE":
            for reel in self.bonus_reels:
                reel.update(now)
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
        self.bonus_cols = BASE_COLS
        self.bonus_rows = BASE_ROWS
        self.respins_left = 3
        self.boss_pos = None
        self.boss_mult = 1
        self.beam_anim_active = False
        self.popping_jugs.clear()

        # Seed initial locked jugs directly from triggering event without wiping the board
        if self.bonus_events and self.bonus_events[0].get("type") == "INIT_BONUS":
            init_evt = self.bonus_events[0]
            self.event_idx = 1
            raw_jugs = init_evt.get("locked_jugs", {})
            self.locked_jugs = {tuple(map(int, k.split(","))): v for k, v in raw_jugs.items()}
            self.respins_left = init_evt.get("respins_left", 3)
            self.bonus_rows = init_evt.get("rows", 3)

        self._rebuild_bonus_reels(self.bonus_rows)
        self.respin_delay_until = pygame.time.get_ticks() + 800

    def _update_bonus_engine(self, now):
        # 1. Boss Cow Sequential Traveling Laser Engine
        if self.beam_anim_active:
            if self.current_target_idx >= len(self.beam_targets):
                self.beam_anim_active = False
                self.respin_delay_until = now + 900
                return

            target = self.beam_targets[self.current_target_idx]
            pos = tuple(target["pos"])

            if self.target_phase == "TRAVEL":
                if now - self.target_start_time >= self.target_travel_duration:
                    # Laser struck target: upgrade multiplier value & initiate pop
                    self.locked_jugs[pos] = target["new_val"]
                    self.popping_jugs[pos] = {
                        "start_time": now,
                        "duration": self.target_pop_duration,
                        "mult_text": f"x{self.boss_mult}",
                    }
                    self.target_phase = "POP"
                    self.target_timer = now + self.target_pop_duration

            elif self.target_phase == "POP":
                if now >= self.target_timer:
                    # Brief breath before next bolt
                    self.target_phase = "PAUSE"
                    self.target_timer = now + 120

            elif self.target_phase == "PAUSE":
                if now >= self.target_timer:
                    self.current_target_idx += 1
                    if self.current_target_idx < len(self.beam_targets):
                        self.target_phase = "TRAVEL"
                        self.target_start_time = now
                    else:
                        self.beam_anim_active = False
                        self.respin_delay_until = now + 850
            return

        # 2. Wait for staggered reels to finish spinning before locking new symbols
        if any(reel.spinning for reel in self.bonus_reels):
            return

        if self.pending_new_jugs:
            for pos, val in self.pending_new_jugs.items():
                self.locked_jugs[pos] = val
                self.unlocked_symbols.pop(pos, None)
            self.pending_new_jugs.clear()

        if now < self.respin_delay_until:
            return

        if self.event_idx >= len(self.bonus_events):
            return

        evt = self.bonus_events[self.event_idx]
        self.event_idx += 1
        evt_type = evt.get("type")

        if evt_type == "RESPIN_RESULT":
            self.respins_left = evt.get("respins_left", 3)
            raw_syms = evt.get("unlocked_symbols", {})
            self.unlocked_symbols = {tuple(map(int, k.split(","))): s for k, s in raw_syms.items()}

            self.pending_new_jugs = {
                tuple(item["pos"]): item["val"] for item in evt.get("new_jugs", [])
            }

            boss_p = evt.get("boss_pos")
            self.boss_pos = tuple(boss_p) if boss_p else None
            self.boss_mult = evt.get("boss_mult", 1)

            # Build virtual column strips for staggered respin animation
            for c in range(self.bonus_cols):
                col_symbols = []
                for r in range(self.bonus_rows):
                    pos = (r, c)
                    if pos in self.locked_jugs:
                        col_symbols.append(self.machine.BONUS)
                    elif pos in self.pending_new_jugs:
                        col_symbols.append(self.machine.BONUS)
                    elif self.boss_pos == pos:
                        col_symbols.append("boss_cow")
                    else:
                        col_symbols.append(self.unlocked_symbols.get(pos, "milk_carton"))

                self.bonus_reels[c].start(
                    col_symbols,
                    duration_ms=850 + c * 280,
                    now=now,
                    extra_spins=8 + c * 3,
                )

        elif evt_type == "BOSS_COW_STRIKE":
            self.beam_anim_active = True
            self.boss_pos = tuple(evt.get("boss_pos"))
            self.boss_mult = evt.get("multiplier", 2)
            self.beam_targets = evt.get("targets", [])
            self.current_target_idx = 0
            self.target_phase = "TRAVEL"
            self.target_start_time = now

        elif evt_type == "EXPAND_GRID":
            self.bonus_rows = evt.get("rows", self.bonus_rows + 1)
            self.respins_left = evt.get("respins_left", 3)
            self._rebuild_bonus_reels(self.bonus_rows)
            self.respin_delay_until = now + 1200

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
        self.popping_jugs.clear()
        self.boss_pos = None

    def _get_bonus_grid_y(self, total_rows):
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

        subtitle_text = f"Match symbols across rows. {self.machine.JUGS_NEEDED}+ Golden Jugs triggers the Barnyard Respin!"
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
                line1=f"{self.machine.JUGS_NEEDED}+ Golden Jugs Discovered!",
                line2="Collect jugs to expand up to 4x5!",
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

        pygame.draw.rect(surface, DARK_GREEN, outer_bounds, border_radius=14)

        # Header info
        info_font = get_font(20, True)
        respin_txt = f"RESPINS REMAINING: {self.respins_left}"
        info_surf = info_font.render(respin_txt, True, WIN_GOLD)
        surface.blit(info_surf, info_surf.get_rect(center=(WIDTH // 2, grid_y - 18)))

        # Draw staggered animated reels
        for reel in self.bonus_reels:
            reel.draw(surface, draw_symbol)

        # Overlay static elements (Locked Jugs, Boss Cow, Multiplier Pops)
        for c in range(self.bonus_cols):
            for r in range(total_rows):
                pos = (r, c)
                rect = self._get_cell_rect(r, c, total_rows)

                # Draw stationary locked jug
                if pos in self.locked_jugs:
                    mult = self.locked_jugs[pos]
                    
                    # Elastic scale pop calculation
                    pop_data = self.popping_jugs.get(pos)
                    scale = 0.35
                    if pop_data:
                        progress = min(1.0, (now - pop_data["start_time"]) / pop_data["duration"])
                        scale = 0.35 * (1.0 + 0.25 * math.sin(progress * math.pi))
                        if progress >= 1.0:
                            self.popping_jugs.pop(pos, None)

                    pygame.draw.rect(surface, REEL_BG, rect)
                    draw_golden_jug(surface, rect, multiplier=mult, scale=scale)
                    pygame.draw.rect(surface, CELL_BORDER, rect, 1)

                    # Floating multiplier indicator
                    if pop_data:
                        progress = min(1.0, (now - pop_data["start_time"]) / pop_data["duration"])
                        float_y = rect.top - int(progress * 18)
                        tag_font = get_font(18, True)
                        tag_surf = tag_font.render(pop_data["mult_text"], True, CYAN_LASER)
                        tag_rect = tag_surf.get_rect(center=(rect.centerx, float_y))
                        surface.blit(tag_surf, tag_rect)

                # Draw Boss Cow with its multiplier badge
                elif self.boss_pos == pos and not self.bonus_reels[c].spinning:
                    pygame.draw.rect(surface, REEL_BG, rect)
                    draw_symbol(surface, "boss_cow", rect)
                    badge_font = get_font(14, True)
                    b_surf = badge_font.render(f"{self.boss_mult}x", True, GOLD)
                    b_rect = b_surf.get_rect(center=(rect.right - 18, rect.bottom - 12))
                    pygame.draw.rect(surface, DARK, b_rect.inflate(6, 4), border_radius=4)
                    pygame.draw.rect(surface, GOLD, b_rect.inflate(6, 4), 1, border_radius=4)
                    surface.blit(b_surf, b_rect)
                    pygame.draw.rect(surface, CELL_BORDER, rect, 1)

        # Draw outer casing border
        pygame.draw.rect(surface, GRAY, outer_bounds, 2, border_radius=14)

        # Traveling Laser Bolt Animation
        if self.beam_anim_active and self.boss_pos and self.target_phase == "TRAVEL":
            if self.current_target_idx < len(self.beam_targets):
                target_pos = tuple(self.beam_targets[self.current_target_idx]["pos"])
                start_p = self._get_cell_rect(self.boss_pos[0], self.boss_pos[1], total_rows).center
                end_p = self._get_cell_rect(target_pos[0], target_pos[1], total_rows).center

                t = min(1.0, (now - self.target_start_time) / self.target_travel_duration)
                eased_t = 1 - (1 - t) ** 2

                cur_x = start_p[0] + (end_p[0] - start_p[0]) * eased_t
                cur_y = start_p[1] + (end_p[1] - start_p[1]) * eased_t

                # Glowing layered neon laser
                pygame.draw.line(surface, (10, 150, 240), start_p, (cur_x, cur_y), 8)
                pygame.draw.line(surface, CYAN_LASER, start_p, (cur_x, cur_y), 4)
                pygame.draw.line(surface, WHITE, start_p, (cur_x, cur_y), 2)
                pygame.draw.circle(surface, WHITE, (int(cur_x), int(cur_y)), 4)

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
        lines.append(f"{self.machine.JUGS_NEEDED}+ Jugs = Respins")

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