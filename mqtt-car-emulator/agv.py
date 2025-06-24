#!/usr/bin/env python3
"""
AGV Emulator
Receives control commands via MQTT and simulates AGV behavior
Supports multiple teams with separate channels
"""

import paho.mqtt.client as mqtt
import json
import time
import threading
from datetime import datetime
import random
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from collections import deque

# MQTT Configuration
MQTT_CONFIG = {
    "broker_host": "gondola.proxy.rlwy.net",
    "broker_port": 58346,
    "keep_alive": 60,
    "username": "binhna",  # todo: Replace by team name
    "password": "1",  # todo: Replace by team password
    "qos": 0,  # Quality of Service (0, 1, or 2)
}

class AGVEmulator:
    def __init__(self, team_name, agv_number):
        self.broker_host = MQTT_CONFIG["broker_host"]
        self.broker_port = MQTT_CONFIG["broker_port"]
        self.team_name = team_name
        self.agv_number = agv_number  # 1 or 2
        self.agv_id = f"{team_name}_AGV{agv_number}"
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=f"agv_{team_name}_agv{agv_number}")
        self.is_connected = False
        self.running = True
        
        # Set username and password
        self.client.username_pw_set(MQTT_CONFIG["username"], MQTT_CONFIG["password"])
        
        # MQTT Topics - team and AGV specific
        self.TOPIC_CONTROL = f"agv/{team_name}/agv{agv_number}/control"
        self.TOPIC_STATUS = f"agv/{team_name}/agv{agv_number}/status"
        self.TOPIC_TELEMETRY = f"agv/{team_name}/agv{agv_number}/telemetry"
        
        # AGV State
        self.position = {"x": 0.0, "y": 0.0}
        self.speed = 0.0  # m/s
        self.direction = "N"  # N, NE, E, SE, S, SW, W, NW
        self.battery = 100.0  # percentage
        self.status = "idle"  # idle, moving, charging, error
        
        # Direction vectors
        self.direction_vectors = {
            "N": (0, 1),
            "NE": (0.707, 0.707),
            "E": (1, 0),
            "SE": (0.707, -0.707),
            "S": (0, -1),
            "SW": (-0.707, -0.707),
            "W": (-1, 0),
            "NW": (-0.707, 0.707)
        }
        
        # Setup callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Rich console and message buffer
        self.console = Console()
        self.messages = deque(maxlen=15)  # Keep last 15 messages
        self.commands_received = deque(maxlen=10)  # Keep last 10 commands
        self.lock = threading.Lock()
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.is_connected = True
            with self.lock:
                self.messages.append((f"✅ AGV{self.agv_number} Connected to MQTT broker", "success"))
                self.messages.append((f"🏷️  Team: {self.team_name}", "info"))
                self.messages.append((f"🤖 AGV ID: {self.agv_id}", "info"))
                self.messages.append((f"📡 Listening on: {self.TOPIC_CONTROL}", "info"))
            
            # Subscribe to control commands
            client.subscribe(self.TOPIC_CONTROL)
            
            # Send initial status
            self.send_status("AGV online and ready")
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
            payload = json.loads(msg.payload.decode())
            command = payload.get("command", "")
            team = payload.get("team", "")
            target_agv = payload.get("agv_id", "")
            
            # Only process commands for our team and AGV
            if team != self.team_name or target_agv != self.agv_number:
                return
                
            with self.lock:
                self.messages.append((f"📥 Received command: {command}", "command"))
                self.commands_received.append(f"{datetime.now().strftime('%H:%M:%S')} - {command}")
            
            # Process command
            if command == "move":
                self.handle_move(payload.get("speed", 0))
            elif command == "turn":
                self.handle_turn(payload.get("direction", "N"))
            elif command == "stop":
                self.handle_stop()
            elif command == "status_request":
                self.send_status("Status requested")
            else:
                with self.lock:
                    self.messages.append((f"❌ Unknown command: {command}", "error"))
                
        except json.JSONDecodeError:
            with self.lock:
                self.messages.append(("❌ Invalid JSON received", "error"))
        except Exception as e:
            with self.lock:
                self.messages.append((f"❌ Error handling message: {e}", "error"))
            
    def handle_move(self, speed):
        """Handle move command"""
        self.speed = max(0, min(speed, 10))  # Clamp speed between 0-10
        if self.speed > 0:
            self.status = "moving"
            with self.lock:
                self.messages.append((f"🚗 Moving at {self.speed} m/s in direction {self.direction}", "status"))
        else:
            self.status = "idle"
            with self.lock:
                self.messages.append(("🛑 AGV stopped", "status"))
        self.send_status(f"Speed set to {self.speed} m/s")
        
    def handle_turn(self, direction):
        """Handle turn command"""
        if direction in self.direction_vectors:
            self.direction = direction
            with self.lock:
                self.messages.append((f"🧭 Direction set to {self.direction}", "status"))
            self.send_status(f"Direction set to {self.direction}")
        else:
            with self.lock:
                self.messages.append((f"❌ Invalid direction: {direction}", "error"))
            self.send_status(f"Invalid direction: {direction}")
            
    def handle_stop(self):
        """Handle emergency stop"""
        self.speed = 0
        self.status = "idle"
        with self.lock:
            self.messages.append(("🛑 EMERGENCY STOP!", "warning"))
        self.send_status("Emergency stop activated")
            
    def send_status(self, message=""):
        """Send status update"""
        if not self.is_connected:
            return
            
        status_data = {
            "agv_id": self.agv_id,
            "agv_number": self.agv_number,
            "team": self.team_name,
            "status": self.status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        self.client.publish(self.TOPIC_STATUS, json.dumps(status_data))
        
    def send_telemetry(self):
        """Send telemetry data"""
        if not self.is_connected:
            return
            
        telemetry_data = {
            "agv_id": self.agv_id,
            "agv_number": self.agv_number,
            "team": self.team_name,
            "position": self.position,
            "speed": self.speed,
            "direction": self.direction,
            "battery": self.battery,
            "status": self.status,
            "timestamp": datetime.now().isoformat()
        }
        
        self.client.publish(self.TOPIC_TELEMETRY, json.dumps(telemetry_data))
        
    def update_position(self):
        """Update AGV position based on speed and direction"""
        if self.status == "moving" and self.speed > 0:
            # Get direction vector
            dx, dy = self.direction_vectors[self.direction]
            
            # Update position (assuming 1 second interval)
            self.position["x"] += dx * self.speed
            self.position["y"] += dy * self.speed
            
            # Simulate battery drain
            self.battery = max(0, self.battery - 0.1)
            
            # Check battery
            if self.battery < 10:
                with self.lock:
                    self.messages.append(("⚠️  Low battery warning!", "warning"))
                if self.battery <= 0:
                    self.speed = 0
                    self.status = "error"
                    self.send_status("Battery depleted - AGV stopped")
                    
    def create_layout(self):
        """Create the console layout"""
        layout = Layout()
        
        # Create main sections
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=4)
        )
        
        # Split body into panels
        layout["body"].split_row(
            Layout(name="status", ratio=1),
            Layout(name="messages", ratio=1)
        )
        
        # Header
        header_text = Text(f"🤖 AGV{self.agv_number} Emulator - Team: {self.team_name}", style="bold cyan")
        layout["header"].update(Panel(header_text, title="AGV Control System"))
        
        # Status panel
        status_table = Table(show_header=False, box=None)
        status_table.add_column("Property", style="cyan")
        status_table.add_column("Value", style="yellow")
        
        status_color = "green" if self.status == "moving" else "yellow" if self.status == "idle" else "red"
        status_table.add_row("Status", f"[{status_color}]{self.status.upper()}[/{status_color}]")
        status_table.add_row("Position", f"({self.position['x']:.1f}, {self.position['y']:.1f})")
        status_table.add_row("Speed", f"{self.speed:.1f} m/s")
        status_table.add_row("Direction", self.direction)
        
        # Battery with color coding
        battery_color = "green" if self.battery > 50 else "yellow" if self.battery > 20 else "red"
        status_table.add_row("Battery", f"[{battery_color}]{self.battery:.1f}%[/{battery_color}]")
        
        # Add commands history
        if self.commands_received:
            status_table.add_row("", "")  # Empty row
            status_table.add_row("[bold]Recent Commands:[/bold]", "")
            for cmd in list(self.commands_received)[-5:]:  # Show last 5 commands
                status_table.add_row("", cmd)
        
        layout["status"].update(Panel(status_table, title="AGV Status"))
        
        # Messages panel
        messages_text = Text()
        for msg, msg_type in list(self.messages):
            if msg_type == "error":
                messages_text.append(f"{msg}\n", style="red")
            elif msg_type == "success":
                messages_text.append(f"{msg}\n", style="green")
            elif msg_type == "command":
                messages_text.append(f"{msg}\n", style="blue")
            elif msg_type == "warning":
                messages_text.append(f"{msg}\n", style="yellow bold")
            elif msg_type == "status":
                messages_text.append(f"{msg}\n", style="cyan")
            else:
                messages_text.append(f"{msg}\n", style="white")
        
        layout["messages"].update(Panel(messages_text, title="Activity Log"))
        
        # Footer with connection status
        if self.is_connected:
            conn_status = "[green]● Connected[/green]"
        else:
            conn_status = "[red]● Disconnected[/red]"
            
        footer_text = f"{conn_status} | Broker: {self.broker_host}:{self.broker_port} | Press Ctrl+C to stop"
        layout["footer"].update(Panel(footer_text, style="dim"))
        
        return layout
                
    def simulation_loop(self):
        """Main simulation loop"""
        while self.running:
            try:
                if self.is_connected:
                    # Update AGV state
                    self.update_position()
                    
                    # Send telemetry
                    self.send_telemetry()
                    
                time.sleep(1)  # Update every second
                
            except Exception as e:
                with self.lock:
                    self.messages.append((f"❌ Simulation error: {e}", "error"))
                
    def run(self):
        """Run the AGV emulator"""
        self.console.clear()
        self.console.print("🤖 AGV Emulator Started", style="bold cyan")
        self.console.print("=" * 50)
        
        try:
            # Connect to broker
            self.client.connect(self.broker_host, self.broker_port, MQTT_CONFIG["keep_alive"])
            self.client.loop_start()
            
            # Wait for connection
            time.sleep(2)
            
            if not self.is_connected:
                self.console.print("❌ Failed to connect to MQTT broker", style="red")
                return
            
            # Start simulation thread
            sim_thread = threading.Thread(target=self.simulation_loop)
            sim_thread.daemon = True
            sim_thread.start()
            
            # Start live display
            with Live(self.create_layout(), refresh_per_second=10, console=self.console) as live:
                while self.running:
                    try:
                        with self.lock:
                            live.update(self.create_layout())
                        time.sleep(0.1)
                    except KeyboardInterrupt:
                        break
                        
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.console.print(f"❌ Error: {e}", style="red")
        finally:
            self.running = False
            with self.lock:
                self.messages.append(("👋 Shutting down AGV...", "info"))
            self.send_status("AGV shutting down")
            time.sleep(0.5)  # Give time for final message
            self.client.loop_stop()
            self.client.disconnect()
            self.console.print("\n👋 AGV emulator stopped", style="yellow")

