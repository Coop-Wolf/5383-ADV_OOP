import pygame
from UI.constants import (
    WHITE, BLACK, GOLD, GRAY, LIGHT_GRAY, DARK_GREEN,
    FONT_NAME, FONT_SIZE_MEDIUM,)


class Button:
    def __init__(self, x, y, width, height, text, font_size=FONT_SIZE_MEDIUM):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(FONT_NAME, font_size)

    def handle_event(self, event):
        """Returns True if the button was clicked."""
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(self, surface):
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        color = GOLD if hovered else DARK_GREEN
        text_color = BLACK if hovered else WHITE

        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, width=2, border_radius=8)

        label = self.font.render(self.text, True, text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))


class TextBox:
    def __init__(self, x, y, width, height, max_length=10, font_size=FONT_SIZE_MEDIUM):
        self.rect = pygame.Rect(x, y, width, height)
        self.max_length = max_length
        self.font = pygame.font.Font(FONT_NAME, font_size)
        self.text = ""
        self.active = True  # starts focused so the player can type right away

    def handle_event(self, event):
        """Returns True if Enter was pressed while active."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isprintable() and event.unicode:
                if len(self.text) < self.max_length:
                    self.text += event.unicode
        return False

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=6)
        border = GOLD if self.active else GRAY
        pygame.draw.rect(surface, border, self.rect, width=3, border_radius=6)

        display = self.text
        # blinking cursor (visible for half of every second)
        if self.active and (pygame.time.get_ticks() // 500) % 2 == 0:
            display += "|"

        label = self.font.render(display, True, BLACK)
        surface.blit(label, (self.rect.x + 10, self.rect.centery - label.get_height() // 2))

    def clear(self):
        self.text = ""