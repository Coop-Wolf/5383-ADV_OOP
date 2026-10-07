
import pygame
from .screenUI import Screen
from UI.widgets import Button
from UI.chips import BetPanel
from UI.cards import draw_hand, CARD_W
from Classes.player import Player
from Classes.Blackjack.blackjack import Blackjack
 
from UI.constants import (
    WIDTH, FELT_GREEN, WHITE, GOLD, GRAY, LIGHT_GRAY, LIGHT_RED,
    FONT_NAME, FONT_SIZE_TITLE, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL,)
 
 
DEALER_STEP_MS = 800        # pause between dealer steps (reveal, each draw, result)
 
DEALER_CARDS_Y = 215
PLAYER_CARDS_Y = 450
RESULT_Y = 560
BUTTON_Y = 615
 
# Screen action name -> Blackjack method
ACTIONS = [
    ("hit", "Hit", "hit"),
    ("stand", "Stand", "stand"),
    ("double", "Double", "double_down"),
    ("split", "Split", "split"),
]
 
 
def _draw_disabled(surface, button):
    pygame.draw.rect(surface, GRAY, button.rect, border_radius=8)
    pygame.draw.rect(surface, LIGHT_GRAY, button.rect, width=2, border_radius=8)
    label = button.font.render(button.text, True, LIGHT_GRAY)
    surface.blit(label, label.get_rect(center=button.rect.center))
 
 
