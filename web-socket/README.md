# WebSocket Chat Application

A comprehensive real-time chat application demonstrating WebSocket technology with Python server and multiple client implementations.

## 🌟 Key Features

### Core Functionality

- ⚡ **Real-time bidirectional communication** - Instant message delivery
- 🔐 **Unique username validation** - Prevents duplicate usernames in the same session
- 👥 **Live online users tracking** - See who's online in real-time
- 📜 **Persistent chat history** - Stores last 50 messages for new joiners
- 🔔 **Join/leave notifications** - Alerts when users enter or exit
- 🌐 **Network-wide accessibility** - Chat across LAN/WAN networks
- 🔄 **Auto-reconnection** - Automatically reconnects on connection loss
- 💻 **Multi-platform clients** - Terminal and web-based interfaces

### Advanced Features

- 📡 **Custom server IP configuration** - Connect to any server address
- 🎨 **Modern UI/UX** - Clean, responsive web interface
- 🔍 **Command system** - Built-in commands for terminal client
- 📊 **User presence** - Real-time online user count and list
- 🚀 **Asynchronous I/O** - High-performance message handling
- 📝 **JSON protocol** - Structured message format

## 📦 Installation

### Requirements

- Python 3.7+
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install websockets aioconsole
```

## 🚀 Quick Start

### 1. Start the Server

```bash
python chat-server.py
```

The server will display:

```
Starting WebSocket chat server on ws://0.0.0.0:8765
==================================================
Server is accessible at:
  📡 ws://localhost:8765 (local only)
  📡 ws://192.168.1.100:8765 (network)
==================================================
Share the network address with other users to connect!
```

### 2. Connect Clients

#### Option A: Python Terminal Client

**Interactive mode** (prompts for server):

```bash
python chat-client.py

# Output:
# 🎉 Welcome to WebSocket Chat!
# ========================================
#
# 📡 Server Connection
# Enter server address (default: localhost:8765): 192.168.1.100:8765
#
# Enter your username: Alice
```

**Direct connection** (specify server):

```bash
python chat-client.py 192.168.1.100:8765
# or
python chat-client.py ws://192.168.1.100:8765
```

#### Option B: Web Browser Client

1. Open `chat-web-client.html` in your browser
2. Enter the server address (e.g., `192.168.1.100:8765`)
3. Enter your username and click "Join Chat"

### 3. Available Commands

#### Terminal Client Commands:

| Command  | Description               |
| -------- | ------------------------- |
| `/help`  | Show available commands   |
| `/users` | Display online users list |
| `/quit`  | Exit the chat             |
| `Enter`  | Send message              |

#### Web Client Features:

- Click on the online users count to see who's online
- Auto-reconnect on connection loss
- Responsive design for mobile devices

## 📁 Project Structure

```
web-socket/
├── chat-server.py           # WebSocket server with multi-client support
├── chat-client.py           # Terminal client with async I/O
├── chat-web-client.html     # Web client with modern UI
├── websocket-demo.html      # Simple WebSocket echo demo
├── huong-dan-websocket.md   # Vietnamese WebSocket guide
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Server Features

- Binds to all network interfaces (0.0.0.0) for network accessibility
- Automatically detects and displays local IP address
- Validates unique usernames per session
- Broadcasts messages to all connected clients
- Maintains chat history (last 50 messages)
- Sends history to new users
- Handles user join/leave events with online users list
- JSON message protocol
- Error handling and logging

## Client Features

### Terminal Client

- Interactive server connection prompt
- Command-line server specification support
- Colored output with emojis
- Async input/output handling
- Command support (/help, /quit, /users)
- Auto-reconnect on connection loss
- Username validation with retry
- Online users display

### Web Client

- Custom server address input
- Modern responsive UI
- Real-time status updates
- Message bubbles with timestamps
- Clickable online users count with dropdown
- Auto-reconnect functionality
- Mobile-friendly design
- Username validation with feedback

## 📨 Message Protocol

The application uses JSON for all WebSocket communications:

### Message Types

| Type                | Description                    | Direction       |
| ------------------- | ------------------------------ | --------------- |
| `set_username`      | Request username validation    | Client → Server |
| `username_accepted` | Username validation successful | Server → Client |
| `username_error`    | Username validation failed     | Server → Client |
| `chat`              | Regular chat message           | Bidirectional   |
| `system`            | System notification            | Server → Client |
| `user_join`         | User joined notification       | Server → All    |
| `user_leave`        | User left notification         | Server → All    |
| `online_users`      | List of online users           | Server → Client |
| `get_users`         | Request online users list      | Client → Server |
| `history`           | Chat history for new users     | Server → Client |

