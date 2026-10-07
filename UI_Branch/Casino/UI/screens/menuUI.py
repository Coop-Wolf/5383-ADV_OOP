
import pygame
from UI.widgets import Button
from .screenUI import Screen
from .placeholderUI import PlaceholderScreen
from .statsUI import StatsScreen
from .warUI import WarScreen
from .blackjackUI import BlackjackScreen
from .add_fundsUI import AddFundsScreen
 
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
 
        self.buttons = []
 
        # Games: full-width buttons
        for i, label in enumerate(["Video Poker", "Blackjack", "War"]):
            self.buttons.append(Button(x, y + i * (bh + gap), bw, bh, label))
 
        # Everything else: two per row
        half_w = (bw - 10) // 2
        row_y = y + 3 * (bh + gap) + 10
        rows = [("Stats", "Add Funds"), ("Logout", "Quit")]
 
        for r, (left, right) in enumerate(rows):
            top = row_y + r * (bh + gap)
            self.buttons.append(Button(x, top, half_w, bh, left))
            self.buttons.append(Button(x + half_w + 10, top, half_w, bh, right))
 
    def handle_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                self.on_click(button.text)
 
    def on_click(self, label):
        """
        Navigate to appropriate screen
        """
 
        if label == "Logout":
            from .loginUI import LoginScreen
            self.app.player = None
            self.app.change_screen(LoginScreen(self.app))
        elif label == "Quit":
            # App.run() sees QUIT, closes the database, and shuts pygame down
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif label == "Stats":
            self.app.change_screen(StatsScreen(self.app, self))
        elif label == "Add Funds":
            self.app.change_screen(AddFundsScreen(self.app, self))
        elif label == "War":
            self.app.change_screen(WarScreen(self.app, self))
        elif label == "Blackjack":
            self.app.change_screen(BlackjackScreen(self.app, self))
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
 
