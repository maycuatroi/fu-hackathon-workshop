import asyncio
import websockets
import json
import datetime
import socket

connected_clients = {}
chat_history = []
MAX_HISTORY = 50


async def broadcast_message(message, sender_ws=None):
    if connected_clients:
        tasks = []
        for client in connected_clients:
            if client != sender_ws and client.open:
                tasks.append(asyncio.create_task(client.send(json.dumps(message))))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


async def get_online_users():
    return [user_info["username"] for user_info in connected_clients.values()]


async def is_username_taken(username):
    for user_info in connected_clients.values():
        if user_info["username"].lower() == username.lower():
            return True
    return False


async def handle_client(websocket, path):
    client_id = f"user_{id(websocket)}"
    username = None

    try:
        async for message in websocket:
            try:
                data = json.loads(message)

                if data.get("type") == "set_username":
                    requested_username = data.get("username", "").strip()

                    if not requested_username:
                        error_msg = {"type": "username_error", "message": "Username cannot be empty"}
                        await websocket.send(json.dumps(error_msg))
                        continue

                    if await is_username_taken(requested_username):
                        error_msg = {
                            "type": "username_error",
                            "message": f"Username '{requested_username}' is already taken. Please choose another one.",
                        }
                        await websocket.send(json.dumps(error_msg))
                        continue

                    username = requested_username
                    connected_clients[websocket] = {"username": username, "client_id": client_id}

                    success_msg = {
                        "type": "username_accepted",
                        "username": username,
                        "timestamp": datetime.datetime.now().isoformat(),
                    }
                    await websocket.send(json.dumps(success_msg))

                    welcome_msg = {
                        "type": "system",
                        "message": f"Welcome to the chat room, {username}!",
                        "timestamp": datetime.datetime.now().isoformat(),
                    }
                    await websocket.send(json.dumps(welcome_msg))

                    online_users = await get_online_users()
                    users_list_msg = {"type": "online_users", "users": online_users, "count": len(online_users)}
                    await websocket.send(json.dumps(users_list_msg))

                    if chat_history:
                        history_msg = {"type": "history", "messages": chat_history[-20:]}
                        await websocket.send(json.dumps(history_msg))

                    join_msg = {
                        "type": "user_join",
                        "message": f"{username} joined the chat",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "online_users": len(connected_clients),
                        "users_list": online_users,
                    }
                    await broadcast_message(join_msg, websocket)

                    break

            except json.JSONDecodeError:
                error_msg = {"type": "error", "message": "Invalid message format"}
                await websocket.send(json.dumps(error_msg))

        if not username:
            return

        async for message in websocket:
            try:
                data = json.loads(message)

                if data.get("type") == "chat":
                    chat_msg = {
                        "type": "chat",
                        "client_id": client_id,
                        "message": data.get("message", ""),
                        "username": username,
                        "timestamp": datetime.datetime.now().isoformat(),
                    }

                    chat_history.append(chat_msg)
                    if len(chat_history) > MAX_HISTORY:
                        chat_history.pop(0)

                    await websocket.send(json.dumps(chat_msg))
                    await broadcast_message(chat_msg, websocket)

                elif data.get("type") == "ping":
                    pong_msg = {"type": "pong", "timestamp": datetime.datetime.now().isoformat()}
                    await websocket.send(json.dumps(pong_msg))

                elif data.get("type") == "get_users":
                    online_users = await get_online_users()
                    users_list_msg = {
                        "type": "online_users",
                        "users": online_users,
                        "count": len(online_users),
                        "timestamp": datetime.datetime.now().isoformat(),
                    }
                    await websocket.send(json.dumps(users_list_msg))

            except json.JSONDecodeError:
                error_msg = {"type": "error", "message": "Invalid message format"}
                await websocket.send(json.dumps(error_msg))
            except Exception:
                pass

    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception:
        pass
    finally:
        if websocket in connected_clients:
            del connected_clients[websocket]

        if connected_clients and username:
            online_users = await get_online_users()
            leave_msg = {
                "type": "user_leave",
                "message": f"{username} left the chat",
                "timestamp": datetime.datetime.now().isoformat(),
                "online_users": len(connected_clients),
                "users_list": online_users,
            }
            await broadcast_message(leave_msg)


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


async def main():
    host = "0.0.0.0"
    port = 8765
    local_ip = get_local_ip()

    print(f"Chat server starting...")
    print(f"Server running on ws://{local_ip}:{port}")
    print(f"Local connection: ws://localhost:{port}")
    print("Server started successfully!")

    async with websockets.serve(handle_client, host, port):
        await asyncio.Future()


if __name__ == "__main__":

    asyncio.run(main())
