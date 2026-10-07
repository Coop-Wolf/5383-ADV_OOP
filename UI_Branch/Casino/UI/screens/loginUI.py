from Classes.util import Util

import pygame
from UI.constants import (
    WIDTH, FELT_GREEN, WHITE, GOLD, RED, TITLE,
    FONT_NAME, FONT_SIZE_TITLE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL,
)
from UI.widgets import Button, TextBox
from .screenUI import Screen
from .menuUI import MenuScreen



class LoginScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.title_font = pygame.font.Font(FONT_NAME, FONT_SIZE_TITLE)
        self.label_font = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.error_font = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)

        self.box = TextBox(WIDTH // 2 - 150, 300, 300, 50, max_length=10)
        self.button = Button(WIDTH // 2 - 100, 380, 200, 50, "Play")
        self.error = ""

    def handle_event(self, event):
        submitted = self.box.handle_event(event)
        if self.button.handle_event(event):
            submitted = True
        if submitted:
            self.try_login()

    def try_login(self):
        username, error = Util.validate_username(self.box.text)
        if error:
            self.error = error
            return

        player, is_new = self.app.db.get_or_create_player(username)
        self.app.player = player
        self.app.change_screen(MenuScreen(self.app, is_new))

    def draw(self, surface):
        surface.fill(FELT_GREEN)

        title = self.title_font.render(TITLE, True, GOLD)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 170)))

        prompt = self.label_font.render("Enter your username", True, WHITE)
        surface.blit(prompt, prompt.get_rect(center=(WIDTH // 2, 265)))

        self.box.draw(surface)
        self.button.draw(surface)

        if self.error:
            msg = self.error_font.render(self.error, True, RED)
            surface.blit(msg, msg.get_rect(center=(WIDTH // 2, 460)))