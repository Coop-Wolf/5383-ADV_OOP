import socket
import threading
import json

HOST = "0.0.0.0"
PORT = 9001

clients = {}  # socket -> username
clients_lock = threading.Lock()

def broadcast(payload, exclude_sock=None):
    raw_data = (json.dumps(payload) + "\n").encode("utf-8")
    with clients_lock:
        dead_clients = []
        for client_sock in clients:
            if client_sock != exclude_sock:
                try:
                    client_sock.sendall(raw_data)
                except (OSError, BrokenPipeError):
                    dead_clients.append(client_sock)
        for dead in dead_clients:
            del clients[dead]

def handle_client(sock, addr):
    username = "Guest"
    try:
        sock_file = sock.makefile("r", encoding="utf-8")
        for line in sock_file:
            if not line.strip():
                continue
            data = json.loads(line)
            msg_type = data.get("type")

            if msg_type == "join":
                username = data.get("username", "Guest")
                with clients_lock:
                    clients[sock] = username
                broadcast({"type": "system", "text": f"{username} entered the casino."})

            elif msg_type == "chat":
                text = data.get("text", "").strip()
                if text:
                    broadcast({"type": "chat", "sender": username, "text": text[:120]})

            elif msg_type == "announcement":
                # System broadcast for big wins or bonus rounds
                broadcast({"type": "announcement", "text": data.get("text", "")})

    except Exception:
        pass
    finally:
        with clients_lock:
            if sock in clients:
                del clients[sock]
        broadcast({"type": "system", "text": f"{username} left the casino."})
        sock.close()

def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(15)
    print(f"Casino Chat Server listening on {HOST}:{PORT}")

    while True:
        client_sock, addr = server.accept()
        t = threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True)
        t.start()

if __name__ == "__main__":
    run_server()