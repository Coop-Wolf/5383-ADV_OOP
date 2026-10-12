
import pygame
from .constants import (GOLD, WHITE, FONT_NAME)


class Reel:
    """Reusable animated reel for slot machines."""

    def __init__(
        self,
        rect,
        rng,
        machine,
        rows=1,
        cell_height=120,
        cell_gap=0,
        reel_bg=(25, 25, 25),
        cell_border=(80, 80, 80),
        border_radius=10,
    ):
        self.rect = pygame.Rect(rect)
        self.rng = rng
        self.machine = machine
        self.rows = rows
        self.cell_height = cell_height
        self.cell_gap = cell_gap
        self.reel_bg = reel_bg
        self.cell_border = cell_border
        self.border_radius = border_radius

        # Populate initial strip with enough symbols to fill all visible rows
        self.strip = [self._random_symbol() for _ in range(self.rows)]
        self.position = 0.0
        self.target_position = 0.0
        self.start_ms = 0
        self.duration_ms = 1000
        self.spinning = False

    @property
    def pitch(self):
        return self.cell_height + self.cell_gap

    def _random_symbol(self):
        names = list(self.machine.SYMBOLS.keys())
        weights = list(self.machine.SYMBOLS.values())

        return self.rng.choices(names, weights=weights, k=1)[0]

    def start(self, final_symbols, duration_ms, now, extra_spins=16):
            """Animate toward the supplied final symbol or symbols."""
            if not isinstance(final_symbols, (list, tuple)):
                final_symbols = [final_symbols]

            current_index = min(int(round(self.position)), len(self.strip) - 1)
            current_symbol = self.strip[current_index]

            spin_padding = [self._random_symbol() for _ in range(extra_spins)]
            self.strip = [current_symbol] + spin_padding + list(final_symbols)

            # The final symbols begin right after current_symbol + spin_padding
            self.target_position = float(1 + len(spin_padding))
            self.position = 0.0
            self.start_ms = now
            self.duration_ms = max(1, duration_ms)
            self.spinning = True

    def update(self, now):
        if not self.spinning:
            return

        progress = min(
            (now - self.start_ms) / self.duration_ms,
            1.0,
        )
        eased = 1 - (1 - progress) ** 3

        self.position = self.target_position * eased

        if progress >= 1.0:
            self.position = self.target_position
            self.spinning = False

    def draw(self, surface, draw_symbol):
            """Draw symbols using the project's shared draw_symbol function."""
            pygame.draw.rect(surface, self.reel_bg, self.rect, border_radius=self.border_radius)

            old_clip = surface.get_clip()
            surface.set_clip(self.rect)

            first_index = max(0, int(self.position) - 1)
            last_index = min(len(self.strip) - 1, int(self.position) + self.rows + 1)

            # Only single-row reels get rounded cells; multi-row columns stay square to avoid seams
            cell_radius = self.border_radius if self.rows == 1 else 0

            for index in range(first_index, last_index + 1):
                if self.rows == 1:
                    # Single-row machines center the single active cell in the reel rect
                    y = self.rect.centery + (index - self.position) * self.pitch
                    cell = pygame.Rect(self.rect.x, 0, self.rect.w, self.cell_height)
                    cell.centery = int(y)
                else:
                    # Multi-row grids flow top-to-bottom starting at self.rect.y
                    y = self.rect.y + (index - self.position) * self.pitch
                    cell = pygame.Rect(self.rect.x, int(y), self.rect.w, self.cell_height)

                if cell.bottom < self.rect.top or cell.top > self.rect.bottom:
                    continue

                pygame.draw.rect(surface, self.reel_bg, cell, border_radius=cell_radius)
                draw_symbol(surface, self.strip[index], cell)
                pygame.draw.rect(surface, self.cell_border, cell, 1, border_radius=cell_radius)

            surface.set_clip(old_clip)
            pygame.draw.rect(surface, self.cell_border, self.rect, 3, border_radius=self.border_radius)



def draw_slot_panel(surface, center_x, top_y, chips, bet, win, width=480, height=52):
    panel_rect = pygame.Rect(0, 0, width, height)
    panel_rect.centerx = center_x
    panel_rect.top = top_y

    pygame.draw.rect(surface, (15, 15, 15), panel_rect, border_radius=8)
    pygame.draw.rect(surface, (80, 80, 80), panel_rect, 2, border_radius=8)

    col_w = width // 3
    labels = [("CREDIT", f"${chips}"), ("BET", f"${bet}"), ("WIN", f"${max(0, win)}")]

    font_label = pygame.font.Font(FONT_NAME, 14)
    font_val = pygame.font.Font(FONT_NAME, 20)

    for i, (title, val) in enumerate(labels):
        cell_x = panel_rect.x + i * col_w
        cx = cell_x + col_w // 2

        t_surf = font_label.render(title, True, (160, 160, 160))
        surface.blit(t_surf, t_surf.get_rect(center=(cx, panel_rect.y + 16)))

        v_surf = font_val.render(val, True, WHITE)
        surface.blit(v_surf, v_surf.get_rect(center=(cx, panel_rect.y + 36)))

        if i < 2:
            div_x = cell_x + col_w
            pygame.draw.line(surface, (50, 50, 50), (div_x, panel_rect.y + 8), (div_x, panel_rect.bottom - 8), 1)