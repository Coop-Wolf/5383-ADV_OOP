"""

Main entry point for the Casino App.

    Initializes the Pygame window, the database, and the first screen (LoginScreen).
    Sets up the main loop.
    Manages screen transitions.
    Scales the 1000x700 virtual canvas and remaps mouse coordinates on resize/maximize.

"""

import pygame
from UI.constants import WIDTH, HEIGHT, FPS, TITLE, FELT_GREEN
from UI.screens.loginUI import LoginScreen
from Database.database import Database
from UI.chips import create_chip_icon


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_icon(create_chip_icon(32))
        self.window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # Fixed internal canvas where all game screens draw
        self.canvas = pygame.Surface((WIDTH, HEIGHT))

        # Scaling and centering offsets
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self.db = Database()
        self.player = None
        self.current = LoginScreen(self)

        # Hook into Pygame's mouse polling so button hover checks
        # across all screens automatically receive virtual canvas coordinates
        self._real_get_pos = pygame.mouse.get_pos
        pygame.mouse.get_pos = self._get_canvas_mouse_pos

    def _get_canvas_mouse_pos(self):
        """Translates raw OS mouse coordinates to the 1000x700 virtual canvas."""
        raw_x, raw_y = self._real_get_pos()
        if self.scale <= 0:
            return raw_x, raw_y

        adj_x = int((raw_x - self.offset_x) / self.scale)
        adj_y = int((raw_y - self.offset_y) / self.scale)

        clamped_x = max(0, min(WIDTH - 1, adj_x))
        clamped_y = max(0, min(HEIGHT - 1, adj_y))
        return clamped_x, clamped_y

    def change_screen(self, screen):
        self.current = screen

    def _update_scale_and_offsets(self, win_w, win_h):
        """Compute aspect-ratio preserved scaling factor and centering offsets."""
        scale_x = win_w / WIDTH
        scale_y = win_h / HEIGHT
        self.scale = min(scale_x, scale_y)

        scaled_w = int(WIDTH * self.scale)
        scaled_h = int(HEIGHT * self.scale)

        self.offset_x = (win_w - scaled_w) // 2
        self.offset_y = (win_h - scaled_h) // 2

    def _transform_mouse_event(self, event):
        """Remap event.pos coordinates back to the virtual canvas space."""
        if not hasattr(event, "pos"):
            return event

        canvas_x, canvas_y = self._get_canvas_mouse_pos()
        event_dict = dict(event.__dict__)
        event_dict["pos"] = (canvas_x, canvas_y)
        return pygame.event.Event(event.type, event_dict)

    def run(self):
        running = True
        while running:
            win_w, win_h = self.window.get_size()
            self._update_scale_and_offsets(win_w, win_h)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                else:
                    if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                        # Block clicks occurring outside the canvas (in the border areas)
                        raw_mx, raw_my = self._real_get_pos()
                        scaled_w = int(WIDTH * self.scale)
                        scaled_h = int(HEIGHT * self.scale)
                        canvas_rect = pygame.Rect(self.offset_x, self.offset_y, scaled_w, scaled_h)

                        if event.type == pygame.MOUSEBUTTONDOWN and not canvas_rect.collidepoint(raw_mx, raw_my):
                            continue

                        event = self._transform_mouse_event(event)

                    self.current.handle_event(event)

            self.current.update()

            # 1. Render game screen directly onto the 1000x700 virtual canvas
            self.current.draw(self.canvas)

            # 2. Scale the canvas to fit the maximized display
            scaled_w = int(WIDTH * self.scale)
            scaled_h = int(HEIGHT * self.scale)
            scaled_canvas = pygame.transform.smoothscale(self.canvas, (scaled_w, scaled_h))

            # 3. Clear window with felt green and blit canvas centered
            self.window.fill(FELT_GREEN)
            self.window.blit(scaled_canvas, (self.offset_x, self.offset_y))

            pygame.display.flip()
            self.clock.tick(FPS)

        self.db.close()
        pygame.quit()


if __name__ == "__main__":
    App().run()