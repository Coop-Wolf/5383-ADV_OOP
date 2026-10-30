import pygame
from UI.constants import WHITE, GOLD, GRAY, DARK

CHAT_CYAN = (80, 220, 255)
SYSTEM_GRAY = (180, 180, 180)
ANNOUNCEMENT_GOLD = (255, 215, 0)

class ChatOverlay:
    def __init__(self, chat_client, font, screen_width=1280, screen_height=720):
        self.client = chat_client
        self.font = font
        self.active = False
        self.input_text = ""

        # Dimensions & bottom-right coordinates
        box_w, box_h = 200, 150
        input_h = 32
        margin_x = 300   # distance from the right edge (bigger = further left)
        margin_y = 100   # distance from the bottom edge (bigger = further up)

        box_x = screen_width - box_w - margin_x
        input_y = screen_height - input_h - margin_y
        box_y = input_y - box_h - 6

        self.rect = pygame.Rect(box_x, box_y, box_w, box_h)
        self.input_rect = pygame.Rect(box_x, input_y, box_w, input_h)

    def _wrap_text(self, text, max_w):
        """Splits raw text into a list of lines that fit within max_w pixels."""
        words = text.split(" ")
        lines = []
        cur_line = ""
        for word in words:
            candidate = f"{cur_line} {word}".strip() if cur_line else word
            if self.font.size(candidate)[0] <= max_w:
                cur_line = candidate
            else:
                if cur_line:
                    lines.append(cur_line)
                # Split extremely long individual words that exceed max_w on their own
                if self.font.size(word)[0] > max_w:
                    partial = ""
                    for ch in word:
                        if self.font.size(partial + ch)[0] <= max_w:
                            partial += ch
                        else:
                            lines.append(partial)
                            partial = ch
                    cur_line = partial
                else:
                    cur_line = word
        if cur_line:
            lines.append(cur_line)
        return lines

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if not self.active:
                if event.key in (pygame.K_RETURN, pygame.K_t):
                    self.active = True
                    self.input_text = ""
                    return True
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
                    if len(self.input_text) < 120 and event.unicode.isprintable():
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

        # Prepare rendered visual lines (bottom-up fill)
        max_content_w = self.rect.w - 16
        line_height = self.font.get_linesize()
        rendered_lines = []

        for msg in list(self.client.messages):
            m_type = msg.get("type")
            if m_type == "chat":
                prefix = f"{msg['sender']}: "
                prefix_w = self.font.size(prefix)[0]
                body_lines = self._wrap_text(msg["text"], max_content_w - prefix_w)
                if body_lines:
                    rendered_lines.append((prefix, body_lines[0], CHAT_CYAN, WHITE))
                    for extra in body_lines[1:]:
                        rendered_lines.append(("", extra, CHAT_CYAN, WHITE))
            elif m_type == "announcement":
                for line in self._wrap_text(f"★ {msg['text']}", max_content_w):
                    rendered_lines.append(("", line, ANNOUNCEMENT_GOLD, ANNOUNCEMENT_GOLD))
            else:
                for line in self._wrap_text(msg.get("text", ""), max_content_w):
                    rendered_lines.append(("", line, SYSTEM_GRAY, SYSTEM_GRAY))

        # Blit lines starting from the bottom of the log panel
        cur_y = self.rect.bottom - line_height - 6
        for prefix, text, prefix_col, text_col in reversed(rendered_lines):
            if cur_y < self.rect.y + 4:
                break
            x_offset = self.rect.x + 8
            if prefix:
                p_surf = self.font.render(prefix, True, prefix_col)
                surface.blit(p_surf, (x_offset, cur_y))
                x_offset += p_surf.get_width()
            t_surf = self.font.render(text, True, text_col)
            surface.blit(t_surf, (x_offset, cur_y))
            cur_y -= line_height

        # Draw active text input field
        if self.active:
            inp_surf = pygame.Surface((self.input_rect.w, self.input_rect.h), pygame.SRCALPHA)
            inp_surf.fill((20, 20, 25, 220))
            surface.blit(inp_surf, self.input_rect.topleft)
            pygame.draw.rect(surface, GOLD, self.input_rect, 2, border_radius=6)

            txt = self.font.render(self.input_text + "_", True, WHITE)
            surface.blit(txt, (self.input_rect.x + 8, self.input_rect.y + 6))