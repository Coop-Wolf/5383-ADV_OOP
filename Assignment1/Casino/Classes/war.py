from .game import Game
from .wardealer import Wardealer
from .warplayer import Warplayer

class War(Game):

    def __init__(self, players):
        # Original Casino players
        self.players = players

        # Blackjack-specific players
        self.war_players = [
            WarPlayer(player.name, player.chips)
            for player in players
        ]

        self.wardealer = Wardealer()