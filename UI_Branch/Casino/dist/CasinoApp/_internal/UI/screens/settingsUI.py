import pygame
from UI.widgets import Button
from .screenUI import Screen
from .statsUI import StatsScreen
from .add_fundsUI import AddFundsScreen
from UI.constants import WIDTH, FELT_GREEN, WHITE, GOLD, FONT_NAME, FONT_SIZE_TITLE, FONT_SIZE_MEDIUM


class SettingsScreen(Screen):
    def __init__(self, app, menu_screen):
        super().__init__(app)
        self.menu_screen = menu_screen

        self.title_font = pygame.font.Font(FONT_NAME, FONT_SIZE_TITLE)
        self.med        = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)

        bw, bh, gap = 300, 55, 15
        x = WIDTH // 2 - bw // 2
        y = 220

        self.buttons = []
        options = ["Add Funds", "Stats", "Logout", "Back"]

        for i, label in enumerate(options):
            top = y + i * (bh + gap) + (15 if label == "Back" else 0)
            self.buttons.append(Button(x, top, bw, bh, label))

    def handle_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                self.on_click(button.text)

    def on_click(self, label):
        if label == "Add Funds":
            self.app.change_screen(AddFundsScreen(self.app, self))
        elif label == "Stats":
            self.app.change_screen(StatsScreen(self.app, self))
        elif label == "Logout":
            from .loginUI import LoginScreen
            self.app.disconnect_chat()
            self.app.player = None
            self.app.change_screen(LoginScreen(self.app))
        elif label == "Back":
            self.app.change_screen(self.menu_screen)

    def draw(self, surface):
        surface.fill(FELT_GREEN)
        player = self.app.player

        # Header: name on the left, chips on the right
        name = self.med.render(player["username"], True, WHITE)
        surface.blit(name, (30, 25))
        chips = self.med.render(f"Chips: {player['chips']}", True, GOLD)
        surface.blit(chips, chips.get_rect(topright=(WIDTH - 30, 25)))

        # Title
        title = self.title_font.render("Settings", True, GOLD)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 120)))

        for button in self.buttons:
            button.draw(surface)