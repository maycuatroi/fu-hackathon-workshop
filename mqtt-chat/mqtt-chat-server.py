#!/usr/bin/env python3
"""
MQTT Chat Server
Manages chat functionality using MQTT broker
"""

import asyncio
import json
import datetime
import paho.mqtt.client as mqtt
import sys
import signal
import socket
from collections import defaultdict

class MQTTChatServer:
    def __init__(self, broker_host, broker_port):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="chat_server", clean_session=True)
        self.connected_users = {}  # username: last_seen
        self.chat_history = []
        self.MAX_HISTORY = 50
        self.running = True
        self.is_connected = False
        self.reconnect_delay = 5  # seconds
        
        # MQTT Topics
        self.TOPIC_CHAT = "chat/messages"
        self.TOPIC_PRESENCE = "chat/presence"
        self.TOPIC_USERS = "chat/users"
        self.TOPIC_HISTORY = "chat/history"
        self.TOPIC_SYSTEM = "chat/system"
        self.TOPIC_PRIVATE = "chat/private/+"  # chat/private/{username}
        
        # Setup MQTT callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"✅ Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.is_connected = True
            # Subscribe to all necessary topics
            topics = [
                (self.TOPIC_CHAT, 0),
                (self.TOPIC_PRESENCE, 0),
                (self.TOPIC_USERS, 0),
                (self.TOPIC_HISTORY, 0),
                ("chat/private/+", 0),
                ("chat/request/+", 0)
            ]
            for topic, qos in topics:
                client.subscribe(topic, qos)
                print(f"   Subscribed to: {topic}")
        else:
            print(f"❌ Failed to connect to MQTT broker (Code: {rc})")
            self.is_connected = False
            
    def on_disconnect(self, client, userdata, rc):
        self.is_connected = False
        print(f"Disconnected from broker (Code: {rc})")
        if rc != 0:
            print("Unexpected disconnection. Will attempt to reconnect...")
            asyncio.create_task(self.reconnect())
            
    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            # Handle presence messages
            if topic == self.TOPIC_PRESENCE:
                self.handle_presence(payload)
                
            # Handle chat messages
            elif topic == self.TOPIC_CHAT:
                self.handle_chat_message(payload)
                
            # Handle user list requests
            elif topic == "chat/request/users":
                self.send_user_list(payload.get("requester"))
                
            # Handle history requests
            elif topic == "chat/request/history":
                self.send_history(payload.get("requester"))
                
        except json.JSONDecodeError:
            print(f"Invalid JSON received on topic {topic}")
        except Exception as e:
            print(f"Error handling message: {e}")
            
    def handle_presence(self, payload):
        """Handle user join/leave messages"""
        action = payload.get("action")
        username = payload.get("username")
        timestamp = datetime.datetime.now().isoformat()
        
        if action == "join":
            if username not in self.connected_users:
                self.connected_users[username] = timestamp
                
                # Broadcast user joined message
                join_msg = {
                    "type": "user_join",
                    "username": username,
                    "message": f"{username} joined the chat",
                    "timestamp": timestamp,
                    "online_users": len(self.connected_users),
                    "users_list": list(self.connected_users.keys())
                }
                self.client.publish(self.TOPIC_SYSTEM, json.dumps(join_msg))
                print(f"➕ {username} joined (Online: {len(self.connected_users)})")
                
        elif action == "leave":
            if username in self.connected_users:
                del self.connected_users[username]
                
                # Broadcast user left message
                leave_msg = {
                    "type": "user_leave",
                    "username": username,
                    "message": f"{username} left the chat",
                    "timestamp": timestamp,
                    "online_users": len(self.connected_users),
                    "users_list": list(self.connected_users.keys())
                }
                self.client.publish(self.TOPIC_SYSTEM, json.dumps(leave_msg))
                print(f"➖ {username} left (Online: {len(self.connected_users)})")
                
        elif action == "heartbeat":
            # Update last seen time
            self.connected_users[username] = timestamp
            
    def handle_chat_message(self, payload):
        """Store chat message in history"""
        try:
            # Add to history
            self.chat_history.append(payload)
            if len(self.chat_history) > self.MAX_HISTORY:
                self.chat_history.pop(0)
                
            # Log the message
            username = payload.get("username", "Unknown")
            message = payload.get("message", "")
            print(f"💬 {username}: {message}")
        except Exception as e:
            print(f"❌ Error handling chat message: {e}")
        
    def send_user_list(self, requester=None):
        """Send current user list"""
        try:
            users_msg = {
                "type": "online_users",
                "users": list(self.connected_users.keys()),
                "count": len(self.connected_users),
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            if requester:
                # Send to specific user
                self.client.publish(f"chat/private/{requester}", json.dumps(users_msg))
            else:
                # Broadcast to all
                self.client.publish(self.TOPIC_USERS, json.dumps(users_msg))
        except Exception as e:
            print(f"❌ Error sending user list: {e}")
            
    def send_history(self, requester):
        """Send chat history to a specific user"""
        if requester and self.chat_history:
            history_msg = {
                "type": "history",
                "messages": self.chat_history[-20:],  # Last 20 messages
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.client.publish(f"chat/private/{requester}", json.dumps(history_msg))
            
    async def reconnect(self):
        """Attempt to reconnect to MQTT broker"""
        while not self.is_connected and self.running:
            try:
                print(f"🔄 Attempting to reconnect to {self.broker_host}:{self.broker_port}...")
                self.client.reconnect()
                await asyncio.sleep(2)  # Give time for connection
                if self.is_connected:
                    print("✅ Reconnected successfully!")
                    break
            except Exception as e:
                print(f"❌ Reconnection failed: {e}")
                print(f"⏳ Waiting {self.reconnect_delay} seconds before retry...")
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay = min(self.reconnect_delay * 2, 60)  # Exponential backoff
    
    def cleanup_inactive_users(self):
        """Remove users who haven't sent heartbeat in 60 seconds"""
        current_time = datetime.datetime.now()
        inactive_users = []
        
        for username, last_seen_str in self.connected_users.items():
            last_seen = datetime.datetime.fromisoformat(last_seen_str)
            if (current_time - last_seen).total_seconds() > 60:
                inactive_users.append(username)
                
        for username in inactive_users:
            del self.connected_users[username]
            leave_msg = {
                "type": "user_timeout",
                "username": username,
                "message": f"{username} timed out",
                "timestamp": current_time.isoformat(),
                "online_users": len(self.connected_users),
                "users_list": list(self.connected_users.keys())
            }
            self.client.publish(self.TOPIC_SYSTEM, json.dumps(leave_msg))
            print(f"⏱️  {username} timed out")
            
    async def periodic_cleanup(self):
        """Run cleanup every 30 seconds"""
        while self.running:
            await asyncio.sleep(30)
            try:
                if self.is_connected:
                    self.cleanup_inactive_users()
                else:
                    print("⚠️  Skipping cleanup - not connected to broker")
            except Exception as e:
                print(f"❌ Error during cleanup: {e}")
            
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n👋 Shutting down server...")
        self.running = False
        self.client.disconnect()
        sys.exit(0)
        
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"
            
    async def run(self):
        """Run the MQTT chat server"""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🚀 MQTT Chat Server")
        print("=" * 50)
        print(f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
        
        # Configure MQTT client settings
        self.client.reconnect_delay_set(min_delay=1, max_delay=120)
        
        # Connect to MQTT broker
        try:
            self.client.connect(self.broker_host, self.broker_port, keepalive=30)
            self.client.loop_start()
            
            # Wait for connection with timeout
            max_wait = 10
            waited = 0
            while not self.is_connected and waited < max_wait:
                await asyncio.sleep(1)
                waited += 1
            
            if self.is_connected:
                print("\n📡 Server Information:")
                print(f"  MQTT Broker: {self.broker_host}:{self.broker_port}")
                print(f"  Local IP: {self.get_local_ip()}")
                print(f"  Keepalive: 30 seconds")
                print(f"  Auto-reconnect: Enabled")
                print("\n📝 Topics:")
                print(f"  Chat: {self.TOPIC_CHAT}")
                print(f"  Presence: {self.TOPIC_PRESENCE}")
                print(f"  System: {self.TOPIC_SYSTEM}")
                print("\n✅ Server is ready and monitoring chat!")
                print("-" * 50)
            else:
                print("⚠️  Warning: Not fully connected to broker, but server will keep trying...")
            
            # Start periodic cleanup
            await self.periodic_cleanup()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.client.loop_stop()
            
async def main():
    """Main entry point"""
    # Default to Railway broker or allow custom broker
    if len(sys.argv) > 2:
        broker_host = sys.argv[1]
        broker_port = int(sys.argv[2])
    else:
        # Use Railway broker as default
        broker_host = "nozomi.proxy.rlwy.net"
        broker_port = 32067
        
    server = MQTTChatServer(broker_host, broker_port)
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped")