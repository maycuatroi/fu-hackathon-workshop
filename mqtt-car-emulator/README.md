# MQTT AGV Emulator

A teaching tool for demonstrating MQTT communication through an Automated Guided Vehicle (AGV) emulator. This project allows teams to control virtual AGVs using MQTT messages.

## Overview

This project consists of two main components:
- **Server (server.py)**: Control center that sends commands to AGVs
- **AGV Emulator (agv.py)**: Simulates AGV behavior and responds to commands

Each team can control 2 AGVs independently using MQTT topics.

## Features

- **Dual AGV Support**: Each team can control 2 AGVs (AGV1 and AGV2)
- **Team-based Channels**: Separate MQTT topics for each team
- **Live Telemetry**: Real-time position, speed, direction, and battery status
- **Battery Simulation**: AGVs consume battery while moving
- **Command History**: Track recent commands sent to AGVs

## Prerequisites

- Python 3.7+
- MQTT Broker access (default configuration included)

## Installation

1. Clone the repository:
```bash
cd mqtt-car-emulator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Edit the MQTT configuration in both `server.py` and `agv.py`:

```python
MQTT_CONFIG = {
    "broker_host": "gondola.proxy.rlwy.net",
    "broker_port": 58346,
    "keep_alive": 60,
    "username": "binhna",  # TODO: Replace with your team name
    "password": "1",       # TODO: Replace with your team password
    "qos": 0,
}
```

## Usage

### Starting AGV Emulators

Run two AGV emulators (one for each AGV) in separate terminals:

**Terminal 1 - AGV 1:**
```bash
python agv.py
```
- Enter your team name
- Enter AGV number: `1`

**Terminal 2 - AGV 2:**
```bash
python agv.py
```
- Enter your team name (same as AGV 1)
- Enter AGV number: `2`

### Starting the Control Server

**Terminal 3 - Control Server:**
```bash
python server.py
```
- Enter your team name (same as AGVs)

## Available Commands

| Command             | Description              | Example         |
| ------------------- | ------------------------ | --------------- |
| `select <1\|2>`     | Select AGV to control    | `select 1`      |
| `set-speed <speed>` | Set AGV speed (0-10 m/s) | `set-speed 5.0` |
| `turn <direction>`  | Set movement direction   | `turn NE`       |
| `stop`              | Emergency stop           | `stop`          |
| `status`            | Request AGV status       | `status`        |
| `help`              | Show available commands  | `help`          |
| `quit`              | Exit the control server  | `quit`          |

### Directions
- **N**: North
- **NE**: Northeast  
- **E**: East
- **SE**: Southeast
- **S**: South
- **SW**: Southwest
- **W**: West
- **NW**: Northwest

## MQTT Topic Structure

Topics are organized by team and AGV number:

```
agv/{team_name}/agv{1|2}/control    # Commands to AGV
agv/{team_name}/agv{1|2}/status     # Status updates from AGV
agv/{team_name}/agv{1|2}/telemetry  # Real-time telemetry data
```

## Display Features

### Control Server Display
- **Left Panel**: Real-time telemetry table for both AGVs
- **Right Panel**: Activity log and messages
- **Footer**: Connection status and available commands

### AGV Emulator Display
- **Status Panel**: Current AGV state with color coding
- **Activity Log**: Recent commands and status changes
- **Command History**: Last 5 received commands

## Teaching Points

This emulator helps demonstrate:

1. **MQTT Pub/Sub Pattern**: How publishers and subscribers communicate
2. **Topic-based Routing**: Using hierarchical topics for message organization
3. **QoS Levels**: Understanding quality of service in MQTT
4. **Real-time Communication**: Low-latency message delivery
5. **Multi-client Architecture**: Multiple clients on same topics

## Troubleshooting

### Connection Issues
- Verify MQTT broker is accessible
- Check username/password configuration
- Ensure network connectivity

### AGV Not Responding
- Confirm team name matches between server and AGV
- Check AGV number selection (1 or 2)
- Verify MQTT connection status in display

### Display Issues
- Terminal must support Unicode characters
- Minimum terminal width: 80 characters
- Use a modern terminal emulator

## Example Workflow

1. Start AGV1 and AGV2 emulators
2. Start control server
3. Select AGV1: `select 1`
4. Set speed: `set-speed 3`
5. Turn east: `turn E`
6. Watch AGV move in emulator display
7. Select AGV2: `select 2`
8. Control AGV2 independently
9. Stop AGV: `stop`

## License

This project is for educational purposes.