import pygame
from UI.widgets import Button
from Final_Project.Casino.UI.screens.screen import Screen
from UI.screens.placeholder import PlaceholderScreen
from UI.screens.stats import StatsScreen

from UI.constants import (WIDTH, FELT_GREEN, WHITE, GOLD,
    FONT_NAME, FONT_SIZE_TITLE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL,)


class MenuScreen(Screen):
    def __init__(self, app, is_new=False):
        super().__init__(app)
        self.is_new = is_new
        self.title_font = pygame.font.Font(FONT_NAME, FONT_SIZE_TITLE)
        self.med = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.small = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)

        bw, bh, gap = 300, 55, 15
        x = WIDTH // 2 - bw // 2
        y = 200

        labels = ["Video Poker", "Blackjack", "War", "Stats", "Logout"]
        self.buttons = []
        
        for i, label in enumerate(labels):
            self.buttons.append(Button(x, y + i * (bh + gap), bw, bh, label))

    def handle_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                self.on_click(button.text)

    def on_click(self, label):
        """
        Navigate to appropriate screen
        """
        
        if label == "Logout":
            from UI.screens.login import LoginScreen
            self.app.player = None
            self.app.change_screen(LoginScreen(self.app))
        elif label == "Stats":
            self.app.change_screen(StatsScreen(self.app, self))
        else:
            self.app.change_screen(PlaceholderScreen(self.app, label, self))

    def draw(self, surface):
        surface.fill(FELT_GREEN)
        player = self.app.player

        # Header: name on the left, chips on the right
        name = self.med.render(player["username"], True, WHITE)
        surface.blit(name, (30, 25))
        chips = self.med.render(f"Chips: {player['chips']}", True, GOLD)
        surface.blit(chips, chips.get_rect(topright=(WIDTH - 30, 25)))

        # Title
        title = self.title_font.render("Coop's Casino", True, GOLD)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 110)))

        # Player Welcome
        greeting = "Welcome!" if self.is_new else "Welcome back!"
        sub = self.small.render(greeting, True, WHITE)
        surface.blit(sub, sub.get_rect(center=(WIDTH // 2, 165)))

        # Render buttons to screen
        for button in self.buttons:
            button.draw(surface)