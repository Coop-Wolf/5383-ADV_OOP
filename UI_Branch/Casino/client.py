import socket
import threading
import json
from collections import deque

DISCOVERY_PORT = 9002

class ChatClient:
    def __init__(self, host="127.0.0.1", port=9001):
        self.host = host
        self.port = port
        self.sock = None
        self.running = False
        self.messages = deque(maxlen=25)
        self.connected = False

    def _discover_server(self, timeout=2.0):
        """Listens on UDP for the server's broadcast beacon."""
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_sock.settimeout(timeout)
        try:
            udp_sock.bind(("", DISCOVERY_PORT))
            data, addr = udp_sock.recvfrom(1024)
            message = data.decode("utf-8")
            if message.startswith("CASINO_BEACON:"):
                discovered_ip = addr[0]
                discovered_port = int(message.split(":")[1])
                return discovered_ip, discovered_port
        except Exception:
            pass
        finally:
            udp_sock.close()
        return None, None

    def connect(self, username):
        self.username = username
        
        # 1. Attempt LAN auto-discovery
        disc_ip, disc_port = self._discover_server(timeout=2.0)
        target_host = disc_ip if disc_ip else self.host
        target_port = disc_port if disc_port else self.port

        # 2. Connect over TCP
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(3.0)  # Prevent indefinite hang if host is unreachable
            self.sock.connect((target_host, target_port))
            self.sock.settimeout(None)  # Restore blocking mode for regular stream reads

            self.running = True
            self.connected = True

            # Register username
            self._send({"type": "join", "username": username})

            # Start listener daemon thread
            t = threading.Thread(target=self._listen, daemon=True)
            t.start()
            return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            self.connected = False
            if self.sock:
                try:
                    self.sock.close()
                except Exception:
                    pass
                self.sock = None
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
        self.disconnect()