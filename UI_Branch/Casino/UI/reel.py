
import pygame


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

        self.strip = [self._random_symbol()]
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

    def start(self, final_symbols, duration_ms, now):
        """Animate toward the supplied final symbol or symbols."""

        if not isinstance(final_symbols, (list, tuple)):
            final_symbols = [final_symbols]

        current_index = min(
            int(round(self.position)),
            len(self.strip) - 1,
        )
        current_symbol = self.strip[current_index]

        extra_symbols = max(0, self.rows - 1)

        self.strip = (
            [current_symbol]
            + [self._random_symbol() for _ in range(extra_symbols)]
            + list(final_symbols)
        )

        self.target_position = float(self.rows)
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

        pygame.draw.rect(
            surface,
            self.reel_bg,
            self.rect,
            border_radius=self.border_radius,
        )

        old_clip = surface.get_clip()
        surface.set_clip(self.rect)

        first_index = max(0, int(self.position) - 1)
        last_index = min(
            len(self.strip) - 1,
            int(self.position) + self.rows,
        )

        for index in range(first_index, last_index + 1):
            y = self.rect.centery + (
                self.position - index
            ) * self.pitch

            cell = pygame.Rect(
                self.rect.x,
                0,
                self.rect.w,
                self.cell_height,
            )
            cell.centery = int(y)

            if (
                cell.bottom < self.rect.top
                or cell.top > self.rect.bottom
            ):
                continue

            pygame.draw.rect(
                surface,
                self.reel_bg,
                cell,
                border_radius=self.border_radius,
            )

            draw_symbol(surface, self.strip[index], cell)

            pygame.draw.rect(
                surface,
                self.cell_border,
                cell,
                1,
                border_radius=self.border_radius,
            )

        surface.set_clip(old_clip)

        pygame.draw.rect(
            surface,
            self.cell_border,
            self.rect,
            3,
            border_radius=self.border_radius,
        )
