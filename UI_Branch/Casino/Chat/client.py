import socket
import threading
import json
from collections import deque

class ChatClient:
    def __init__(self, host="127.0.0.1", port=9001):
        self.host = host
        self.port = port
        self.sock = None
        self.running = False
        self.messages = deque(maxlen=25)  # Keeps latest 25 messages
        self.connected = False

    def connect(self, username):
        self.username = username
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.running = True
            self.connected = True

            # Register username
            self._send({"type": "join", "username": username})

            # Start listener daemon thread
            t = threading.Thread(target=self._listen, daemon=True)
            t.start()
            return True
        except ConnectionRefusedError:
            self.connected = False
            return False

    def _listen(self):
        try:
            sock_file = self.sock.makefile("r", encoding="utf-8")
            for line in sock_file:
                if not line.strip():
                    continue
                data = json.loads(line)
                self.messages.append(data)
        except Exception:
            pass
        finally:
            self.connected = False

    def _send(self, payload):
        if not self.connected or not self.sock:
            return
        try:
            raw = (json.dumps(payload) + "\n").encode("utf-8")
            self.sock.sendall(raw)
        except Exception:
            self.connected = False

    def send_chat(self, text):
        if text.strip():
            self._send({"type": "chat", "text": text.strip()})

    def send_announcement(self, text):
        """Emitted when landing a big win or entering bonus features."""
        self._send({"type": "announcement", "text": text})

    def disconnect(self):
        """Disconnects the socket, stops listening, and clears chat history."""
        self.running = False
        self.connected = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None
        self.messages.clear()


    def close(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass