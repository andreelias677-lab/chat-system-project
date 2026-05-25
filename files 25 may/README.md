#  Client-Server Chat Application

A real-time multi-user chat system built with **Python TCP Sockets** following the **Client-Server architecture**.  
Supports public messaging, private messages, message history, and an optional modern GUI.

---

##  Project Overview

| Item | Details |
|---|---|
| **Course** | Network Applications Programming |
| **Architecture** | Client-Server |
| **Language** | Python 3 |
| **Protocol** | TCP Sockets |

---

##  Features

| Feature | Status |
|---|---|
| Multi-client support (simultaneous connections) 
| Username registration on login 
| Public broadcasting to all users 
| Private messaging `/msg <user> <text>` 
| View online users `/users` 
| Message history log `/history` 
| Clean logout `quit` 
| Automatic chat log file (`chat_history.log`) 
| Duplicate username rejection 
| Thread-safe multi-client handling 
| Modern GUI client (optional) 

---

##  Project Structure

```
chat-system-project/
│
├── server.py         # Server — manages all clients and routing
├── client.py         # Terminal client — lightweight, no dependencies
├── client_gui.py     # GUI client — modern interface (requires customtkinter)
├── chat_history.log  # Auto-generated message log (created at runtime)
└── README.md         # Documentation
```

---

##  Technologies Used

| Technology | Purpose |
|---|---|
| Python 3 | Core language |
| `socket` | TCP network communication |
| `threading` | Handle multiple clients concurrently |
| `datetime` | Timestamping messages |
| `customtkinter` | Modern GUI (optional client) |
| Git & GitHub | Version control and collaboration |

---

##  How to Run

### Prerequisites
- Python 3.x
- For GUI client only: `pip install customtkinter`

---

### Step 1 — Start the Server
```bash
python server.py
```
Output:
```
[SERVER STARTED] 0.0.0.0:5000
[LOG FILE] /path/to/chat_history.log
```

---

### Step 2 — Connect Clients

**Option A — Terminal Client (no dependencies):**
```bash
python client.py
```

**Option B — GUI Client:**
```bash
python client_gui.py
```
Open as many client windows as you want.

---

### Step 3 — Chat Commands

| Command | Description |
|---|---|
| *(type any text)* | Send public message to all users |
| `/users` | Show currently online users |
| `/msg <username> <message>` | Send a private message |
| `/history` | View last 50 messages from log |
| `quit` | Disconnect cleanly |

---

##  Example Session

**Server:**
```
[SERVER STARTED] 0.0.0.0:5000
[REGISTERED] Alice
[Alice]: Hello everyone!
[REGISTERED] Bob
PM | Bob → Alice: Hey, private message!
[DISCONNECTED] Bob
```

**Alice (terminal):**
```
Enter your username: Alice
[SERVER] Welcome, Alice! Type 'quit' to exit.
[ Online: Alice ]

You: Hello everyone!

[PM from Bob]: Hey, private message!
You: /history
─── Last messages ───
[2026-05-25 10:30:01] Alice joined the chat.
[2026-05-25 10:30:05] [Alice]: Hello everyone!
─────────────────────
```

**Bob (terminal):**
```
Enter your username: Bob
[SERVER] Alice has joined the chat! [ Online: Alice, Bob ]
[Alice]: Hello everyone!
You: /msg Alice Hey, private message!
[PM to Alice]: Hey, private message!
```

---

##  System Architecture

```
           ┌──────────────────────┐
           │       SERVER         │
           │   server.py :5000    │
           │                      │
           │  ┌────────────────┐  │
           │  │ Thread pool    │  │
           │  │ (1/client)     │  │
           │  └────────────────┘  │
           │  ┌────────────────┐  │
           │  │ chat_history   │  │
           │  │    .log        │  │
           │  └────────────────┘  │
           └──────┬───────┬───────┘
                  │       │
         ┌────────┘       └────────┐
         │                         │
  ┌──────▼──────┐           ┌──────▼──────┐
  │  Client A   │           │  Client B   │
  │ (Terminal)  │           │   (GUI)     │
  └─────────────┘           └─────────────┘
```

**Flow:**
1. Client connects → Server spawns dedicated thread
2. Client registers username → Server validates and broadcasts join
3. Client sends message → Server routes to all or specific target
4. All messages logged to `chat_history.log` with timestamps
5. Client sends `quit` → Server cleans up and notifies others

---

##  Use Cases

| Use Case | Description |
|---|---|
| **Login** | Enter username → server validates → join confirmed |
| **Send Public Message** | Text broadcast to all connected users |
| **Send Private Message** | `/msg <user> <text>` — delivered only to target |
| **View Online Users** | `/users` — returns live list |
| **View History** | `/history` — returns last 50 logged messages |
| **Logout** | `quit` — clean disconnect, others notified |

---

##  Team Members

| Member | Role |
|---|---|
| Ibrahim hamodah | Server Development |
| George hanna | Client Development |
| Andreh Elias | Testing + Documentation + GitHub Management |

---

##  Future Improvements

-  Chat rooms / channels
-  File sharing between users
-  Password authentication
-  Database for persistent message storage
-  Web-based interface
-  Desktop notifications

---

## 🔗 Repository

[https://github.com/andreelias677-lab/chat-system-project](https://github.com/andreelias677-lab/chat-system-project)
