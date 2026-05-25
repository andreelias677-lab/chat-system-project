import socket
import threading
import datetime
import os

HOST = '0.0.0.0'
PORT = 5000

# {socket: username}
clients = {}
lock = threading.Lock()

LOG_FILE = "chat_history.log"


# ─── Logging ────────────────────────────────────────────────
def log_message(message):
    """Append a message to the log file with a timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


# ─── Helpers ─────────────────────────────────────────────────
def get_socket_by_username(target_username):
    """Return the socket of a user by their username, or None."""
    with lock:
        for sock, uname in clients.items():
            if uname.lower() == target_username.lower():
                return sock
    return None


def get_online_users():
    with lock:
        users = list(clients.values())
    if users:
        return "[ Online: " + ", ".join(users) + " ]"
    return "[ No users online ]"


def safe_send(sock, message):
    try:
        sock.send(message.encode())
        return True
    except:
        return False


def broadcast(message, sender_socket=None):
    """Send to all clients except sender."""
    with lock:
        targets = [(s, u) for s, u in clients.items() if s != sender_socket]
    for sock, _ in targets:
        if not safe_send(sock, message):
            remove_client(sock)


def remove_client(client_socket):
    with lock:
        if client_socket in clients:
            username = clients.pop(client_socket)
            try:
                client_socket.close()
            except:
                pass
            return username
    return None


# ─── Client handler ──────────────────────────────────────────
def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address}")

    # 1) Username registration
    try:
        safe_send(client_socket, "USERNAME_REQUEST")
        username = client_socket.recv(1024).decode().strip()
        if not username:
            username = f"User_{client_address[1]}"

        # Reject duplicate usernames
        with lock:
            existing = list(clients.values())
        if username in existing:
            safe_send(client_socket, "ERROR: Username already taken. Disconnecting.")
            client_socket.close()
            return

        with lock:
            clients[client_socket] = username

        print(f"[REGISTERED] {username}")
        log_message(f"{username} joined the chat.")

        safe_send(client_socket, f"WELCOME|{username}")
        broadcast(f"[SERVER] {username} has joined the chat! {get_online_users()}", sender_socket=client_socket)
        safe_send(client_socket, get_online_users())

    except Exception as e:
        print(f"[ERROR] Registration: {e}")
        client_socket.close()
        return

    # 2) Message loop
    while True:
        try:
            data = client_socket.recv(2048).decode().strip()
            if not data:
                break

            # ── quit ──────────────────────────────────────────
            if data.lower() == "quit":
                break

            # ── /users ────────────────────────────────────────
            if data.lower() == "/users":
                safe_send(client_socket, get_online_users())
                continue

            # ── /history ──────────────────────────────────────
            if data.lower() == "/history":
                if os.path.exists(LOG_FILE):
                    with open(LOG_FILE, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    last = lines[-50:] if len(lines) > 50 else lines
                    history = "─── Last messages ───\n" + "".join(last) + "─────────────────────"
                else:
                    history = "[SERVER] No history yet."
                safe_send(client_socket, history)
                continue

            # ── /msg <target> <text> ──────────────────────────
            if data.lower().startswith("/msg "):
                parts = data.split(" ", 2)
                if len(parts) < 3:
                    safe_send(client_socket, "[SERVER] Usage: /msg <username> <message>")
                    continue
                target_name = parts[1]
                private_text = parts[2]
                target_sock = get_socket_by_username(target_name)
                if target_sock is None:
                    safe_send(client_socket, f"[SERVER] User '{target_name}' not found or offline.")
                    continue
                pm = f"[PM from {username}]: {private_text}"
                safe_send(target_sock, pm)
                safe_send(client_socket, f"[PM to {target_name}]: {private_text}")
                log_message(f"PM | {username} → {target_name}: {private_text}")
                continue

            # ── broadcast ─────────────────────────────────────
            full_msg = f"[{username}]: {data}"
            print(full_msg)
            log_message(full_msg)
            broadcast(full_msg, sender_socket=client_socket)

        except Exception as e:
            print(f"[ERROR] {username}: {e}")
            break

    # 3) Disconnect
    uname = remove_client(client_socket)
    if uname:
        print(f"[DISCONNECTED] {uname}")
        log_message(f"{uname} left the chat.")
        broadcast(f"[SERVER] {uname} has left the chat. {get_online_users()}")


# ─── Start ───────────────────────────────────────────────────
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[SERVER STARTED] {HOST}:{PORT}")
    print(f"[LOG FILE] {os.path.abspath(LOG_FILE)}\n")

    while True:
        try:
            client_socket, client_address = server.accept()
            t = threading.Thread(target=handle_client,
                                 args=(client_socket, client_address),
                                 daemon=True)
            t.start()
        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down.")
            break

    server.close()


if __name__ == "__main__":
    start_server()
