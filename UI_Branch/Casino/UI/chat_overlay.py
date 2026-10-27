import pygame
from UI.constants import WHITE, GOLD, GRAY, DARK

CHAT_CYAN = (80, 220, 255)
SYSTEM_GRAY = (180, 180, 180)
ANNOUNCEMENT_GOLD = (255, 215, 0)

class ChatOverlay:
    def __init__(self, chat_client, font):
        self.client = chat_client
        self.font = font
        self.active = False
        self.input_text = ""
        self.rect = pygame.Rect(18, 480, 280, 135)
        self.input_rect = pygame.Rect(18, 620, 280, 32)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if not self.active:
                if event.key in (pygame.K_RETURN, pygame.K_t):
                    self.active = True
                    self.input_text = ""
                    return True  # Event consumed
            else:
                if event.key == pygame.K_RETURN:
                    if self.input_text.strip():
                        self.client.send_chat(self.input_text)
                    self.input_text = ""
                    self.active = False
                    return True
                elif event.key == pygame.K_ESCAPE:
                    self.active = False
                    self.input_text = ""
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                    return True
                else:
                    if len(self.input_text) < 55 and event.unicode.isprintable():
                        self.input_text += event.unicode
                    return True
        return False

    def draw(self, surface):
        if not self.client.connected:
            return

        # Semi-transparent chat log panel
        log_surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        log_surf.fill((15, 15, 20, 160 if self.active else 90))
        surface.blit(log_surf, self.rect.topleft)
        pygame.draw.rect(surface, (70, 70, 80) if not self.active else GOLD, self.rect, 1, border_radius=6)

        # Draw the last 5 incoming messages
        recent = list(self.client.messages)[-5:]
        start_y = self.rect.bottom - 22
        for msg in reversed(recent):
            m_type = msg.get("type")
            if m_type == "chat":
                prefix = f"{msg['sender']}: "
                p_surf = self.font.render(prefix, True, CHAT_CYAN)
                t_surf = self.font.render(msg["text"], True, WHITE)
                surface.blit(p_surf, (self.rect.x + 8, start_y))
                surface.blit(t_surf, (self.rect.x + 8 + p_surf.get_width(), start_y))
            elif m_type == "announcement":
                t_surf = self.font.render(f"★ {msg['text']}", True, ANNOUNCEMENT_GOLD)
                surface.blit(t_surf, (self.rect.x + 8, start_y))
            else:
                t_surf = self.font.render(msg.get("text", ""), True, SYSTEM_GRAY)
                surface.blit(t_surf, (self.rect.x + 8, start_y))

            start_y -= 22

        # Draw active text input field
        if self.active:
            inp_surf = pygame.Surface((self.input_rect.w, self.input_rect.h), pygame.SRCALPHA)
            inp_surf.fill((20, 20, 25, 220))
            surface.blit(inp_surf, self.input_rect.topleft)
            pygame.draw.rect(surface, GOLD, self.input_rect, 2, border_radius=6)

            txt = self.font.render(self.input_text + "_", True, WHITE)
            surface.blit(txt, (self.input_rect.x + 8, self.input_rect.y + 6))