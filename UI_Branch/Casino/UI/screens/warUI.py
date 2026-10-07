import pygame
from .screenUI import Screen
from UI.widgets import Button
from UI.chips import BetPanel
from UI.cards import draw_card
from Classes.player import Player
from Classes.War.war import War

from UI.constants import (
    WIDTH, FELT_GREEN, WHITE, GOLD, LIGHT_RED,
    FONT_NAME, FONT_SIZE_TITLE, FONT_SIZE_LARGE,
    FONT_SIZE_MEDIUM, FONT_SIZE_SMALL,
)


DEAL_MS = 900
REVEAL_MS = 900


class WarScreen(Screen):

    def __init__(self, app, menu):
        super().__init__(app)
        self.menu = menu

        self.title_font = pygame.font.Font(FONT_NAME, FONT_SIZE_TITLE)
        self.large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.med = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.small = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)

        casino_player = Player(
            app.player["username"],
            app.player["chips"],
            app.player["id"]
        )

        self.game = War(casino_player, db=app.db)

        self.panel = BetPanel(balance=app.player["chips"])
        self.menu_button = Button(
            30, 630, 120, 45, "Menu",
            font_size=FONT_SIZE_SMALL
        )
        self.again_button = Button(
            WIDTH // 2 - 180, 600, 170, 50, "Play Again"
        )
        self.result_menu_button = Button(
            WIDTH // 2 + 10, 600, 170, 50, "Menu"
        )
        self.out_menu_button = Button(
            WIDTH // 2 - 85, 600, 170, 50, "Menu"
        )

        self.state = "BET"
        self.state_start = 0
        self.bet = 0
        self.outcome = None
        self.shown_chips = app.player["chips"]

    def _set_state(self, state):
        self.state = state
        self.state_start = pygame.time.get_ticks()

    def _go_to_menu(self):
        self.app.change_screen(self.menu)

    def _deal(self):
        self.bet = self.panel.bet

        # Backend handles the deck, bet, and cards.
        self.game.deal(self.bet)

        self.shown_chips = self.app.player["chips"] - self.bet
        self._set_state("DEAL")

    def handle_event(self, event):
        if self.state == "BET":
            if self.panel.handle_event(event):
                self._deal()

            elif self.menu_button.handle_event(event):
                self._go_to_menu()

        elif self.state == "RESULT":
            if self.app.player["chips"] > 0:
                if self.again_button.handle_event(event):
                    self.panel.reset(self.app.player["chips"])
                    self.shown_chips = self.app.player["chips"]
                    self._set_state("BET")

                elif self.result_menu_button.handle_event(event):
                    self._go_to_menu()

            elif self.out_menu_button.handle_event(event):
                self._go_to_menu()

    def update(self):
        elapsed = pygame.time.get_ticks() - self.state_start

        if self.state == "DEAL" and elapsed >= DEAL_MS:
            self._set_state("REVEAL")

        elif self.state == "REVEAL" and elapsed >= REVEAL_MS:
            self.outcome, _ = self.game.determine_winner()

            self.app.player["chips"] = self.game.player.chips
            self.shown_chips = self.app.player["chips"]

            self._set_state("RESULT")

    def draw(self, surface):
        surface.fill(FELT_GREEN)

        name = self.med.render(
            self.app.player["username"], True, WHITE
        )
        surface.blit(name, (30, 25))

        chips_now = (
            self.panel.remaining
            if self.state == "BET"
            else self.shown_chips
        )

        chips = self.med.render(
            f"Chips: {chips_now}", True, GOLD
        )
        surface.blit(
            chips,
            chips.get_rect(topright=(WIDTH - 30, 25))
        )

        title = self.title_font.render("WAR", True, GOLD)
        surface.blit(
            title,
            title.get_rect(center=(WIDTH // 2, 110))
        )

        rules = self.small.render(
            "Higher card wins and pays 1 to 1. Aces are high. "
            "A tie returns your bet.",
            True,
            WHITE,
        )
        surface.blit(
            rules,
            rules.get_rect(center=(WIDTH // 2, 165))
        )

        if self.state == "BET":
            self.panel.draw(surface)
            self.menu_button.draw(surface)
            return

        you_x = WIDTH // 2 - 140
        dealer_x = WIDTH // 2 + 140
        card_y = 340

        for text, x in (("YOU", you_x), ("DEALER", dealer_x)):
            label = self.med.render(text, True, WHITE)
            surface.blit(
                label,
                label.get_rect(center=(x, 225))
            )

        dealer_up = self.state in ("REVEAL", "RESULT")

        draw_card(
            surface,
            (you_x, card_y),
            self.game.player_card,
            True,
            self.med,
        )

        draw_card(
            surface,
            (dealer_x, card_y),
            self.game.dealer_card,
            dealer_up,
            self.med,
        )

        bet = self.med.render(
            f"Bet: ${self.bet}", True, GOLD
        )
        surface.blit(
            bet,
            bet.get_rect(center=(WIDTH // 2, 465))
        )

        if self.state != "RESULT":
            return

        if self.outcome == "win":
            text, color = f"You win!  +${self.bet}", GOLD
        elif self.outcome == "loss":
            text, color = f"Dealer wins  -${self.bet}", LIGHT_RED
        else:
            text, color = "Tie - your bet is returned", WHITE

        result = self.large.render(text, True, color)
        surface.blit(
            result,
            result.get_rect(center=(WIDTH // 2, 520))
        )

        if self.app.player["chips"] > 0:
            self.again_button.draw(surface)
            self.result_menu_button.draw(surface)
        else:
            out = self.med.render(
                "You're out of chips!", True, LIGHT_RED
            )
            surface.blit(
                out,
                out.get_rect(center=(WIDTH // 2, 565))
            )
            self.out_menu_button.draw(surface)