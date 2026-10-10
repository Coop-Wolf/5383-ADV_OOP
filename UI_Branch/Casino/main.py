"""

Main entry point for the Casino App.

    Initializes the Pygame window, the database, and the first screen (LoginScreen).
    Sets up the main loop.
    Manages screen transitions.

"""

import pygame
from UI.constants import WIDTH, HEIGHT, FPS, TITLE
from UI.screens.loginUI import LoginScreen
from Database.database import Database


class App:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.db = Database()
        self.player = None
        self.current = LoginScreen(self)

    def change_screen(self, screen):
        self.current = screen

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.current.handle_event(event)

            self.current.update()
            self.current.draw(self.window)
            pygame.display.flip()
            self.clock.tick(FPS)

        self.db.close()
        pygame.quit()


if __name__ == "__main__":
    App().run()