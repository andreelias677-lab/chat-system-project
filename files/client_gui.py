import socket
import threading
import datetime
import sys

try:
    import customtkinter as ctk
except ImportError:
    print("Please install customtkinter: pip install customtkinter")
    sys.exit(1)

HOST = '127.0.0.1'
PORT = 5000

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("💬 Chat App")
        self.geometry("900x600")
        self.minsize(700, 500)
        self.resizable(True, True)

        self.client_socket = None
        self.username = ""
        self.connected = False

        self._build_login_screen()

    # ─── Login Screen ─────────────────────────────────────────
    def _build_login_screen(self):
        self.login_frame = ctk.CTkFrame(self, corner_radius=20)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.login_frame, text="💬 Chat Application",
                     font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(30, 5))
        ctk.CTkLabel(self.login_frame, text="Client-Server Architecture | Python Sockets",
                     font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 25))

        ctk.CTkLabel(self.login_frame, text="Server Host", anchor="w").pack(padx=40, fill="x")
        self.host_entry = ctk.CTkEntry(self.login_frame, width=320, placeholder_text="127.0.0.1")
        self.host_entry.pack(padx=40, pady=(4, 12))
        self.host_entry.insert(0, HOST)

        ctk.CTkLabel(self.login_frame, text="Port", anchor="w").pack(padx=40, fill="x")
        self.port_entry = ctk.CTkEntry(self.login_frame, width=320, placeholder_text="5000")
        self.port_entry.pack(padx=40, pady=(4, 12))
        self.port_entry.insert(0, str(PORT))

        ctk.CTkLabel(self.login_frame, text="Username", anchor="w").pack(padx=40, fill="x")
        self.username_entry = ctk.CTkEntry(self.login_frame, width=320, placeholder_text="Enter your username")
        self.username_entry.pack(padx=40, pady=(4, 20))
        self.username_entry.bind("<Return>", lambda e: self._do_connect())

        self.connect_btn = ctk.CTkButton(self.login_frame, text="Connect",
                                         width=320, height=40,
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         command=self._do_connect)
        self.connect_btn.pack(padx=40, pady=(0, 30))

        self.status_label = ctk.CTkLabel(self.login_frame, text="",
                                          text_color="#e74c3c",
                                          font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=(0, 15))

    # ─── Connect ──────────────────────────────────────────────
    def _do_connect(self):
        host = self.host_entry.get().strip()
        port_str = self.port_entry.get().strip()
        username = self.username_entry.get().strip()

        if not host or not port_str or not username:
            self.status_label.configure(text="Please fill all fields.")
            return

        try:
            port = int(port_str)
        except ValueError:
            self.status_label.configure(text="Port must be a number.")
            return

        self.connect_btn.configure(state="disabled", text="Connecting...")
        self.status_label.configure(text="", text_color="#e74c3c")

        threading.Thread(target=self._connect_thread,
                         args=(host, port, username), daemon=True).start()

    def _connect_thread(self, host, port, username):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))

            # Wait for USERNAME_REQUEST
            prompt = sock.recv(1024).decode()
            if "USERNAME_REQUEST" not in prompt:
                raise Exception("Unexpected server response.")

            sock.send(username.encode())

            # Wait for WELCOME or ERROR
            response = sock.recv(1024).decode()
            if response.startswith("ERROR"):
                raise Exception(response.replace("ERROR: ", ""))

            if response.startswith("WELCOME|"):
                self.username = response.split("|", 1)[1]

            self.client_socket = sock
            self.connected = True
            self.after(0, self._show_chat_screen)
            threading.Thread(target=self._receive_loop, daemon=True).start()

        except Exception as e:
            self.after(0, lambda: self._login_error(str(e)))

    def _login_error(self, msg):
        self.status_label.configure(text=f"❌ {msg}")
        self.connect_btn.configure(state="normal", text="Connect")

    # ─── Chat Screen ──────────────────────────────────────────
    def _show_chat_screen(self):
        self.login_frame.destroy()
        self.title(f"💬 Chat App — {self.username}")
        self._build_chat_screen()

    def _build_chat_screen(self):
        # ── Top bar ───────────────────────────────────────────
        top = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color=("#1a1a2e", "#1a1a2e"))
        top.pack(fill="x", side="top")
        top.pack_propagate(False)

        ctk.CTkLabel(top, text="💬 Chat Application",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="white").pack(side="left", padx=20, pady=10)

        self.conn_indicator = ctk.CTkLabel(top, text="● Connected",
                                            text_color="#2ecc71",
                                            font=ctk.CTkFont(size=12))
        self.conn_indicator.pack(side="right", padx=20)

        ctk.CTkLabel(top, text=f"👤 {self.username}",
                     text_color="#95a5a6",
                     font=ctk.CTkFont(size=12)).pack(side="right", padx=10)

        # ── Main layout ───────────────────────────────────────
        main = ctk.CTkFrame(self, corner_radius=0)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=0)
        main.rowconfigure(0, weight=1)

        # ── Chat area (left) ──────────────────────────────────
        chat_frame = ctk.CTkFrame(main, corner_radius=0)
        chat_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        chat_frame.rowconfigure(0, weight=1)
        chat_frame.rowconfigure(1, weight=0)
        chat_frame.columnconfigure(0, weight=1)

        self.chat_box = ctk.CTkTextbox(chat_frame, state="disabled",
                                        font=ctk.CTkFont(size=13),
                                        wrap="word", corner_radius=10)
        self.chat_box.grid(row=0, column=0, sticky="nsew", padx=5, pady=(5, 5))

        # configure text tags (colors per message type)
        self.chat_box._textbox.tag_config("server",   foreground="#f39c12")
        self.chat_box._textbox.tag_config("private",  foreground="#9b59b6")
        self.chat_box._textbox.tag_config("self_msg", foreground="#2ecc71")
        self.chat_box._textbox.tag_config("other",    foreground="#ecf0f1")
        self.chat_box._textbox.tag_config("time",     foreground="#7f8c8d")
        self.chat_box._textbox.tag_config("info",     foreground="#3498db")

        # Input row
        input_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
        input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        input_frame.columnconfigure(0, weight=1)

        self.msg_entry = ctk.CTkEntry(input_frame, placeholder_text="Type a message…",
                                       font=ctk.CTkFont(size=13), height=40, corner_radius=10)
        self.msg_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.msg_entry.bind("<Return>", lambda e: self._send_message())

        ctk.CTkButton(input_frame, text="Send", width=80, height=40,
                       corner_radius=10,
                       command=self._send_message).grid(row=0, column=1)

        # ── Sidebar (right) ───────────────────────────────────
        sidebar = ctk.CTkFrame(main, width=200, corner_radius=10)
        sidebar.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="👥 Online Users",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 8))

        self.users_box = ctk.CTkTextbox(sidebar, state="disabled",
                                         font=ctk.CTkFont(size=12),
                                         corner_radius=8, height=200)
        self.users_box.pack(fill="x", padx=10)

        ctk.CTkLabel(sidebar, text="Commands",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(20, 6))

        cmds = [
            ("/users",         "Refresh user list"),
            ("/history",       "Show last messages"),
            ("/msg user text", "Private message"),
        ]
        for cmd, desc in cmds:
            f = ctk.CTkFrame(sidebar, fg_color="transparent")
            f.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(f, text=cmd, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="#3498db").pack(anchor="w")
            ctk.CTkLabel(f, text=desc, font=ctk.CTkFont(size=10),
                         text_color="gray").pack(anchor="w")

        ctk.CTkButton(sidebar, text="Disconnect", fg_color="#e74c3c",
                       hover_color="#c0392b", height=36,
                       command=self._disconnect).pack(side="bottom", padx=10, pady=15, fill="x")

        self._append_chat("[SERVER] Connected successfully! Welcome to the chat.", "server")

    # ─── Chat helpers ─────────────────────────────────────────
    def _append_chat(self, message, tag="other"):
        self.chat_box.configure(state="normal")
        time_str = datetime.datetime.now().strftime("%H:%M")
        self.chat_box._textbox.insert("end", f"[{time_str}] ", "time")
        self.chat_box._textbox.insert("end", message + "\n", tag)
        self.chat_box.configure(state="disabled")
        self.chat_box._textbox.see("end")

    def _update_users_box(self, text):
        self.users_box.configure(state="normal")
        self.users_box.delete("1.0", "end")
        names = text.replace("[ Online:", "").replace("]", "").strip()
        for name in names.split(","):
            name = name.strip()
            if name:
                marker = "▶ " if name == self.username else "• "
                self.users_box.insert("end", f"{marker}{name}\n")
        self.users_box.configure(state="disabled")

    # ─── Send ─────────────────────────────────────────────────
    def _send_message(self):
        if not self.connected or not self.client_socket:
            return
        msg = self.msg_entry.get().strip()
        if not msg:
            return
        self.msg_entry.delete(0, "end")

        try:
            self.client_socket.send(msg.encode())
        except:
            self._append_chat("[ERROR] Failed to send message.", "server")
            return

        # Show sent message locally
        if msg.lower().startswith("/msg "):
            parts = msg.split(" ", 2)
            if len(parts) == 3:
                self._append_chat(f"[PM to {parts[1]}]: {parts[2]}", "private")
        elif msg.lower() in ("/users", "/history"):
            pass  # server will reply
        elif msg.lower() == "quit":
            self._disconnect()
        else:
            self._append_chat(f"[You]: {msg}", "self_msg")

    # ─── Receive loop ─────────────────────────────────────────
    def _receive_loop(self):
        while self.connected:
            try:
                data = self.client_socket.recv(4096).decode()
                if not data:
                    break
                self.after(0, lambda d=data: self._handle_incoming(d))
            except:
                break
        self.after(0, self._on_disconnect)

    def _handle_incoming(self, message):
        # Online users list
        if message.startswith("[ Online:") or message == "[ No users online ]":
            self._update_users_box(message)
            return

        # Server notices
        if message.startswith("[SERVER]"):
            self._append_chat(message, "server")
            # If it contains the user list inline, also update sidebar
            if "[ Online:" in message:
                start = message.index("[ Online:")
                self._update_users_box(message[start:])
            return

        # Private messages
        if message.startswith("[PM"):
            self._append_chat(message, "private")
            return

        # History block
        if "Last messages" in message or "─────" in message:
            self._append_chat(message, "info")
            return

        # Errors
        if message.startswith("[ERROR]") or message.startswith("ERROR"):
            self._append_chat(message, "server")
            return

        # Regular message from another user
        self._append_chat(message, "other")

    # ─── Disconnect ───────────────────────────────────────────
    def _disconnect(self):
        self.connected = False
        if self.client_socket:
            try:
                self.client_socket.send("quit".encode())
                self.client_socket.close()
            except:
                pass
        self.destroy()

    def _on_disconnect(self):
        self.connected = False
        if hasattr(self, 'conn_indicator'):
            self.conn_indicator.configure(text="● Disconnected", text_color="#e74c3c")
        self._append_chat("[SERVER] You have been disconnected.", "server")


if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()
