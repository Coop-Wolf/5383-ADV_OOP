import pygame

from .screenUI import Screen
from UI.widgets import Button
from UI.chips import BetPanel
from UI.cards import draw_hand, CARD_W, CARD_H
from Classes.player import Player
from Classes.VideoPoker.videopoker import VideoPoker

from UI.constants import (
    WIDTH,
    FELT_GREEN,
    WHITE,
    GOLD,
    LIGHT_RED,
    FONT_NAME,
    FONT_SIZE_TITLE,
    FONT_SIZE_LARGE,
    FONT_SIZE_MEDIUM,
    FONT_SIZE_SMALL,
)


class VideoPokerScreen(Screen):

    def __init__(self, app, menu):
        super().__init__(app)
        self.menu = menu

        self.title_font = pygame.font.Font(
            FONT_NAME, FONT_SIZE_TITLE
        )
        self.large = pygame.font.Font(
            FONT_NAME, FONT_SIZE_LARGE
        )
        self.med = pygame.font.Font(
            FONT_NAME, FONT_SIZE_MEDIUM
        )
        self.small = pygame.font.Font(
            FONT_NAME, FONT_SIZE_SMALL
        )

        # ----------------------------------------------------------
        # Backend game
        # ----------------------------------------------------------

        casino_player = Player(
            app.player["username"],
            app.player["chips"],
            app.player["id"],
        )

        self.game = VideoPoker(
            casino_player,
            db=app.db,
        )

        # ----------------------------------------------------------
        # Betting / buttons
        # ----------------------------------------------------------

        self.panel = BetPanel(
            balance=app.player["chips"]
        )

        # Same menu position as Blackjack and War
        self.menu_button = Button(
            30,
            630,
            120,
            45,
            "Menu",
            font_size=FONT_SIZE_SMALL,
        )

        self.draw_button = Button(
            WIDTH // 2 - 85,
            600,
            170,
            50,
            "Draw",
        )

        self.again_button = Button(
            WIDTH // 2 - 180,
            600,
            170,
            50,
            "Play Again",
        )

        self.result_menu_button = Button(
            WIDTH // 2 + 10,
            600,
            170,
            50,
            "Menu",
        )

        self.out_menu_button = Button(
            WIDTH // 2 - 85,
            600,
            170,
            50,
            "Menu",
        )

        # ----------------------------------------------------------
        # Game state
        # ----------------------------------------------------------

        self.state = "BET"

        self.bet = 0
        self.held = set()

        self.hand_name = None
        self.payout = 0
        self.net_change = 0

        self.shown_chips = app.player["chips"]

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------

    def _set_state(self, state):
        self.state = state

    def _go_to_menu(self):
        self.app.change_screen(self.menu)

    # ------------------------------------------------------------------
    # Game actions
    # ------------------------------------------------------------------

    def _deal(self):
        self.bet = self.panel.bet

        # Backend handles the bet and deals five cards.
        self.game.deal(self.bet)

        self.held.clear()
        self.hand_name = None
        self.payout = 0
        self.net_change = 0

        # Bet has now been removed from the player's balance.
        self.shown_chips = self.app.player["chips"] - self.bet

        self._set_state("DRAW")

    def _draw(self):
        # Replace every card that was not held.
        self.game.draw(self.held)

        # Evaluate and settle the hand.
        self.hand_name, self.payout = self.game.determine_winner()

        self.net_change = self.game.net_change

        # Update the main casino player's balance.
        self.app.player["chips"] = self.game.player.chips

        self.shown_chips = self.app.player["chips"]

        self.held.clear()

        self._set_state("RESULT")

    # ------------------------------------------------------------------
    # Card interaction
    # ------------------------------------------------------------------

    def _handle_card_click(self, position):
        cards = self.game.video_player.hand.cards

        if len(cards) != 5:
            return

        # Match the spacing used when drawing the hand.
        offset = 130

        total_width = CARD_W + 4 * offset
        left = WIDTH // 2 - total_width // 2

        for index in range(5):

            x = left + CARD_W // 2 + index * offset

            rect = pygame.Rect(
                0,
                0,
                CARD_W,
                CARD_H,
            )

            rect.center = (
                x,
                360,
            )

            if rect.collidepoint(position):

                # Toggle held/unheld.
                if index in self.held:
                    self.held.remove(index)
                else:
                    self.held.add(index)

                break

    # ------------------------------------------------------------------
    # Screen interface
    # ------------------------------------------------------------------

    def handle_event(self, event):

        # --------------------------------------------------------------
        # Betting phase
        # --------------------------------------------------------------

        if self.state == "BET":

            # BetPanel handles chip selection, Clear, and Deal.
            if self.panel.handle_event(event):
                self._deal()

            elif self.menu_button.handle_event(event):
                self._go_to_menu()

        # --------------------------------------------------------------
        # Card selection phase
        # --------------------------------------------------------------

        elif self.state == "DRAW":

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._handle_card_click(event.pos)

            if self.draw_button.handle_event(event):
                self._draw()

            elif self.menu_button.handle_event(event):
                self._go_to_menu()

        # --------------------------------------------------------------
        # Result phase
        # --------------------------------------------------------------

        elif self.state == "RESULT":

            if self.app.player["chips"] > 0:

                if self.again_button.handle_event(event):

                    self.panel.reset(
                        self.app.player["chips"]
                    )

                    self.shown_chips = (
                        self.app.player["chips"]
                    )

                    self.held.clear()
                    self.hand_name = None
                    self.payout = 0
                    self.net_change = 0

                    self._set_state("BET")

                elif self.result_menu_button.handle_event(event):
                    self._go_to_menu()

            elif self.out_menu_button.handle_event(event):
                self._go_to_menu()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, surface):

        surface.fill(FELT_GREEN)

        # --------------------------------------------------------------
        # Header
        # --------------------------------------------------------------

        # Player name — same location as Blackjack/War
        name = self.med.render(
            self.app.player["username"],
            True,
            WHITE,
        )

        surface.blit(
            name,
            (30, 25),
        )

        # Chips — same location as Blackjack/War
        if self.state == "BET":
            chips_now = self.panel.remaining
        else:
            chips_now = self.shown_chips

        chips = self.med.render(
            f"Chips: {chips_now}",
            True,
            GOLD,
        )

        surface.blit(
            chips,
            chips.get_rect(
                topright=(WIDTH - 30, 25)
            ),
        )

        # --------------------------------------------------------------
        # Title
        # --------------------------------------------------------------

        title = self.title_font.render(
            "VIDEO POKER",
            True,
            GOLD,
        )

        surface.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 110)
            ),
        )

        # --------------------------------------------------------------
        # Betting screen
        # --------------------------------------------------------------

        if self.state == "BET":

            rules = self.small.render(
                "Get the best five-card poker hand. "
                "Jacks or Better pays 1 to 1.",
                True,
                WHITE,
            )

            surface.blit(
                rules,
                rules.get_rect(
                    center=(WIDTH // 2, 165)
                ),
            )

            # BetPanel contains the chips, Clear button, and Deal button.
            self.panel.draw(surface)

            self.menu_button.draw(surface)

            return

        # --------------------------------------------------------------
        # Game / result screen
        # --------------------------------------------------------------

        rules = self.small.render(
            "Click cards to hold them, then click Draw.",
            True,
            WHITE,
        )

        surface.blit(
            rules,
            rules.get_rect(
                center=(WIDTH // 2, 165)
            ),
        )

        self._draw_hand(surface)

        # --------------------------------------------------------------
        # Draw state
        # --------------------------------------------------------------

        if self.state == "DRAW":

            bet = self.med.render(
                f"Bet: ${self.bet}",
                True,
                GOLD,
            )

            surface.blit(
                bet,
                bet.get_rect(
                    center=(WIDTH // 2, 500)
                ),
            )

            self.draw_button.draw(surface)
            self.menu_button.draw(surface)

        # --------------------------------------------------------------
        # Result state
        # --------------------------------------------------------------

        elif self.state == "RESULT":

            self._draw_result(surface)

    # ------------------------------------------------------------------
    # Draw cards
    # ------------------------------------------------------------------

    def _draw_hand(self, surface):

        cards = self.game.video_player.hand.cards

        draw_hand(
            surface,
            cards,
            (WIDTH // 2, 340),
            self.med,
            offset=130,
            selected=self.held,
        )

        # Labels underneath the cards.
        if self.state == "DRAW":

            held_count = len(self.held)

            if held_count == 0:
                text = "No cards held"
            elif held_count == 5:
                text = "All cards held"
            else:
                text = f"{held_count} card(s) held"

            label = self.small.render(
                text,
                True,
                WHITE,
            )

            surface.blit(
                label,
                label.get_rect(
                    center=(WIDTH // 2, 455)
                ),
            )

    # ------------------------------------------------------------------
    # Result
    # ------------------------------------------------------------------

    def _draw_result(self, surface):

        # Hand name
        result = self.large.render(
            self.hand_name,
            True,
            GOLD,
        )

        surface.blit(
            result,
            result.get_rect(
                center=(WIDTH // 2, 475)
            ),
        )

        # Payout/result message
        if self.net_change > 0:

            text = f"You win!  +${self.net_change}"
            color = GOLD

        elif self.net_change < 0:

            text = f"You lose  -${abs(self.net_change)}"
            color = LIGHT_RED

        else:

            if self.hand_name == "Pair":
                text = "No payout - Pair must be Jacks or Better"
            elif self.payout == 1:
                text = "Jacks or Better - Bet returned"
            else:
                text = "No payout"

            color = WHITE

        payout = self.med.render(
            text,
            True,
            color,
        )

        surface.blit(
            payout,
            payout.get_rect(
                center=(WIDTH // 2, 530)
            ),
        )

        # --------------------------------------------------------------
        # Buttons
        # --------------------------------------------------------------

        if self.app.player["chips"] > 0:

            self.again_button.draw(surface)
            self.result_menu_button.draw(surface)

        else:

            out = self.med.render(
                "You're out of chips!",
                True,
                LIGHT_RED,
            )

            surface.blit(
                out,
                out.get_rect(
                    center=(WIDTH // 2, 565)
                ),
            )

            self.out_menu_button.draw(surface)