class BlackjackScreen(Screen):
    """
    States:
        BET     - player places a bet with chips
        PLAYER  - player chooses Hit / Stand / Double / Split for each hand
        DEALER  - dealer reveals the hole card and draws, one step at a time
        RESULT  - outcome shown, Play Again / Menu
    """
 
    def __init__(self, app, menu):
        super().__init__(app)
        self.menu = menu
 
        self.title_font = pygame.font.Font(FONT_NAME, FONT_SIZE_TITLE)
        self.large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.med = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.small = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)
 
        # The game itself: all the rules live in the Blackjack class
        casino_player = Player(
            app.player["username"], app.player["chips"], app.player["id"])
        self.game = Blackjack(casino_player, db=app.db)
 
        self.panel = BetPanel(balance=app.player["chips"])
 
        self.menu_button = Button(30, 630, 120, 45, "Menu", font_size=FONT_SIZE_SMALL)
        self.again_button = Button(WIDTH // 2 - 180, BUTTON_Y, 170, 50, "Play Again")
        self.result_menu_button = Button(WIDTH // 2 + 10, BUTTON_Y, 170, 50, "Menu")
        self.out_menu_button = Button(WIDTH // 2 - 85, BUTTON_Y, 170, 50, "Menu")
 
        # Hit / Stand / Double / Split along the bottom
        bw, gap = 150, 15
        x = (WIDTH - (len(ACTIONS) * bw + (len(ACTIONS) - 1) * gap)) // 2
        self.action_buttons = {}
        for i, (action, label, _method) in enumerate(ACTIONS):
            self.action_buttons[action] = Button(x + i * (bw + gap), BUTTON_Y, bw, 50, label)
 
        self.state = "BET"
        self.state_start = 0
        self.bet = 0
        self.dealer_revealed = False
 
    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------
    def _set_state(self, state):
        self.state = state
        self.state_start = pygame.time.get_ticks()
 
    def _go_to_menu(self):
        self.app.change_screen(self.menu)
 
    def _deal(self):
        self.bet = self.panel.bet
        self.dealer_revealed = False
 
        self.game.deal(self.bet)
 
        if self.game.player_turn_over:
            self._start_dealer()        # starting 21: nothing to decide
        else:
            self._set_state("PLAYER")
 
    def _start_dealer(self):
        self.dealer_revealed = False
        self._set_state("DEALER")
 
    # ------------------------------------------------------------------
    # Screen interface
    # ------------------------------------------------------------------
    def handle_event(self, event):
 
        if self.state == "BET":
            if self.panel.handle_event(event):
                self._deal()
            elif self.menu_button.handle_event(event):
                self._go_to_menu()
 
        elif self.state == "PLAYER":
            available = self.game.available_actions()
 
            for action, _label, method in ACTIONS:
                if action in available and self.action_buttons[action].handle_event(event):
                    getattr(self.game, method)()
 
                    if self.game.player_turn_over:
                        self._start_dealer()
                    break
 
        elif self.state == "RESULT":
            if self.app.player["chips"] > 0:
                if self.again_button.handle_event(event):
                    self.panel.reset(self.app.player["chips"])
                    self._set_state("BET")
                elif self.result_menu_button.handle_event(event):
                    self._go_to_menu()
            elif self.out_menu_button.handle_event(event):
                self._go_to_menu()
 
    def update(self):
        if self.state != "DEALER":
            return
 
        if pygame.time.get_ticks() - self.state_start < DEALER_STEP_MS:
            return
 
        if not self.dealer_revealed:
            self.dealer_revealed = True
 
        elif self.game.dealer_needs_to_play and self.game.dealer_should_hit():
            self.game.dealer_hit()
 
        else:
            # Dealer is done: settle every hand (this also saves to the database)
            self.game.determine_winner()
            self.app.player["chips"] = self.game.blackjack_player.chips
            self._set_state("RESULT")
            return
 
        self.state_start = pygame.time.get_ticks()
 
    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw(self, surface):
        surface.fill(FELT_GREEN)
 
        # Header: name on the left, chips on the right
        name = self.med.render(self.app.player["username"], True, WHITE)
        surface.blit(name, (30, 25))
 
        if self.state == "BET":
            chips_now = self.panel.remaining
        else:
            chips_now = self.game.blackjack_player.chips
        chips = self.med.render(f"Chips: {chips_now}", True, GOLD)
        surface.blit(chips, chips.get_rect(topright=(WIDTH - 30, 25)))
 
        # Title
        title = self.title_font.render("BLACKJACK", True, GOLD)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 55)))
 
        if self.state == "BET":
            rules = self.small.render(
                "Get closer to 21 than the dealer. Blackjack pays 3 to 2. Dealer hits to 17.",
                True, WHITE)
            surface.blit(rules, rules.get_rect(center=(WIDTH // 2, 120)))
            self.panel.draw(surface)
            self.menu_button.draw(surface)
            return
 
        self._draw_dealer(surface)
        self._draw_player_hands(surface)
 
        if self.state == "PLAYER":
            self._draw_action_buttons(surface)
        elif self.state == "RESULT":
            self._draw_result(surface)
 
    def _draw_dealer(self, surface):
        dealer = self.game.dealer
        hidden = () if self.dealer_revealed else (1,)
 
        draw_hand(surface, dealer.hand.cards, (WIDTH // 2, DEALER_CARDS_Y),
                  self.med, hidden=hidden)
 
        text = "DEALER"
        if self.dealer_revealed:
            text += f": {dealer.get_hand_value()}"
            if dealer.is_bust():
                text += "  Bust"
 
        label = self.small.render(text, True, WHITE)
        surface.blit(label, label.get_rect(center=(WIDTH // 2, 108)))
 
    def _draw_player_hands(self, surface):
        player = self.game.blackjack_player
        hands = player.hands
        count = len(hands)
        slot_w = (WIDTH - 60) / count
 
        for i, hand in enumerate(hands):
            cx = int(30 + slot_w * (i + 0.5))
 
            # Squeeze the overlap when a hand has many cards or there are several hands
            cards = len(hand.cards)
            available_w = slot_w - CARD_W - 20
            offset = 40 if cards <= 1 else int(max(16, min(40, available_w / (cards - 1))))
 
            rect = draw_hand(surface, hand.cards, (cx, PLAYER_CARDS_Y), self.med, offset=offset)
 
            # Highlight the hand being played after a split
            if self.state == "PLAYER" and count > 1 and i == player.active_index:
                pygame.draw.rect(surface, GOLD, rect.inflate(16, 16), width=3, border_radius=12)
 
            name = "YOU" if count == 1 else f"HAND {i + 1}"
            top = self.small.render(f"{name}: {hand.get_value()}", True, WHITE)
            surface.blit(top, top.get_rect(center=(cx, 322)))
 
            text, color = self._hand_line(i, hand)
            line = self.small.render(text, True, color)
            surface.blit(line, line.get_rect(center=(cx, 344)))
 
    def _hand_line(self, index, hand):
        """Second label line under a hand: bet and status, or the result."""
 
        if self.state == "RESULT" and index < len(self.game.results):
            result = self.game.results[index]
            net = result["net_change"]
 
            if result["outcome"] == "win":
                return f"{result['detail']}  +${net}", GOLD
            if result["outcome"] == "loss":
                return f"{result['detail']}  -${hand.bet}", LIGHT_RED
            return f"{result['detail']}  bet returned", WHITE
 
        status = ""
        if hand.is_bust():
            status = "  Bust"
        elif hand.is_blackjack():
            status = "  Blackjack"
        elif hand.stood:
            status = "  Stand"
 
        return f"Bet ${hand.bet}{status}", LIGHT_GRAY
 
    def _draw_action_buttons(self, surface):
        available = self.game.available_actions()
 
        for action, _label, _method in ACTIONS:
            button = self.action_buttons[action]
            if action in available:
                button.draw(surface)
            else:
                _draw_disabled(surface, button)
 
    def _draw_result(self, surface):
        net = sum(r["net_change"] if r["outcome"] == "win" else
                  (-hand.bet if r["outcome"] == "loss" else 0)
                  for r, hand in zip(self.game.results, self.game.blackjack_player.hands))
 
        if net > 0:
            text, color = f"You win!  +${net}", GOLD
        elif net < 0:
            text, color = f"You lose  -${abs(net)}", LIGHT_RED
        else:
            text, color = "Push - nothing won or lost", WHITE
 
        result = self.large.render(text, True, color)
        surface.blit(result, result.get_rect(center=(WIDTH // 2, RESULT_Y)))
 
        if self.app.player["chips"] > 0:
            self.again_button.draw(surface)
            self.result_menu_button.draw(surface)
        else:
            out = self.med.render("You're out of chips!", True, LIGHT_RED)
            surface.blit(out, out.get_rect(center=(WIDTH // 2, 598)))
            self.out_menu_button.draw(surface)
 
