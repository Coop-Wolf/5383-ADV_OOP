import pygame
from UI.constants import WHITE, GOLD, GRAY, DARK

CHAT_CYAN = (80, 220, 255)
SYSTEM_GRAY = (180, 180, 180)
ANNOUNCEMENT_GOLD = (255, 215, 0)
HINT_COLOR = (150, 150, 165)

class ChatOverlay:
    def __init__(self, chat_client, font, screen_width=1280, screen_height=720):
        self.client = chat_client
        self.font = font
        self.active = False
        self.input_text = ""

        # Visibility and mode states
        self.visible = True          # Toggled with 'H' (Hide completely)
        self.shadow_mode = False     # Toggled with 'B' Hides menu bar
        self.scroll_offset = 0       # 0 = locked to newest messages
        self.last_msg_count = 0

        # Dimensions & bottom-right coordinates
        box_w, box_h = 240, 160
        toolbar_h = 18
        input_h = 32
        margin_x = 300   # distance from right edge
        margin_y = 100   # distance from bottom edge

        box_x = screen_width - box_w - margin_x
        input_y = screen_height - input_h - margin_y
        box_y = input_y - box_h - 6
        toolbar_y = box_y - toolbar_h - 4

        self.toolbar_rect = pygame.Rect(box_x, toolbar_y, box_w, toolbar_h)
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
        # 1. Hotkeys when not actively typing in the input box
        if event.type == pygame.KEYDOWN and not self.active:
            if event.key == pygame.K_h:
                self.visible = not self.visible
                return True
            elif event.key == pygame.K_b:
                self.shadow_mode = not self.shadow_mode
                return True
            elif event.key in (pygame.K_RETURN, pygame.K_t):
                if not self.visible:
                    self.visible = True
                self.active = True
                self.input_text = ""
                return True

        if not self.visible:
            return False

        # 2. Scrolling history via mouse wheel over the log box
        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.scroll_offset = max(0, self.scroll_offset + event.y)
                return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if event.button == 4:  # Wheel up
                    self.scroll_offset += 1
                    return True
                elif event.button == 5:  # Wheel down
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                    return True
            elif self.input_rect.collidepoint(event.pos):
                self.active = True
                return True
            else:
                self.active = False

        # 3. Text input handling
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.input_text.strip():
                    self.client.send_chat(self.input_text)
                self.input_text = ""
                self.active = False
                self.scroll_offset = 0
                return True
            elif event.key == pygame.K_ESCAPE:
                self.active = False
                self.input_text = ""
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
                return True
            else:
                if len(self.input_text) < 120 and event.unicode and event.unicode.isprintable():
                    self.input_text += event.unicode
                return True

        return False

    def draw(self, surface):
        if not self.client.connected or not self.visible:
            return

        line_height = self.font.get_linesize()
        max_content_w = self.rect.w - 16

        # Snap to bottom if new messages arrived
        current_msg_count = len(self.client.messages)
        if current_msg_count != self.last_msg_count:
            self.scroll_offset = 0
            self.last_msg_count = current_msg_count

        # 1. Render Toolbar / Action Legend
        if not self.shadow_mode:
            toolbar_surf = pygame.Surface((self.toolbar_rect.w, self.toolbar_rect.h), pygame.SRCALPHA)
            toolbar_surf.fill((10, 10, 15, 200))
            surface.blit(toolbar_surf, self.toolbar_rect.topleft)
            pygame.draw.rect(surface, (60, 60, 70), self.toolbar_rect, 1, border_radius=4)
            hint_txt = self.font.render("[Enter] Chat  [H] Hide  [B] Shadow", True, HINT_COLOR)
            surface.blit(hint_txt, (self.toolbar_rect.x + 6, self.toolbar_rect.y + 2))

        # 2. Render Log Box Panel Background
        if not self.shadow_mode:
            log_surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
            log_surf.fill((15, 15, 20, 180 if self.active else 100))
            surface.blit(log_surf, self.rect.topleft)
            pygame.draw.rect(surface, (70, 70, 80) if not self.active else GOLD, self.rect, 1, border_radius=6)
        else:
            # Minimalist shadow mode: dim backdrop only
            log_surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
            log_surf.fill((5, 5, 10, 75))
            surface.blit(log_surf, self.rect.topleft)

        # 3. Prepare visual wrapped lines
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

        # Calculate scroll bounds
        max_visible_lines = max(1, (self.rect.h - 10) // line_height)
        max_scroll = max(0, len(rendered_lines) - max_visible_lines)
        self.scroll_offset = min(self.scroll_offset, max_scroll)

        # Slice lines according to scroll offset
        if self.scroll_offset > 0:
            sliced_lines = rendered_lines[:len(rendered_lines) - self.scroll_offset]
        else:
            sliced_lines = rendered_lines

        # Blit messages bottom-up
        cur_y = self.rect.bottom - line_height - 6
        for prefix, text, prefix_col, text_col in reversed(sliced_lines):
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

        # Scroll position indicator
        if self.scroll_offset > 0:
            scroll_indicator = self.font.render(f"▲ +{self.scroll_offset}", True, GOLD)
            surface.blit(scroll_indicator, (self.rect.right - scroll_indicator.get_width() - 8, self.rect.y + 6))

        # 4. Render Active Input Field with dynamic text boundary clipping
        if self.active:
            inp_surf = pygame.Surface((self.input_rect.w, self.input_rect.h), pygame.SRCALPHA)
            inp_surf.fill((20, 20, 25, 230))
            surface.blit(inp_surf, self.input_rect.topleft)
            pygame.draw.rect(surface, GOLD, self.input_rect, 2, border_radius=6)

            cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
            display_str = self.input_text + cursor
            max_input_w = self.input_rect.w - 16

            # Shift text so the typing tail is always visible within the box
            while len(display_str) > 0 and self.font.size(display_str)[0] > max_input_w:
                display_str = display_str[1:]

            txt = self.font.render(display_str, True, WHITE)
            surface.blit(txt, (self.input_rect.x + 8, self.input_rect.y + 6))