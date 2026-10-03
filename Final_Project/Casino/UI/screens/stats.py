import pygame
from UI.constants import (
    WIDTH, FELT_GREEN, DARK_GREEN, WHITE, GOLD, LIGHT_RED, LIGHT_GRAY,
    FONT_NAME, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL,
)
from UI.widgets import Button
from Final_Project.Casino.UI.screens.screen import Screen

GAME_LABELS = {"VideoPoker": "Video Poker", "Blackjack": "Blackjack", "War": "War"}

HEADERS = ["Game", "Rounds", "Wins", "Losses", "Win Rate", "Biggest Win", "Net Profit"]
# x position for each column (Game is left-aligned, the rest are centered)
COLUMN_X = [65, 330, 420, 510, 620, 745, 865]


class StatsScreen(Screen):
    def __init__(self, app, previous):
        super().__init__(app)
        self.previous = previous
        self.title_font = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.header_font = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)
        self.row_font = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.back = Button(WIDTH // 2 - 100, 520, 200, 50, "Back")

        # Read fresh stats each time the screen opens
        stats = app.db.get_stats(app.player["id"])
        self.rows = [self.make_row(GAME_LABELS[g], s) for g, s in stats.items()]
        self.total_row = self.make_row("Total", self.combine(stats.values()))

    @staticmethod
    def combine(stat_list):
        stat_list = list(stat_list)
        return {
            "rounds_played": sum(s["rounds_played"] for s in stat_list),
            "wins": sum(s["wins"] for s in stat_list),
            "losses": sum(s["losses"] for s in stat_list),
            "biggest_win": max(s["biggest_win"] for s in stat_list),
            "net_profit": sum(s["net_profit"] for s in stat_list),
        }

    @staticmethod
    def make_row(label, s):
        """Returns a list of (text, color) cells, one per column."""
        rounds = s["rounds_played"]
        win_rate = f"{s['wins'] / rounds:.0%}" if rounds else "-"

        net = s["net_profit"]
        if net > 0:
            net_cell = (f"+{net}", GOLD)
        elif net < 0:
            net_cell = (str(net), LIGHT_RED)
        else:
            net_cell = ("0", WHITE)

        return [
            (label, WHITE),
            (str(rounds), WHITE),
            (str(s["wins"]), WHITE),
            (str(s["losses"]), WHITE),
            (win_rate, WHITE),
            (str(s["biggest_win"]), WHITE),
            net_cell,
        ]

    def handle_event(self, event):
        if self.back.handle_event(event):
            self.app.change_screen(self.previous)

    def draw_row(self, surface, y, cells, font):
        for i, (text, color) in enumerate(cells):
            img = font.render(text, True, color)
            if i == 0:
                surface.blit(img, img.get_rect(midleft=(COLUMN_X[0], y)))
            else:
                surface.blit(img, img.get_rect(center=(COLUMN_X[i], y)))

    def draw(self, surface):
        surface.fill(FELT_GREEN)

        title = self.title_font.render(f"{self.app.player['username']}'s Stats", True, GOLD)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 80)))

        # Table panel
        panel = pygame.Rect(40, 130, WIDTH - 80, 360)
        pygame.draw.rect(surface, DARK_GREEN, panel, border_radius=10)
        pygame.draw.rect(surface, WHITE, panel, width=2, border_radius=10)

        # Header row
        header_cells = [(h, LIGHT_GRAY) for h in HEADERS]
        self.draw_row(surface, 170, header_cells, self.header_font)
        pygame.draw.line(surface, LIGHT_GRAY, (60, 195), (WIDTH - 60, 195), 1)

        # Game rows
        y = 235
        for cells in self.rows:
            self.draw_row(surface, y, cells, self.row_font)
            y += 65

        # Totals row
        pygame.draw.line(surface, LIGHT_GRAY, (60, 420), (WIDTH - 60, 420), 1)
        self.draw_row(surface, 455, self.total_row, self.row_font)

        self.back.draw(surface)