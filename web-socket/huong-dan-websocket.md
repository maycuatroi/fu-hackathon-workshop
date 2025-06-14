# WebSocket với Python: Từ Zero đến Hero - Góc nhìn của một Solution Architect

## Câu chuyện bắt đầu từ một cuộc điện thoại...

Hãy tưởng tượng bạn đang nói chuyện điện thoại với một người bạn. Cả hai có thể nói và nghe **cùng một lúc**, phải không? Đó chính xác là cách WebSocket hoạt động - một "cuộc điện thoại" giữa browser và server!

Khác với HTTP truyền thống mà các bạn vẫn dùng để truy cập web (giống như gửi thư - gửi đi, chờ hồi âm), WebSocket cho phép:

- **Giao tiếp hai chiều real-time** - Như cuộc gọi video, không phải tin nhắn
- **Độ trễ cực thấp** - Tính bằng milliseconds, không phải giây
- **Tiết kiệm băng thông** - Không cần gửi headers dài dòng mỗi lần
- **Kết nối liên tục** - Một lần bắt tay, nói chuyện mãi mãi

## Khi nào tôi nên dùng WebSocket?

WebSocket là "vũ khí" tối ưu cho:

- **Chat applications**: Slack, Discord, Zalo... bạn nghĩ họ dùng gì?
- **Live dashboards**: Biểu đồ Bitcoin nhảy múa theo từng giây
- **Multiplayer games**: PUBG Mobile không thể chậm được 1 giây
- **Collaborative tools**: Google Docs - thấy con trỏ của đồng nghiệp real-time
- **Push notifications**: "Ting!" - Có người vừa like ảnh của bạn

## Bắt tay vào code thôi!

### Bước 1: Cài đặt "vũ khí"

```bash
pip install websockets
pip install aioconsole  # Để chat trong terminal như hacker thực thụ
```

### Bước 2: Tạo một WebSocket Server đơn giản

Hãy bắt đầu với một server "lắng nghe" cơ bản:

```python
import asyncio
import websockets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_client(websocket, path):
    """
    Đây là WebSocket server
    Mỗi client kết nối sẽ được phục vụ bởi function này
    """
    client_address = websocket.remote_address
    logger.info(f"🎉 Khách mới check-in từ {client_address}")

    try:
        # Lắng nghe tin nhắn
        async for message in websocket:
            logger.info(f"📨 Nhận được: {message}")

            # Echo lại
            response = f"🤖 Echo: {message}"
            await websocket.send(response)

    except websockets.exceptions.ConnectionClosed:
        logger.info(f"👋 Khách {client_address} đã check-out")

async def start_server():
    """Khởi động 'khách sạn' WebSocket của chúng ta"""
    host = "0.0.0.0"  # Lắng nghe từ mọi nơi
    port = 8765       # Cổng bí mật của chúng ta

    logger.info(f"🚀 WebSocket Server đang khởi động...")
    logger.info(f"📡 Địa chỉ: ws://localhost:{port}")

    async with websockets.serve(handle_client, host, port):
        logger.info("✅ Server sẵn sàng! Đang chờ khách...")
        await asyncio.Future()  # Chạy mãi mãi

if __name__ == "__main__":
    asyncio.run(start_server())
```

### Bước 3: Client kết nối như thế nào?

```python
import asyncio
import websockets
import json

async def hello_websocket():
    """Client đơn giản"""
    uri = "ws://localhost:8765"

    async with websockets.connect(uri) as websocket:
        # Gửi lời chào
        await websocket.send("Xin chào Server! 👋")

        # Chờ câu trả lời
        response = await websocket.recv()
        print(f"Server phản hồi: {response}")

# Chạy thử
asyncio.run(hello_websocket())
```

## Level Up: Xây dựng Chat Application thực thụ

### 1. Xác thực username (Không ai được trùng tên!)

