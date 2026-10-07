import pygame
from .screenUI import Screen
from UI.widgets import Button
from UI.chips import BetPanel
from Classes.deck import Deck
 
from UI.constants import (
    WIDTH, FELT_GREEN, DARK_GREEN, WHITE, BLACK, GOLD, LIGHT_GRAY, LIGHT_RED,
    FONT_NAME, FONT_SIZE_TITLE, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL,)
 
 
CARD_W, CARD_H = 120, 170
CARD_RED = (200, 30, 30)
CARD_BACK = (30, 60, 150)
CARD_BACK_LIGHT = (90, 130, 220)
RANK_LABELS = {"Jack": "J", "Queen": "Q", "King": "K", "Ace": "A"}
 
DEAL_MS = 900       # player card shown, dealer card face down
REVEAL_MS = 900     # both cards shown before the result appears
 
 
def draw_suit(surface, suit, center, s, color):
    """Draw a suit symbol with shapes. s is roughly half the symbol's height."""
 
    cx, cy = center
 
    if suit == "Diamonds":
        pygame.draw.polygon(surface, color, [
            (cx, cy - s), (cx + 0.7 * s, cy), (cx, cy + s), (cx - 0.7 * s, cy)])
 
    elif suit == "Hearts":
        r = int(0.52 * s)
        pygame.draw.circle(surface, color, (int(cx - 0.48 * s), int(cy - 0.28 * s)), r)
        pygame.draw.circle(surface, color, (int(cx + 0.48 * s), int(cy - 0.28 * s)), r)
        pygame.draw.polygon(surface, color, [
            (cx - 0.98 * s, cy - 0.12 * s), (cx + 0.98 * s, cy - 0.12 * s), (cx, cy + 0.95 * s)])
 
    elif suit == "Spades":
        r = int(0.52 * s)
        pygame.draw.circle(surface, color, (int(cx - 0.48 * s), int(cy + 0.2 * s)), r)
        pygame.draw.circle(surface, color, (int(cx + 0.48 * s), int(cy + 0.2 * s)), r)
        pygame.draw.polygon(surface, color, [
            (cx - 0.98 * s, cy + 0.05 * s), (cx + 0.98 * s, cy + 0.05 * s), (cx, cy - 0.95 * s)])
        pygame.draw.polygon(surface, color, [
            (cx, cy + 0.2 * s), (cx - 0.3 * s, cy + 0.95 * s), (cx + 0.3 * s, cy + 0.95 * s)])
 
    else:  # Clubs
        r = int(0.4 * s)
        pygame.draw.circle(surface, color, (int(cx), int(cy - 0.5 * s)), r)
        pygame.draw.circle(surface, color, (int(cx - 0.5 * s), int(cy + 0.2 * s)), r)
        pygame.draw.circle(surface, color, (int(cx + 0.5 * s), int(cy + 0.2 * s)), r)
        pygame.draw.polygon(surface, color, [
            (cx, cy + 0.1 * s), (cx - 0.3 * s, cy + 0.95 * s), (cx + 0.3 * s, cy + 0.95 * s)])
 
 
def draw_card(surface, center, card, face_up, font):
    """Draw a playing card (face up or face down) using only pygame shapes."""
 
    rect = pygame.Rect(0, 0, CARD_W, CARD_H)
    rect.center = center
 
    # Drop shadow
    pygame.draw.rect(surface, DARK_GREEN, rect.move(3, 4), border_radius=10)
 
    # Card back
    if not face_up:
        pygame.draw.rect(surface, CARD_BACK, rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, rect, width=3, border_radius=10)
        inner = rect.inflate(-24, -24)
        pygame.draw.rect(surface, CARD_BACK_LIGHT, inner, width=2, border_radius=6)
        cx, cy = rect.center
        pygame.draw.polygon(surface, CARD_BACK_LIGHT, [
            (cx, inner.top + 10), (inner.right - 10, cy),
            (cx, inner.bottom - 10), (inner.left + 10, cy)], width=2)
        return
 
    # Card face
    color = CARD_RED if card.suit in ("Hearts", "Diamonds") else BLACK
    pygame.draw.rect(surface, WHITE, rect, border_radius=10)
    pygame.draw.rect(surface, LIGHT_GRAY, rect, width=2, border_radius=10)
 
    rank = RANK_LABELS.get(card.rank, card.rank)
    label = font.render(rank, True, color)
    surface.blit(label, (rect.x + 10, rect.y + 8))
    draw_suit(surface, card.suit, (rect.x + 10 + label.get_width() // 2, rect.y + 8 + label.get_height() + 12), 9, color)
 
    draw_suit(surface, card.suit, (rect.centerx, rect.centery + 8), 32, color)
 
 
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
 
        self.menu_button = Button(30, 630, 120, 45, "Menu", font_size=FONT_SIZE_SMALL)
        self.again_button = Button(WIDTH // 2 - 180, 600, 170, 50, "Play Again")
        self.result_menu_button = Button(WIDTH // 2 + 10, 600, 170, 50, "Menu")
        self.out_menu_button = Button(WIDTH // 2 - 85, 600, 170, 50, "Menu")
 
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
 
        # Saved right away so closing the window mid-round can't dodge a loss
        new_balance = self.app.db.record_result(
            self.app.player["id"], "War", self.outcome, net_change)
        self.app.player["chips"] = new_balance
 
        # The header keeps showing the chips minus the bet until the result appears
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
 
        # Header: name on the left, chips on the right
        name = self.med.render(self.app.player["username"], True, WHITE)
        surface.blit(name, (30, 25))
 
        chips_now = self.panel.remaining if self.state == "BET" else self.shown_chips
        chips = self.med.render(f"Chips: {chips_now}", True, GOLD)
        surface.blit(chips, chips.get_rect(topright=(WIDTH - 30, 25)))
 
        # Title and rules
        title = self.title_font.render("WAR", True, GOLD)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 110)))
        rules = self.small.render(
            "Higher card wins and pays 1 to 1. Aces are high. A tie returns your bet.",
            True, WHITE)
        surface.blit(rules, rules.get_rect(center=(WIDTH // 2, 165)))
 
        if self.state == "BET":
            self.panel.draw(surface)
            self.menu_button.draw(surface)
            return
 
        # Cards
        you_x, dealer_x, card_y = WIDTH // 2 - 140, WIDTH // 2 + 140, 340
        for text, x in (("YOU", you_x), ("DEALER", dealer_x)):
            label = self.med.render(text, True, WHITE)
            surface.blit(label, label.get_rect(center=(x, 225)))
 
        dealer_up = self.state in ("REVEAL", "RESULT")
        draw_card(surface, (you_x, card_y), self.player_card, True, self.med)
        draw_card(surface, (dealer_x, card_y), self.dealer_card, dealer_up, self.med)
 
        bet = self.med.render(f"Bet: ${self.bet}", True, GOLD)
        surface.blit(bet, bet.get_rect(center=(WIDTH // 2, 465)))
 
        if self.state != "RESULT":
            return
 
        # Result
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
 