### Message Format

```json
{
  "type": "message_type",
  "message": "message content",
  "username": "sender username",
  "timestamp": "ISO 8601 format",
  "client_id": "unique identifier",
  "users": ["array of usernames"],
  "users_list": ["current online users"],
  "count": 5,
  "online_users": 5
}
```

### Example Messages

**Chat Message:**

```json
{
  "type": "chat",
  "message": "Hello everyone!",
  "username": "Alice",
  "timestamp": "2024-01-14T10:30:00",
  "client_id": "user_12345"
}
```

**User Join:**

```json
{
  "type": "user_join",
  "message": "Bob joined the chat",
  "timestamp": "2024-01-14T10:31:00",
  "online_users": 3,
  "users_list": ["Alice", "Bob", "Charlie"]
}
```

## 🔧 Development & Extension Ideas

### Current Architecture

- **Server**: Asynchronous Python using `websockets` library
- **Protocol**: JSON-based message passing
- **Clients**: Python terminal (async) and JavaScript web

### Potential Enhancements

#### 🎯 Features

1. **Private Messaging** - Direct messages between users
2. **Chat Rooms** - Multiple topic-based rooms
3. **File Sharing** - Share images and documents
4. **Voice/Video** - WebRTC integration
5. **Message Reactions** - Emoji reactions to messages
6. **Typing Indicators** - Show when someone is typing
7. **Read Receipts** - Message delivery confirmation
8. **User Profiles** - Avatars and status messages

#### 🔐 Security

1. **Authentication** - User login system
2. **Message Encryption** - End-to-end encryption
3. **Rate Limiting** - Prevent spam
4. **Input Validation** - Sanitize all user input
5. **WSS Support** - Secure WebSocket connections

#### 🚀 Performance

1. **Redis Integration** - For scalability
2. **Load Balancing** - Multiple server instances
3. **Message Queuing** - Handle offline messages
4. **Database Storage** - Persistent message history

## 🌐 Network Setup

### Local Network (LAN)

1. **Start the server** - It will automatically detect and display your local IP
2. **Share the IP address** - Give the network address to other users
3. **Connect clients** - Use `YOUR_IP:8765` format

### Internet Access (WAN)

1. **Port Forwarding** - Configure router to forward port 8765
2. **Dynamic DNS** - Use a service like No-IP for stable addresses
3. **Firewall Rules** - Allow incoming connections

### Firewall Configuration

#### Windows

```powershell
# PowerShell (Admin)
New-NetFirewallRule -DisplayName "WebSocket Chat" -Direction Inbound -Protocol TCP -LocalPort 8765 -Action Allow
```

#### Linux

```bash
# UFW
sudo ufw allow 8765/tcp

# iptables
sudo iptables -A INPUT -p tcp --dport 8765 -j ACCEPT
```

#### macOS

```bash
# Using pfctl
echo "pass in proto tcp from any to any port 8765" | sudo pfctl -ef -
```

## 🔍 Troubleshooting

### Common Issues

| Problem                             | Solution                                                                                      |
| ----------------------------------- | --------------------------------------------------------------------------------------------- |
| **Connection refused**              | • Check server is running<br>• Verify IP address<br>• Check port 8765 is free                 |
| **Username taken**                  | • Choose a different username<br>• Wait for user to disconnect                                |
| **Can't see messages**              | • Check firewall settings<br>• Verify WebSocket connection<br>• Check browser console         |
| **Can't connect from other device** | • Ensure server binds to `0.0.0.0`<br>• Check network connectivity<br>• Verify firewall rules |
| **Auto-reconnect not working**      | • Check if server is still running<br>• Verify network connection<br>• Refresh the page       |

### Debug Mode

Run server with debug logging:

```python
# Add to chat-server.py
logging.basicConfig(level=logging.DEBUG)
```

Check WebSocket connection in browser:

```javascript
// Browser console
ws.readyState; // Should be 1 (OPEN)
```

## 📚 Resources

- **WebSocket Protocol**: [RFC 6455](https://tools.ietf.org/html/rfc6455)
- **Python websockets**: [Documentation](https://websockets.readthedocs.io/)
- **MDN WebSocket API**: [Web Docs](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- **Tutorial**: See `huong-dan-websocket.md` (Vietnamese)

## 📄 License

This project is open source and available for educational purposes.
