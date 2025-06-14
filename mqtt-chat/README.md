# MQTT Chat Application

A real-time chat application built using MQTT protocol, demonstrating publish/subscribe messaging patterns for IoT and real-time communication.

## 🌟 Key Features

### Core Functionality
- ⚡ **Real-time messaging** via MQTT publish/subscribe
- 🔐 **Unique client IDs** - Prevents connection conflicts
- 👥 **User presence tracking** - Live online users with heartbeat
- 📜 **Chat history** - Last 50 messages for new joiners
- 🔔 **Join/leave notifications** - Real-time user status updates
- 🌐 **Cloud MQTT broker** - Ready to use with Railway deployment
- 💗 **Heartbeat mechanism** - Automatic timeout for inactive users
- 🎯 **Topic-based routing** - Organized message channels

### MQTT Topics Structure
```
chat/messages      - Public chat messages
chat/presence      - User join/leave/heartbeat
chat/system        - System notifications
chat/users         - Online users list
chat/private/{user} - Private messages to specific users
chat/request/users - Request online users
chat/request/history - Request chat history
```

## 📦 Installation

### Requirements
- Python 3.7+
- MQTT Broker (e.g., Railway EMQX deployment)

### Install Dependencies
```bash
pip install paho-mqtt aioconsole
```

## 🚀 Quick Start

### Using Railway MQTT Broker

1. **Start the Server** (monitors and manages chat):
```bash
python mqtt-chat-server.py
# Or specify custom broker:
python mqtt-chat-server.py broker.example.com 1883
```

2. **Connect Clients**:
```bash
python mqtt-chat-client.py
# Or specify broker directly:
python mqtt-chat-client.py nozomi.proxy.rlwy.net:32067
```

### Default Railway Broker
- **Host**: `nozomi.proxy.rlwy.net`
- **Port**: `32067`

## 🏗️ Architecture

### MQTT vs WebSocket Comparison

| Feature | MQTT Implementation | WebSocket Implementation |
|---------|-------------------|------------------------|
| **Protocol** | MQTT over TCP | WebSocket |
| **Server Role** | Monitor/Manager | Message Router |
| **Message Routing** | Broker-based | Server-based |
| **Scalability** | Excellent (broker handles) | Limited (server bottleneck) |
| **Offline Messages** | Supported (QoS levels) | Not supported |
| **Resource Usage** | Very low | Moderate |
| **Use Case** | IoT, distributed systems | Web applications |

### Message Flow

1. **Client → Broker**: Publishes to topic
2. **Broker → Subscribers**: Distributes to all subscribed clients
3. **Server**: Monitors messages, manages presence, stores history

### Key Differences from WebSocket Version

1. **No Central Server Required**: MQTT broker handles message routing
2. **Topic-Based**: Messages organized by topics instead of direct routing
3. **Quality of Service**: Built-in message delivery guarantees
4. **Lightweight**: Minimal bandwidth usage, ideal for IoT
5. **Retained Messages**: Can store last message per topic

## 📡 MQTT Topics Explained

### Public Topics
- `chat/messages` - All chat messages
- `chat/system` - System-wide notifications
- `chat/presence` - User status updates
- `chat/users` - Current online users list

### Private Topics
- `chat/private/{username}` - Direct messages to specific user
- `chat/request/*` - Request channels for history/users

## 💬 Message Protocol

### Message Types

```json
// Chat Message
{
    "type": "chat",
    "username": "Alice",
    "message": "Hello everyone!",
    "timestamp": "2025-01-14T10:30:00"
}

// Presence Message
{
    "action": "join|leave|heartbeat",
    "username": "Bob",
    "timestamp": "2025-01-14T10:31:00"
}

// System Notification
{
    "type": "user_join|user_leave",
    "username": "Charlie",
    "message": "Charlie joined the chat",
    "online_users": 3,
    "users_list": ["Alice", "Bob", "Charlie"]
}
```

## 🛠️ Advanced Features

### Heartbeat Mechanism
- Clients send heartbeat every 30 seconds
- Server removes inactive users after 60 seconds
- Automatic reconnection on broker disconnect

### Quality of Service (QoS)
- QoS 0: Fire and forget (default)
- QoS 1: At least once delivery
- QoS 2: Exactly once delivery

### Retained Messages
- Last Will and Testament (LWT) for disconnect handling
- Retained user list for new joiners

## 🔧 Configuration

### Environment Variables
```bash
MQTT_BROKER_HOST=nozomi.proxy.rlwy.net
MQTT_BROKER_PORT=32067
MQTT_CLIENT_ID=unique_client_id
```

### Custom Broker Setup
```python
# Local Mosquitto
python mqtt-chat-server.py localhost 1883

# Cloud MQTT
python mqtt-chat-server.py broker.hivemq.com 1883

# Secure MQTT (TLS)
python mqtt-chat-server.py broker.example.com 8883
```

## 🚦 Testing

### Test Connection
```bash
# Test script included
python test_mqtt_connection.py
```

### MQTT Client Tools
- MQTT Explorer (GUI)
- mosquitto_pub/sub (CLI)
- MQTTX (Cross-platform)

## 📊 Performance Considerations

### Advantages
- **Low Bandwidth**: ~2-10 bytes overhead per message
- **Battery Efficient**: Ideal for mobile/IoT devices  
- **Scalable**: Broker handles thousands of connections
- **Reliable**: Built-in reconnection and QoS

### Limitations
- Requires MQTT broker infrastructure
- No built-in encryption (use TLS)
- Topic design crucial for performance

## 🔐 Security Best Practices

1. **Use TLS/SSL** for encrypted connections
2. **Implement authentication** (username/password)
3. **Use ACLs** to restrict topic access
4. **Validate all messages** before processing
5. **Rate limiting** to prevent spam

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check broker address and port |
| Client ID conflict | Ensure unique client IDs |
| Messages not received | Verify topic subscriptions |
| High latency | Check network and broker load |
| Disconnections | Implement reconnection logic |

## 📚 MQTT Resources

- [MQTT.org](https://mqtt.org/) - Official MQTT documentation
- [Eclipse Paho](https://www.eclipse.org/paho/) - MQTT client libraries
- [EMQX Docs](https://www.emqx.io/docs) - EMQX broker documentation
- [HiveMQ](https://www.hivemq.com/mqtt/) - MQTT essentials

## 🎯 Use Cases

This MQTT chat implementation is ideal for:
- IoT device communication
- Mobile chat applications  
- Distributed system messaging
- Real-time notifications
- Low-bandwidth environments
- Scalable chat systems

## 🔄 Migration from WebSocket

To migrate from WebSocket to MQTT:
1. Replace WebSocket connection with MQTT client
2. Map WebSocket events to MQTT topics
3. Update message routing to use topics
4. Implement QoS for reliability
5. Add heartbeat for presence