import pygame
from .screenUI import Screen
from UI.widgets import Button
from UI.chips import BetPanel
from UI.cards import draw_card
from Classes.deck import Deck

from UI.constants import (
    WIDTH, FELT_GREEN, WHITE, GOLD, LIGHT_RED,
    FONT_NAME, FONT_SIZE_TITLE, FONT_SIZE_LARGE,
    FONT_SIZE_MEDIUM, FONT_SIZE_SMALL,
)


DEAL_MS = 900       # player card shown, dealer card face down
REVEAL_MS = 900     # both cards shown before the result appears


class WarScreen(Screen):
    """
    States:
        BET     - player places a bet with chips
        DEAL    - player card face up, dealer card face down
        REVEAL  - both cards face up
        RESULT  - outcome shown, Play Again / Menu
    """

    def __init__(self, app, menu):
        super().__init__(app)
        self.menu = menu

        self.title_font = pygame.font.Font(FONT_NAME, FONT_SIZE_TITLE)
        self.large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.med = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.small = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)

        self.panel = BetPanel(balance=app.player["chips"])

        self.menu_button = Button(
            30, 630, 120, 45, "Menu", font_size=FONT_SIZE_SMALL
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
        self.player_card = None
        self.dealer_card = None
        self.bet = 0
        self.outcome = None
        self.shown_chips = app.player["chips"]

    # State helpers
    def _set_state(self, state):
        self.state = state
        self.state_start = pygame.time.get_ticks()

    def _go_to_menu(self):
        self.app.change_screen(self.menu)

    def _deal(self):
        """Draw the cards, settle the round in the database, then start the animation."""

        chips_before = self.app.player["chips"]
        self.bet = self.panel.bet

        deck = Deck()
        self.player_card = deck.deal_card()
        self.dealer_card = deck.deal_card()

        player_value = self.player_card.get_poker_value()
        dealer_value = self.dealer_card.get_poker_value()

        if player_value > dealer_value:
            self.outcome, net_change = "win", self.bet
        elif player_value < dealer_value:
            self.outcome, net_change = "loss", -self.bet
        else:
            self.outcome, net_change = "push", 0

        # Save the result immediately so the round is recorded even if
        # the game closes before the result screen appears.
        new_balance = self.app.db.record_result(
            self.app.player["id"], "War", self.outcome, net_change
        )
        self.app.player["chips"] = new_balance

        # Show the balance after the bet until the result is revealed.
        self.shown_chips = chips_before - self.bet
        self._set_state("DEAL")

    # Screen interface
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
            self.shown_chips = self.app.player["chips"]
            self._set_state("RESULT")

    def draw(self, surface):
        surface.fill(FELT_GREEN)

        # Header: name on the left, chips on the right.
        name = self.med.render(self.app.player["username"], True, WHITE)
        surface.blit(name, (30, 25))

        chips_now = (
            self.panel.remaining
            if self.state == "BET"
            else self.shown_chips
        )
        chips = self.med.render(f"Chips: {chips_now}", True, GOLD)
        surface.blit(chips, chips.get_rect(topright=(WIDTH - 30, 25)))

        # Title and rules.
        title = self.title_font.render("WAR", True, GOLD)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 110)))

        rules = self.small.render(
            "Higher card wins and pays 1 to 1. Aces are high. A tie returns your bet.",
            True,
            WHITE,
        )
        surface.blit(rules, rules.get_rect(center=(WIDTH // 2, 165)))

        if self.state == "BET":
            self.panel.draw(surface)
            self.menu_button.draw(surface)
            return

        # Cards.
        you_x = WIDTH // 2 - 140
        dealer_x = WIDTH // 2 + 140
        card_y = 340

        for text, x in (("YOU", you_x), ("DEALER", dealer_x)):
            label = self.med.render(text, True, WHITE)
            surface.blit(label, label.get_rect(center=(x, 225)))

        dealer_up = self.state in ("REVEAL", "RESULT")

        draw_card(
            surface,
            (you_x, card_y),
            self.player_card,
            True,
            self.med,
        )
        draw_card(
            surface,
            (dealer_x, card_y),
            self.dealer_card,
            dealer_up,
            self.med,
        )

        bet = self.med.render(f"Bet: ${self.bet}", True, GOLD)
        surface.blit(bet, bet.get_rect(center=(WIDTH // 2, 465)))

        if self.state != "RESULT":
            return

        # Result.
        if self.outcome == "win":
            text, color = f"You win!  +${self.bet}", GOLD
        elif self.outcome == "loss":
            text, color = f"Dealer wins  -${self.bet}", LIGHT_RED
        else:
            text, color = "Tie - your bet is returned", WHITE

        result = self.large.render(text, True, color)
        surface.blit(result, result.get_rect(center=(WIDTH // 2, 520)))

        if self.app.player["chips"] > 0:
            self.again_button.draw(surface)
            self.result_menu_button.draw(surface)
        else:
            out = self.med.render("You're out of chips!", True, LIGHT_RED)
            surface.blit(out, out.get_rect(center=(WIDTH // 2, 565)))
            self.out_menu_button.draw(surface)