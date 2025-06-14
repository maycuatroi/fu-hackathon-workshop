#!/usr/bin/env python3
"""
Simple WebSocket Chat Client
Requires: pip install websockets
"""

import asyncio
import websockets
import json
import aioconsole
from datetime import datetime

class ChatClient:
    def __init__(self, uri=None):
        self.uri = uri
        self.websocket = None
        self.username = None
        self.running = True
        self.online_users = []
    
    async def connect(self):
        """Connect to the WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.uri)
            print(f"✅ Connected to {self.uri}")
            
            # Send username for validation
            username_msg = {
                "type": "set_username",
                "username": self.username
            }
            await self.websocket.send(json.dumps(username_msg))
            
            # Wait for username validation response
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data["type"] == "username_error":
                print(f"❌ {data['message']}")
                await self.websocket.close()
                return False
            elif data["type"] == "username_accepted":
                print(f"✅ Username '{self.username}' accepted!")
                return True
            
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the server"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            print("👋 Disconnected from server")
    
    async def send_message(self, message):
        """Send a chat message"""
        if self.websocket and not self.websocket.closed:
            msg_data = {
                "type": "chat",
                "message": message,
                "username": self.username
            }
            await self.websocket.send(json.dumps(msg_data))
    
    async def request_users(self):
        """Request the list of online users"""
        if self.websocket and not self.websocket.closed:
            msg_data = {
                "type": "get_users"
            }
            await self.websocket.send(json.dumps(msg_data))
    
    async def receive_messages(self):
        """Receive and display messages from the server"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                if data["type"] == "system":
                    print(f"\n📢 System: {data['message']}")
                
                elif data["type"] == "chat":
                    timestamp = datetime.fromisoformat(data["timestamp"]).strftime("%H:%M:%S")
                    username = data.get("username", data["client_id"])
                    
                    # Don't display our own messages again
                    if username != self.username:
                        print(f"\n[{timestamp}] {username}: {data['message']}")
                    
                elif data["type"] == "user_join":
                    print(f"\n➕ {data['message']} (Online: {data['online_users']})")
                    if "users_list" in data:
                        self.online_users = data['users_list']
                        print(f"   👥 Online users: {', '.join(data['users_list'])}")
                
                elif data["type"] == "user_leave":
                    print(f"\n➖ {data['message']} (Online: {data['online_users']})")
                    if "users_list" in data:
                        self.online_users = data['users_list']
                        print(f"   👥 Online users: {', '.join(data['users_list'])}")
                
                elif data["type"] == "online_users":
                    self.online_users = data['users']
                    print(f"\n👥 Online users ({data['count']}):")
                    for i, user in enumerate(data['users'], 1):
                        status = " (You)" if user == self.username else ""
                        print(f"   {i}. {user}{status}")
                
                elif data["type"] == "history":
                    print("\n📜 Recent chat history:")
                    for msg in data["messages"]:
                        if msg["type"] == "chat":
                            timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M:%S")
                            username = msg.get("username", msg["client_id"])
                            print(f"  [{timestamp}] {username}: {msg['message']}")
                
                elif data["type"] == "error":
                    print(f"\n❗ Error: {data['message']}")
                
                # Print prompt again
                print(f"\n{self.username}> ", end="", flush=True)
                
        except websockets.exceptions.ConnectionClosed:
            print("\n❌ Connection lost")
            self.running = False
        except Exception as e:
            print(f"\n❌ Error receiving message: {e}")
            self.running = False
    
    async def send_input(self):
        """Handle user input"""
        while self.running:
            try:
                # Get input without blocking
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
                # Handle Ctrl+D
                await self.disconnect()
                break
            except Exception as e:
                print(f"\n❌ Error sending message: {e}")
    
    async def run(self):
        """Run the chat client"""
        print("🎉 Welcome to WebSocket Chat!")
        print("=" * 40)
        
        # Get server address if not provided
        if not self.uri:
            print("\n📡 Server Connection")
            server_input = input("Enter server address (default: localhost:8765): ").strip()
            
            if not server_input:
                server_input = "localhost:8765"
            
            # Add ws:// prefix if not present
            if not server_input.startswith("ws://") and not server_input.startswith("wss://"):
                self.uri = f"ws://{server_input}"
            else:
                self.uri = server_input
            
            print(f"Connecting to: {self.uri}")
        
        while True:
            # Get username
            self.username = input("\nEnter your username: ").strip()
            if not self.username:
                print("❌ Username cannot be empty. Please try again.")
                continue
            
            print(f"\nHello, {self.username}! Connecting to chat server...")
            
            # Connect to server
            if await self.connect():
                break
            else:
                print("\n🔄 Please choose a different username.\n")
                continue
        
        print("\n💡 Type /help for commands or /quit to exit\n")
        
        # Run receive and send tasks concurrently
        try:
            receive_task = asyncio.create_task(self.receive_messages())
            send_task = asyncio.create_task(self.send_input())
            
            # Wait for either task to complete
            done, pending = await asyncio.wait(
                [receive_task, send_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        finally:
            await self.disconnect()

async def main():
    """Main entry point"""
    import sys
    
    # Check if server address is provided as command line argument
    uri = None
    if len(sys.argv) > 1:
        server_arg = sys.argv[1]
        if not server_arg.startswith("ws://") and not server_arg.startswith("wss://"):
            uri = f"ws://{server_arg}"
        else:
            uri = server_arg
        print(f"Using server: {uri}")
    
    client = ChatClient(uri)
    await client.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Chat client stopped")
    except Exception as e:
        print(f"❌ Error: {e}")