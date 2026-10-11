"""
 
Slots lobby for the Casino App.
 
    Shown when the player picks "Slots" on the main menu. It has one button per
    slot machine plus a Back button, laid out like the main menu.
 
    The machine buttons use each machine's title, so adding a new machine only
    means adding its class to SLOT_MACHINES.
 
"""
 
import pygame
from UI.widgets import Button
from .screenUI import Screen
from .slotsUI import FruitsUI
from Classes.Slots.fruits import Fruits
from Classes.Slots.wildwest import WildWest
from Classes.Slots.goldrush import GoldRush
from UI.constants import (WIDTH, FELT_GREEN, WHITE, GOLD, FONT_NAME, FONT_SIZE_TITLE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL,)
 
SLOT_MACHINES = [Fruits, WildWest, GoldRush]
 
 
class SlotsMenuScreen(Screen):
    def __init__(self, app, menu):
        super().__init__(app)
        self.menu = menu
 
        self.title_font = pygame.font.Font(FONT_NAME, FONT_SIZE_TITLE)
        self.med        = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.small      = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)
 
        bw, bh, gap = 300, 55, 15
        x = WIDTH // 2 - bw // 2
        y = 200
 
        # Button label -> machine class
        self.machines = {machine.title: machine for machine in SLOT_MACHINES}
 
        self.buttons = []
 
        # Machines: full-width buttons
        for i, machine in enumerate(SLOT_MACHINES):
            self.buttons.append(Button(x, y + i * (bh + gap), bw, bh, machine.title))
 
        # Back to the main menu
        back_y = y + len(SLOT_MACHINES) * (bh + gap) + 10
        self.buttons.append(Button(x, back_y, bw, bh, "Back"))
 
    def handle_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                self.on_click(button.text)
                return
 
    def on_click(self, label):
        """
        Navigate to the chosen machine, or back to the main menu
        """
 
        if label == "Back":
            self.app.change_screen(self.menu)
        elif label in self.machines:
            self.app.change_screen(FruitsUI(self.app, self, self.machines[label]))
 
    def draw(self, surface):
        surface.fill(FELT_GREEN)
        player = self.app.player
 
        # Header: name on the left, chips on the right
        name = self.med.render(player["username"], True, WHITE)
        surface.blit(name, (30, 25))
        chips = self.med.render(f"Chips: {player['chips']}", True, GOLD)
        surface.blit(chips, chips.get_rect(topright=(WIDTH - 30, 25)))
 
        # Title
        title = self.title_font.render("Slots", True, GOLD)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 110)))
 
        # Prompt
        sub = self.small.render("Choose a machine", True, WHITE)
        surface.blit(sub, sub.get_rect(center=(WIDTH // 2, 165)))
 
        # Render buttons to screen
        for button in self.buttons:
            button.draw(surface)