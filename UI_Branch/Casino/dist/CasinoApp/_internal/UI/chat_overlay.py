import pygame
from UI.constants import WHITE, GOLD

CHAT_CYAN = (80, 220, 255)
SYSTEM_GRAY = (180, 180, 180)
ANNOUNCEMENT_GOLD = (255, 215, 0)
HINT_COLOR = (150, 150, 165)

class ChatOverlay:
    def __init__(self, chat_client, font, screen_width=1000, screen_height=700):
        self.client = chat_client
        self.font = font
        self.active = False
        self.input_text = ""

        # Visibility and scroll states
        self.visible = True          # Toggled with 'H' (Hide/Show completely)
        self.scroll_offset = 0       # 0 = locked to newest messages
        self.last_msg_count = 0

        # Dimensions & positioning
        box_w, box_h = 240, 120
        self.header_h = 20
        input_h = 26
        margin_x = 20    # distance from the right edge (puts box at X = 740)
        margin_y = 98    # distance from the bottom edge

        box_x = screen_width - box_w - margin_x
        input_y = screen_height - input_h - margin_y
        box_y = input_y - box_h - 4

        self.rect = pygame.Rect(box_x, box_y, box_w, box_h)
        self.header_rect = pygame.Rect(box_x, box_y, box_w, self.header_h)
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
        # 1. Hotkeys when idle
        if event.type == pygame.KEYDOWN and not self.active:
            if event.key == pygame.K_h:
                self.visible = not self.visible
                return True
            elif event.key == pygame.K_RETURN:
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

        # 1. Main Background Box
        log_surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        log_surf.fill((15, 15, 20, 180 if self.active else 120))
        surface.blit(log_surf, self.rect.topleft)
        pygame.draw.rect(surface, (70, 70, 80) if not self.active else GOLD, self.rect, 1, border_radius=6)

        # 2. Integrated Top Header / Tool Strip (pinned inside top of box)
        header_surf = pygame.Surface((self.header_rect.w, self.header_rect.h), pygame.SRCALPHA)
        header_surf.fill((25, 25, 35, 200))
        surface.blit(header_surf, self.header_rect.topleft)
        pygame.draw.line(surface, (60, 60, 70), (self.rect.left, self.rect.top + self.header_h), (self.rect.right, self.rect.top + self.header_h), 1)

        hint_txt = self.font.render("Tools: [H] Hide/Show | [Enter] Type", True, HINT_COLOR)
        surface.blit(hint_txt, (self.rect.x + 8, self.rect.y + 2))

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

        # Calculate message viewable area (stops below the header line)
        message_area_h = self.rect.h - self.header_h - 6
        max_visible_lines = max(1, message_area_h // line_height)
        max_scroll = max(0, len(rendered_lines) - max_visible_lines)
        self.scroll_offset = min(self.scroll_offset, max_scroll)

        # Slice lines according to scroll offset
        if self.scroll_offset > 0:
            sliced_lines = rendered_lines[:len(rendered_lines) - self.scroll_offset]
        else:
            sliced_lines = rendered_lines

        # Blit messages bottom-up, stopping strictly below the header divider
        cur_y = self.rect.bottom - line_height - 4
        for prefix, text, prefix_col, text_col in reversed(sliced_lines):
            if cur_y < self.rect.top + self.header_h + 2:
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
            surface.blit(scroll_indicator, (self.rect.right - scroll_indicator.get_width() - 8, self.rect.y + 2))

        # 4. Render Active Input Field
        if self.active:
            inp_surf = pygame.Surface((self.input_rect.w, self.input_rect.h), pygame.SRCALPHA)
            inp_surf.fill((20, 20, 25, 230))
            surface.blit(inp_surf, self.input_rect.topleft)
            pygame.draw.rect(surface, GOLD, self.input_rect, 2, border_radius=6)

            cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
            display_str = self.input_text + cursor
            max_input_w = self.input_rect.w - 16

            while len(display_str) > 0 and self.font.size(display_str)[0] > max_input_w:
                display_str = display_str[1:]

            txt = self.font.render(display_str, True, WHITE)
            surface.blit(txt, (self.input_rect.x + 8, self.input_rect.y + 4))