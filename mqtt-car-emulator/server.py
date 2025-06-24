#!/usr/bin/env python3
"""
AGV Control Server
Publishes control commands to AGV via MQTT
Supports multiple teams with separate channels
"""

import paho.mqtt.client as mqtt
import json
import time
import sys
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from collections import deque
import threading

# MQTT Configuration
MQTT_CONFIG = {
    "broker_host": "gondola.proxy.rlwy.net",
    "broker_port": 58346,
    "keep_alive": 60,
    "username": "binhna",  # todo: Replace by team name
    "password": "1",  # todo: Replace by team password
    "qos": 0,  # Quality of Service (0, 1, or 2)
}

class AGVControlServer:
    def __init__(self, team_name):
        self.broker_host = MQTT_CONFIG["broker_host"]
        self.broker_port = MQTT_CONFIG["broker_port"]
        self.team_name = team_name
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=f"agv_control_server_{team_name}")
        self.is_connected = False
        self.current_agv = None  # Currently selected AGV (1 or 2)
        
        # Set username and password
        self.client.username_pw_set(MQTT_CONFIG["username"], MQTT_CONFIG["password"])
        
        # MQTT Topics - team and AGV specific
        self.TOPIC_CONTROL_BASE = f"agv/{team_name}"
        self.TOPIC_STATUS_BASE = f"agv/{team_name}"
        self.TOPIC_TELEMETRY_BASE = f"agv/{team_name}"
        
        # Setup callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Rich console and message buffer
        self.console = Console()
        self.messages = deque(maxlen=20)  # Keep last 20 messages
        self.telemetry_data = {}  # Store latest telemetry for each AGV
        self.command_history = deque(maxlen=10)
        self.lock = threading.Lock()
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.is_connected = True
            with self.lock:
                self.messages.append(("✅ Connected to MQTT broker", "success"))
                self.messages.append((f"🏷️  Team: {self.team_name}", "info"))
            
            # Subscribe to status and telemetry from both AGVs
            for agv_id in [1, 2]:
                status_topic = f"{self.TOPIC_STATUS_BASE}/agv{agv_id}/status"
                telemetry_topic = f"{self.TOPIC_TELEMETRY_BASE}/agv{agv_id}/telemetry"
                client.subscribe(status_topic)
                client.subscribe(telemetry_topic)
                with self.lock:
                    self.messages.append((f"📡 Subscribed to AGV{agv_id} topics", "info"))
        else:
            self.is_connected = False
            with self.lock:
                self.messages.append((f"❌ Failed to connect (Code: {rc})", "error"))
            
    def on_disconnect(self, client, userdata, rc):
        self.is_connected = False
        with self.lock:
            self.messages.append((f"❌ Disconnected from broker (Code: {rc})", "error"))
        
    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            # Determine which AGV sent the message
            if "/agv1/" in topic:
                agv_num = 1
            elif "/agv2/" in topic:
                agv_num = 2
            else:
                return
                
            if topic.endswith("/status"):
                self.handle_status(payload, agv_num)
            elif topic.endswith("/telemetry"):
                self.handle_telemetry(payload, agv_num)
                
        except json.JSONDecodeError:
            with self.lock:
                self.messages.append((f"❌ Invalid JSON received on topic {topic}", "error"))
        except Exception as e:
            with self.lock:
                self.messages.append((f"❌ Error handling message: {e}", "error"))
            
    def handle_status(self, payload, agv_num):
        """Handle AGV status messages"""
        message = payload.get("message", "")
        status = payload.get("status", "Unknown")
        
        with self.lock:
            self.messages.append((f"📊 AGV{agv_num} Status: {status} - {message}", "status"))
        
    def handle_telemetry(self, payload, agv_num):
        """Handle AGV telemetry data"""
        with self.lock:
            self.telemetry_data[agv_num] = payload
            
    def send_control_command(self, command_type, **kwargs):
        """Send control command to AGV"""
        if not self.is_connected:
            with self.lock:
                self.messages.append(("❌ Not connected to broker", "error"))
            return
            
        if self.current_agv is None:
            with self.lock:
                self.messages.append(("❌ No AGV selected. Use 'select 1' or 'select 2' first.", "error"))
            return
            
        command = {
            "command": command_type,
            "team": self.team_name,
            "agv_id": self.current_agv,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        
        control_topic = f"{self.TOPIC_CONTROL_BASE}/agv{self.current_agv}/control"
        self.client.publish(control_topic, json.dumps(command))
        
        with self.lock:
            self.messages.append((f"📤 Sent to AGV{self.current_agv}: {command_type} {kwargs}", "command"))
            self.command_history.append(f"{command_type} {kwargs}")
    
    def create_layout(self):
        """Create the console layout"""
        layout = Layout()
        
        # Create main sections
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Split body into panels
        layout["body"].split_row(
            Layout(name="telemetry", ratio=1),
            Layout(name="messages", ratio=1)
        )
        
        # Header
        header_text = Text(f"🎮 AGV Control Server - Team: {self.team_name}", style="bold blue")
        layout["header"].update(Panel(header_text, title="Control Center"))
        
        # Telemetry panel
        telemetry_table = Table(title="AGV Telemetry", show_header=True, header_style="bold magenta")
        telemetry_table.add_column("AGV", style="cyan", width=6)
        telemetry_table.add_column("Status", style="green")
        telemetry_table.add_column("Position", style="yellow")
        telemetry_table.add_column("Speed", style="blue")
        telemetry_table.add_column("Direction", style="magenta")
        telemetry_table.add_column("Battery", style="red")
        
        for agv_num in [1, 2]:
            if agv_num in self.telemetry_data:
                data = self.telemetry_data[agv_num]
                pos = data.get("position", {})
                telemetry_table.add_row(
                    f"AGV{agv_num}",
                    data.get("status", "Unknown"),
                    f"({pos.get('x', 0):.1f}, {pos.get('y', 0):.1f})",
                    f"{data.get('speed', 0):.1f} m/s",
                    data.get("direction", "Unknown"),
                    f"{data.get('battery', 0):.1f}%"
                )
            else:
                telemetry_table.add_row(
                    f"AGV{agv_num}",
                    "Offline",
                    "-",
                    "-",
                    "-",
                    "-"
                )
        
        layout["telemetry"].update(Panel(telemetry_table))
        
        # Messages panel
        messages_text = Text()
        for msg, msg_type in list(self.messages):
            if msg_type == "error":
                messages_text.append(f"{msg}\n", style="red")
            elif msg_type == "success":
                messages_text.append(f"{msg}\n", style="green")
            elif msg_type == "command":
                messages_text.append(f"{msg}\n", style="blue")
            elif msg_type == "status":
                messages_text.append(f"{msg}\n", style="yellow")
            else:
                messages_text.append(f"{msg}\n", style="white")
        
        layout["messages"].update(Panel(messages_text, title="Messages"))
        
        # Footer with current AGV
        agv_text = f"Selected: AGV{self.current_agv}" if self.current_agv else "No AGV Selected"
        footer_text = Text(f"{agv_text} | Commands: select, set-speed, turn, stop, status, help, quit", style="dim")
        layout["footer"].update(Panel(footer_text))
        
        return layout
        
    def run_interactive(self):
        """Run interactive control mode"""
        self.console.clear()
        self.console.print("🎮 AGV Control Server - Interactive Mode", style="bold blue")
        self.console.print("=" * 50)
        
        # Connect to broker
        try:
            self.client.connect(self.broker_host, self.broker_port, MQTT_CONFIG["keep_alive"])
            self.client.loop_start()
            
            # Wait for connection
            time.sleep(2)
            
            if not self.is_connected:
                self.console.print("❌ Failed to connect to MQTT broker", style="red")
                return
            
            # Start the live display in a separate thread
            def update_display(live):
                while self.running:
                    with self.lock:
                        live.update(self.create_layout())
                    time.sleep(0.1)
            
            self.running = True
            with Live(self.create_layout(), refresh_per_second=10, screen=False) as live:
                # Start display update thread
                display_thread = threading.Thread(target=update_display, args=(live,))
                display_thread.daemon = True
                display_thread.start()
                
                # Command loop
                while self.running:
                    try:
                        # Get command without affecting the display
                        user_input = self.console.input("\n[bold cyan]Command>[/bold cyan] ").strip().lower()
                        
                        if user_input == "quit":
                            self.running = False
                            break
                            
                        elif user_input.startswith("select "):
                            try:
                                agv_id = int(user_input.split()[1])
                                if agv_id in [1, 2]:
                                    self.current_agv = agv_id
                                    with self.lock:
                                        self.messages.append((f"✅ Selected AGV{agv_id}", "success"))
                                else:
                                    with self.lock:
                                        self.messages.append(("❌ Invalid AGV ID. Use 1 or 2.", "error"))
                            except (IndexError, ValueError):
                                with self.lock:
                                    self.messages.append(("❌ Invalid command. Use: select <1|2>", "error"))
                            
                        elif user_input == "stop":
                            self.send_control_command("stop")
                            
                        elif user_input == "status":
                            self.send_control_command("status_request")
                            
                        elif user_input.startswith("set-speed "):
                            try:
                                speed = float(user_input.split()[1])
                                if 0 <= speed <= 10:
                                    self.send_control_command("move", speed=speed)
                                else:
                                    with self.lock:
                                        self.messages.append(("❌ Speed must be between 0 and 10 m/s", "error"))
                            except (IndexError, ValueError):
                                with self.lock:
                                    self.messages.append(("❌ Invalid command. Use: set-speed <speed>", "error"))
                                
                        elif user_input.startswith("turn "):
                            try:
                                direction = user_input.split()[1].upper()
                                valid_directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
                                if direction in valid_directions:
                                    self.send_control_command("turn", direction=direction)
                                else:
                                    with self.lock:
                                        self.messages.append((f"❌ Invalid direction. Use: {', '.join(valid_directions)}", "error"))
                            except IndexError:
                                with self.lock:
                                    self.messages.append(("❌ Invalid command. Use: turn <direction>", "error"))
                                
                        elif user_input == "help":
                            help_text = """
📋 Commands:
  select <1|2> - Select AGV to control
  set-speed <speed> - Set speed (0-10 m/s)
  turn <direction> - Set direction (N, NE, E, SE, S, SW, W, NW)
  stop - Emergency stop
  status - Get AGV status
  help - Show this help
  quit - Exit
                            """
                            with self.lock:
                                for line in help_text.strip().split('\n'):
                                    self.messages.append((line, "info"))
                            
                        else:
                            if user_input:  # Don't show error for empty input
                                with self.lock:
                                    self.messages.append(("❌ Unknown command. Type 'help' for available commands.", "error"))
                                    
                    except KeyboardInterrupt:
                        self.running = False
                        break
                    except Exception as e:
                        with self.lock:
                            self.messages.append((f"❌ Error: {e}", "error"))
                            
        except Exception as e:
            self.console.print(f"❌ Connection error: {e}", style="red")
        finally:
            self.running = False
            self.client.loop_stop()
            self.client.disconnect()
            self.console.print("\n👋 Control server stopped", style="yellow")

def main():
    """Main entry point"""
    console = Console()
    console.print("🚗 AGV Control Server", style="bold blue")
    console.print("=" * 50)
    
    # Get team name
    team_name = console.input("[bold cyan]Enter your team name:[/bold cyan] ").strip()
    while not team_name:
        console.print("❌ Team name cannot be empty", style="red")
        team_name = console.input("[bold cyan]Enter your team name:[/bold cyan] ").strip()
    
    console.print(f"\n[green]Connecting to MQTT broker:[/green]")
    console.print(f"  Host: {MQTT_CONFIG['broker_host']}")
    console.print(f"  Port: {MQTT_CONFIG['broker_port']}")
    console.print(f"  Username: {MQTT_CONFIG['username']}")
    
    server = AGVControlServer(team_name)
    server.run_interactive()

if __name__ == "__main__":
    main()