def main():
    """Main entry point"""
    console = Console()
    console.print("🚗 AGV Emulator", style="bold cyan")
    console.print("=" * 50)
    
    # Get team name
    team_name = console.input("[bold cyan]Enter your team name:[/bold cyan] ").strip()
    while not team_name:
        console.print("❌ Team name cannot be empty", style="red")
        team_name = console.input("[bold cyan]Enter your team name:[/bold cyan] ").strip()
    
    # Get AGV number
    agv_number = None
    while agv_number not in [1, 2]:
        try:
            agv_number = int(console.input("[bold cyan]Enter AGV number (1 or 2):[/bold cyan] ").strip())
            if agv_number not in [1, 2]:
                console.print("❌ AGV number must be 1 or 2", style="red")
        except ValueError:
            console.print("❌ Please enter a valid number (1 or 2)", style="red")
    
    console.print(f"\n[green]Connecting to MQTT broker:[/green]")
    console.print(f"  Host: {MQTT_CONFIG['broker_host']}")
    console.print(f"  Port: {MQTT_CONFIG['broker_port']}")
    console.print(f"  Username: {MQTT_CONFIG['username']}")
    
    # Create and run AGV
    agv = AGVEmulator(team_name, agv_number)
    agv.run()

if __name__ == "__main__":
    main()