```python
# Dictionary lưu trữ clients
connected_clients = {}  # {websocket: {"username": "Alice", "id": "123"}}

async def validate_username(username):
    """Kiểm tra username"""
    for client_info in connected_clients.values():
        if client_info["username"].lower() == username.lower():
            return False, "❌ Username đã tồn tại!"
    return True, "✅ Username hợp lệ!"

async def handle_new_user(websocket, username):
    """Quy trình 'check-in'"""
    # Validate username
    is_valid, message = await validate_username(username)

    if not is_valid:
        error_msg = {
            "type": "error",
            "message": message
        }
        await websocket.send(json.dumps(error_msg))
        return False

    # Lưu thông tin client
    connected_clients[websocket] = {
        "username": username,
        "id": str(id(websocket))
    }

    # Gửi thông báo chào mừng
    welcome_msg = {
        "type": "welcome",
        "message": f"🎉 Chào mừng {username} đến với chat room!"
    }
    await websocket.send(json.dumps(welcome_msg))

    return True
```

### 2. Broadcast messages

```python
async def broadcast_message(message, sender_ws=None):
    """
    Gửi tin nhắn cho tất cả mọi người
    """
    if not connected_clients:
        return

    # Tạo danh sách tasks để gửi đồng thời
    tasks = []
    for client_ws in connected_clients:
        # Không gửi lại cho người gửi
        if client_ws != sender_ws and client_ws.open:
            task = asyncio.create_task(
                client_ws.send(json.dumps(message))
            )
            tasks.append(task)

    # Gửi đồng thời
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
```

### 3. Theo dõi online users (Ai đang online?)

```python
async def get_online_users():
    """Lấy danh sách user"""
    return [
        info["username"]
        for info in connected_clients.values()
    ]

async def notify_user_list_update():
    """Cập nhật danh sách online cho mọi người"""
    online_users = await get_online_users()

    update_msg = {
        "type": "users_update",
        "users": online_users,
        "count": len(online_users),
        "message": f"👥 Hiện có {len(online_users)} người online"
    }

    await broadcast_message(update_msg)
```

## Best Practices

### 1. Heartbeat - Giữ kết nối

```python
async def heartbeat_handler(websocket):
    """
    Ping định kỳ để check xem client còn sống không
    """
    try:
        while True:
            await asyncio.sleep(30)  # 30 giây một lần
            pong_waiter = await websocket.ping()
            await asyncio.wait_for(pong_waiter, timeout=10)
    except:
        # Client không phản hồi
        logger.warning("Client không phản hồi ping")
```

### 2. Auto-reconnection - Không bỏ cuộc như Naruto

```python
class SmartWebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None
        self.reconnect_interval = 5  # seconds

    async def connect_with_retry(self):
        """persistent connection"""
        retry_count = 0

        while True:
            try:
                logger.info(f"Đang kết nối... (Lần thử: {retry_count + 1})")
                self.websocket = await websockets.connect(self.uri)
                logger.info("Kết nối thành công!")
                return True

            except Exception as e:
                retry_count += 1
                logger.error(f"Kết nối thất bại: {e}")

                if retry_count >= 5:
                    logger.error("Đã thử 5 lần, từ bỏ thôi...")
                    return False

                logger.info(f"⏳ Chờ {self.reconnect_interval}s rồi thử lại...")
                await asyncio.sleep(self.reconnect_interval)
```

### 3. Rate Limiting - Chống spam

## Security

1. Sử dụng WSS (WebSocket Secure)
2. Authentication rõ ràng chứ không chỉ nhập ID như bây giờ
3. Chú ý các hacker tiểu xảo gửi đoạn `html` trong message body.

## Scale lên như thế nào?

1. Sử dụng Redis cho nhiều servers
2. Load Balancing với Nginx
3. Distributed message storage

## Kết luận: Lessons Learned

Đây là những bài học xương máu:

1. **Start simple, scale later** - Đừng over-engineering từ đầu
2. **Monitor everything** - Log,
3. **Plan for failure** - Mọi thứ sẽ sập, hãy chuẩn bị
4. **Security first** - Bảo mật từ đầu, không phải sau khi bị hack
5. **User experience is king** - Nhanh, mượt, không lag mới là vua

## Tài nguyên để đào sâu hơn

- **Code mẫu đầy đủ**: Check các file `chat-server.py` và `chat-client.py` trong project
- **Python WebSockets Docs**: https://websockets.readthedocs.io/
- **My Blog**: [omelet.tech](https://omelet.tech) - Follow để đọc thêm về AI, Security, Distributed systems

---

_Chúc các bạn bắn message vui vẻ_

_P/S: Coffee ☕ là nguồn năng lượng chính của tôi khi viết bài này._
