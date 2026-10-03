import pygame
from UI.constants import (
    WIDTH, FELT_GREEN, GOLD, WHITE,
    FONT_NAME, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM,
)
from UI.widgets import Button
from UI.screens.screen import Screen


class PlaceholderScreen(Screen):
    """Temporary stand-in for screens we haven't built yet."""

    def __init__(self, app, title, previous):
        super().__init__(app)
        self.title = title
        self.previous = previous  # the screen to return to
        self.big = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.med = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.back = Button(WIDTH // 2 - 100, 400, 200, 50, "Back")

    def handle_event(self, event):
        if self.back.handle_event(event):
            self.app.change_screen(self.previous)

    def draw(self, surface):
        surface.fill(FELT_GREEN)
        title = self.big.render(self.title, True, GOLD)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 250)))
        note = self.med.render("Coming soon", True, WHITE)
        surface.blit(note, note.get_rect(center=(WIDTH // 2, 320)))
        self.back.draw(surface)