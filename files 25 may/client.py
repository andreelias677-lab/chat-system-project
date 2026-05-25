import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 5000


def receive_messages(client_socket):
    """Continuously receive messages from the server in a separate thread."""
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                print("\n[DISCONNECTED] Server closed the connection.")
                break
            print(f"\n{message}")
            print("You: ", end='', flush=True)
        except Exception as e:
            print(f"\n[ERROR] Connection lost: {e}")
            break

    client_socket.close()
    sys.exit(0)


def start_client():
    """Connect to the server and start sending/receiving messages."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((HOST, PORT))
        print(f"[CONNECTED] Connected to server at {HOST}:{PORT}")
    except ConnectionRefusedError:
        print(f"[ERROR] Could not connect to server at {HOST}:{PORT}")
        print("[ERROR] Make sure the server is running.")
        sys.exit(1)

    # Step 1: Handle username registration
    try:
        # Receive the username prompt from server
        prompt = client.recv(1024).decode()
        username = input(prompt).strip()
        if not username:
            username = "Anonymous"
        client.send(username.encode())
    except Exception as e:
        print(f"[ERROR] Registration failed: {e}")
        client.close()
        sys.exit(1)

    # Step 2: Start receiving thread
    receive_thread = threading.Thread(
        target=receive_messages,
        args=(client,),
        daemon=True
    )
    receive_thread.start()

    # Step 3: Main sending loop
    print("\n[CHAT] You are now connected! Type your message and press Enter.")
    print("[CHAT] Type '/users' to see online users. Type 'quit' to exit.\n")

    while True:
        try:
            message = input("You: ").strip()

            if not message:
                continue

            client.send(message.encode())

            if message.lower() == 'quit':
                print("[DISCONNECTED] You left the chat.")
                break

        except (KeyboardInterrupt, EOFError):
            print("\n[DISCONNECTED] You left the chat.")
            client.send("quit".encode())
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            break

    client.close()


if __name__ == "__main__":
    start_client()
