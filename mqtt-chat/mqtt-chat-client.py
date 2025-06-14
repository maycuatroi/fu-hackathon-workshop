#!/usr/bin/env python3
"""
MQTT Chat Client
Connects to MQTT broker for real-time chat
"""

import asyncio
import paho.mqtt.client as mqtt
import json
import aioconsole
from datetime import datetime
import sys
import threading
import time

class MQTTChatClient:
    def __init__(self, broker_host=None, broker_port=None):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = None
        self.username = None
        self.running = True
        self.connected = False
        self.online_users = []
        
        # MQTT Topics
        self.TOPIC_CHAT = "chat/messages"
        self.TOPIC_PRESENCE = "chat/presence"
        self.TOPIC_USERS = "chat/users"
        self.TOPIC_HISTORY = "chat/history"
        self.TOPIC_SYSTEM = "chat/system"
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"✅ Connected to MQTT broker")
            self.connected = True
            
            # Subscribe to necessary topics
            topics = [
                (self.TOPIC_CHAT, 0),
                (self.TOPIC_SYSTEM, 0),
                (self.TOPIC_USERS, 0),
                (f"chat/private/{self.username}", 0)
            ]
            
            for topic, qos in topics:
                client.subscribe(topic, qos)
            
            # Send join message
            join_msg = {
                "action": "join",
                "username": self.username,
                "timestamp": datetime.now().isoformat()
            }
            client.publish(self.TOPIC_PRESENCE, json.dumps(join_msg))
            
            # Request history
            history_request = {
                "requester": self.username,
                "timestamp": datetime.now().isoformat()
            }
            client.publish("chat/request/history", json.dumps(history_request))
            
            # Request user list
            users_request = {
                "requester": self.username,
                "timestamp": datetime.now().isoformat()
            }
            client.publish("chat/request/users", json.dumps(users_request))
            
        else:
            print(f"❌ Failed to connect (Code: {rc})")
            self.connected = False
            
    def on_disconnect(self, client, userdata, rc):
        print(f"❌ Disconnected from broker")
        self.connected = False
        
    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            # Handle different message types
            if topic == self.TOPIC_CHAT:
                self.handle_chat_message(payload)
            elif topic == self.TOPIC_SYSTEM:
                self.handle_system_message(payload)
            elif topic == self.TOPIC_USERS or topic == f"chat/private/{self.username}":
                if payload.get("type") == "online_users":
                    self.handle_users_list(payload)
                elif payload.get("type") == "history":
                    self.handle_history(payload)
                    
        except json.JSONDecodeError:
            print(f"Invalid message received")
        except Exception as e:
            print(f"Error handling message: {e}")
            
    def handle_chat_message(self, payload):
        """Display chat messages"""
        username = payload.get("username", "Unknown")
        message = payload.get("message", "")
        timestamp = datetime.fromisoformat(payload.get("timestamp", datetime.now().isoformat()))
        
        # Don't display our own messages again
        if username != self.username:
            print(f"\n[{timestamp.strftime('%H:%M:%S')}] {username}: {message}")
            print(f"{self.username}> ", end="", flush=True)
            
    def handle_system_message(self, payload):
        """Handle system messages"""
        msg_type = payload.get("type")
        
        if msg_type == "user_join":
            print(f"\n➕ {payload['message']} (Online: {payload['online_users']})")
            if "users_list" in payload:
                self.online_users = payload['users_list']
                print(f"   👥 Online users: {', '.join(payload['users_list'])}")
                
        elif msg_type == "user_leave" or msg_type == "user_timeout":
            print(f"\n➖ {payload['message']} (Online: {payload['online_users']})")
            if "users_list" in payload:
                self.online_users = payload['users_list']
                print(f"   👥 Online users: {', '.join(payload['users_list'])}")
                
        print(f"{self.username}> ", end="", flush=True)
        
    def handle_users_list(self, payload):
        """Handle online users list"""
        self.online_users = payload['users']
        print(f"\n👥 Online users ({payload['count']}):")
        for i, user in enumerate(payload['users'], 1):
            status = " (You)" if user == self.username else ""
            print(f"   {i}. {user}{status}")
        print(f"{self.username}> ", end="", flush=True)
        
    def handle_history(self, payload):
        """Handle chat history"""
        print("\n📜 Recent chat history:")
        for msg in payload['messages']:
            timestamp = datetime.fromisoformat(msg['timestamp'])
            username = msg.get('username', 'Unknown')
            message = msg.get('message', '')
            print(f"  [{timestamp.strftime('%H:%M:%S')}] {username}: {message}")
        print(f"{self.username}> ", end="", flush=True)
        
    async def send_heartbeat(self):
        """Send periodic heartbeat to stay online"""
        while self.running:
            if self.connected:
                heartbeat_msg = {
                    "action": "heartbeat",
                    "username": self.username,
                    "timestamp": datetime.now().isoformat()
                }
                self.client.publish(self.TOPIC_PRESENCE, json.dumps(heartbeat_msg))
            await asyncio.sleep(30)  # Send heartbeat every 30 seconds
            
    async def send_message(self, message):
        """Send a chat message"""
        if self.connected:
            msg_data = {
                "type": "chat",
                "username": self.username,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            self.client.publish(self.TOPIC_CHAT, json.dumps(msg_data))
            
    async def request_users(self):
        """Request online users list"""
        if self.connected:
            users_request = {
                "requester": self.username,
                "timestamp": datetime.now().isoformat()
            }
            self.client.publish("chat/request/users", json.dumps(users_request))
            
    async def disconnect(self):
        """Disconnect from chat"""
        self.running = False
        if self.connected:
            # Send leave message
            leave_msg = {
                "action": "leave",
                "username": self.username,
                "timestamp": datetime.now().isoformat()
            }
            self.client.publish(self.TOPIC_PRESENCE, json.dumps(leave_msg))
            await asyncio.sleep(0.5)  # Give time for message to send
            
        self.client.loop_stop()
        self.client.disconnect()
        print("👋 Disconnected from chat")
        
    async def send_input(self):
        """Handle user input"""
        while self.running:
            try:
                message = await aioconsole.ainput(f"{self.username}> ")
                
                if message.strip():
                    if message.lower() == "/quit":
                        await self.disconnect()
                        break
                    elif message.lower() == "/help":
                        print("\n📋 Commands:")
                        print("  /help - Show this help message")
                        print("  /quit - Exit the chat")
                        print("  /users - Show online users")
                        print("  Just type to send a message!")
                    elif message.lower() == "/users":
                        await self.request_users()
                    else:
                        await self.send_message(message)
                        # Display our own message
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        print(f"[{timestamp}] {self.username}: {message}")
                        
            except EOFError:
                await self.disconnect()
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                
    async def run(self):
        """Run the chat client"""
        print("🎉 Welcome to MQTT Chat!")
        print("=" * 40)
        
        # Get broker address if not provided
        if not self.broker_host:
            print("\n📡 MQTT Broker Connection")
            broker_input = input("Enter broker address (default: nozomi.proxy.rlwy.net:32067): ").strip()
            
            if not broker_input:
                self.broker_host = "nozomi.proxy.rlwy.net"
                self.broker_port = 32067
            else:
                # Parse host and port
                if ":" in broker_input:
                    self.broker_host, port_str = broker_input.split(":", 1)
                    self.broker_port = int(port_str)
                else:
                    self.broker_host = broker_input
                    self.broker_port = 1883
                    
        print(f"Connecting to: {self.broker_host}:{self.broker_port}")
        
        # Get username
        while True:
            self.username = input("\nEnter your username: ").strip()
            if self.username:
                break
            print("❌ Username cannot be empty")
            
        # Create MQTT client with unique ID
        self.client = mqtt.Client(client_id=f"chat_client_{self.username}_{int(time.time())}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        print(f"\nHello, {self.username}! Connecting to MQTT broker...")
        
        # Connect to broker
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            # Wait for connection
            await asyncio.sleep(2)
            
            if not self.connected:
                print("❌ Failed to connect to MQTT broker")
                return
                
            print("\n💡 Type /help for commands or /quit to exit\n")
            
            # Start heartbeat task
            heartbeat_task = asyncio.create_task(self.send_heartbeat())
            
            # Handle user input
            await self.send_input()
            
            # Cancel heartbeat
            heartbeat_task.cancel()
            
        except Exception as e:
            print(f"❌ Connection error: {e}")
        finally:
            await self.disconnect()

async def main():
    """Main entry point"""
    # Check if broker address is provided as command line argument
    broker_host = None
    broker_port = None
    
    if len(sys.argv) > 1:
        broker_arg = sys.argv[1]
        if ":" in broker_arg:
            broker_host, port_str = broker_arg.split(":", 1)
            broker_port = int(port_str)
        else:
            broker_host = broker_arg
            broker_port = 1883
        print(f"Using broker: {broker_host}:{broker_port}")
        
    client = MQTTChatClient(broker_host, broker_port)
    await client.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Chat client stopped")
    except Exception as e:
        print(f"❌ Error: {e}")