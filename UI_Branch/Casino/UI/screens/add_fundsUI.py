
import pygame
from .screenUI import Screen
from UI.widgets import Button
from Classes.player import Player
 
from UI.constants import (
    WIDTH, FELT_GREEN, WHITE, GOLD,
    FONT_NAME, FONT_SIZE_TITLE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL,)
 
 
AMOUNTS = [50, 100, 500, 1000]
 
 
class AddFundsScreen(Screen):
    def __init__(self, app, menu):
        super().__init__(app)
        self.menu = menu
 
        self.title_font = pygame.font.Font(FONT_NAME, FONT_SIZE_TITLE)
        self.med = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.small = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)
 
        # The rules for adding funds live in the Player class
        self.player = Player(
            app.player["username"], app.player["chips"], app.player["id"])
 
        bw, bh, gap = 300, 55, 15
        x = WIDTH // 2 - bw // 2
        y = 200
 
        self.amount_buttons = []
        for i, amount in enumerate(AMOUNTS):
            self.amount_buttons.append(
                (amount, Button(x, y + i * (bh + gap), bw, bh, f"+ ${amount:,}")))
 
        self.back_button = Button(x, y + len(AMOUNTS) * (bh + gap), bw, bh, "Back")
 
        self.message = ""
 
    def handle_event(self, event):
        for amount, button in self.amount_buttons:
            if button.handle_event(event):
                self._add(amount)
                return
 
        if self.back_button.handle_event(event):
            self.app.change_screen(self.menu)
 
    def _add(self, amount):
        self.player.add_funds(amount)
 
        # Save the new balance and keep the menu header in sync
        self.app.db.save_chips(self.player.id, self.player.chips)
        self.app.player["chips"] = self.player.chips
 
        self.message = f"Added ${amount:,} in chips!"
 
    def draw(self, surface):
        surface.fill(FELT_GREEN)
 
        # Header: name on the left, chips on the right
        name = self.med.render(self.app.player["username"], True, WHITE)
        surface.blit(name, (30, 25))
        chips = self.med.render(f"Chips: {self.app.player['chips']}", True, GOLD)
        surface.blit(chips, chips.get_rect(topright=(WIDTH - 30, 25)))
 
        # Title
        title = self.title_font.render("Add Funds", True, GOLD)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 110)))
 
        sub = self.small.render("Choose an amount to add to your chips", True, WHITE)
        surface.blit(sub, sub.get_rect(center=(WIDTH // 2, 165)))
 
        for _amount, button in self.amount_buttons:
            button.draw(surface)
        self.back_button.draw(surface)
 
        if self.message:
            msg = self.med.render(self.message, True, GOLD)
            surface.blit(msg, msg.get_rect(center=(WIDTH // 2, 640)))