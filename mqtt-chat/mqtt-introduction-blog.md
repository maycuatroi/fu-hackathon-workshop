# MQTT: Giao thức nhắn tin nhẹ cho IoT và hơn thế nữa

## Message Broker - Khái niệm cơ bản

Hãy tưởng tượng Message Broker như một bưu điện: người gửi (publisher) không cần biết địa chỉ cụ thể của người nhận (subscriber), chỉ cần gửi thư với tem phù hợp. Bưu điện sẽ lo việc phân phối.

### Các loại Message Broker phổ biến

**Mỗi broker như một loại phương tiện vận chuyển khác nhau:**

- **RabbitMQ**: Xe tải đa năng - chở được nhiều loại hàng (AMQP, STOMP, MQTT)
- **Apache Kafka**: Tàu container - xử lý lượng hàng khổng lồ, phân tán
- **Redis Pub/Sub**: Xe máy - nhanh, gọn nhẹ, chạy trong RAM
- **Amazon SQS/SNS**: Dịch vụ ship hàng - không cần tự quản lý phương tiện
- **MQTT Brokers**: Xe đạp - siêu nhẹ, tiết kiệm năng lượng cho IoT

### MQTT - Lựa chọn tối ưu cho IoT

**Tại sao MQTT là "xe đạp" hoàn hảo cho IoT?**

- **Cực kỳ nhẹ**: Header chỉ 2 bytes (nhẹ như tin nhắn SMS)
- **Băng thông thấp**: Hoạt động tốt với 2G/3G (như WhatsApp thời 2010)
- **Tiết kiệm pin**: Sensor có thể chạy hàng năm với 1 viên pin AA
- **Quy mô lớn**: 1 broker xử lý được triệu thiết bị (như 1 tổng đài điện thoại)

## Giới thiệu về MQTT

**MQTT = WhatsApp cho máy móc** 💬

Ra đời năm 1999 bởi IBM để theo dõi đường ống dầu ở sa mạc. Giờ đây, MQTT là tiêu chuẩn quốc tế cho IoT - từ cảm biến nhiệt độ trong nhà đến xe Tesla báo cáo vị trí.

## Kiến trúc MQTT

### 1. Các thành phần chính

**Broker**

- Nhận cuộc gọi từ mọi người
- Chuyển đúng người, đúng nội dung
- Kiểm tra ai được phép gọi

**Client**

- Có thể gọi (publish) hoặc nhận cuộc gọi (subscribe)
- 1 chiếc điện thoại có thể vừa gọi vừa nhận

**Topic**

- Ví dụ: `home/bedroom/temperature` = phòng ngủ báo nhiệt độ
- Wildcard `+`: `home/+/temperature` = mọi phòng báo nhiệt độ
- Wildcard `#`: `home/#` = mọi thứ trong nhà

### 2. Cơ chế hoạt động

```
Sensor → "nhà/phòng khách/nhiệt độ: 25°C" → Broker → App điện thoại
```

**3 bước đơn giản:**

1. Sensor gửi: "25°C" vào topic `home/livingroom/temp`
2. Broker kiểm tra: "Ai quan tâm nhiệt độ phòng khách?"
3. Broker chuyển: Gửi "25°C" cho mọi app đang theo dõi

### 3. Quality of Service (QoS)

**QoS**

- **QoS 0** = Thả thư vào hộp: Nhanh nhất, không biết có nhận không
- **QoS 1** = Gửi thường: Đảm bảo nhận, có thể nhận 2 lần
- **QoS 2** = Gửi bảo đảm: Chậm nhất, nhận đúng 1 lần

💡 **Mẹo**: Dùng QoS 0 cho nhiệt độ (mất 1 lần không sao), QoS 2 cho lệnh bật/tắt thiết bị

## So sánh MQTT với WebSocket

### WebSocket là gì?

**WebSocket**

Giống như FaceTime - cả 2 bên có thể nói chuyện cùng lúc, real-time, không cần chờ lượt.

### MQTT vs WebSocket - Cuộc chiến công nghệ

| Tiêu chí                           | MQTT                                         | WebSocket                                  |
| ---------------------------------- | -------------------------------------------- | ------------------------------------------ |
| **1. Mô hình giao tiếp**           | Như group chat - gửi 1 lần, nhiều người nhận | Như điện thoại - chỉ nói chuyện 1-1        |
| **2. Tiết kiệm dữ liệu**           | Header 2 bytes (= 2 ký tự)                   | Header 14+ bytes (= 1 dòng text)           |
| **3. Khi mất mạng**                | Broker giữ tin nhắn, online lại sẽ nhận      | Mất kết nối = mất tin nhắn luôn            |
| **4. Độ tin cậy**                  | 3 cấp độ gửi thư (thường/bảo đảm/khẩn)       | Tự lo lấy                                  |
| **5. "Di chúc" kỹ thuật số (LWT)** | Sensor chết = tự báo "tôi đã offline"        | Im lặng là vàng (không biết chết hay sống) |
| **6. Phân phối thông minh**        | Broker tự biết gửi cho ai quan tâm           | Code thủ công mọi thứ                      |

### Khi nào dùng cái gì?

**MQTT - Khi bạn cần:**

- 100 sensor nhiệt độ báo về 1 app
- Điện thoại nhận thông báo từ 10 camera
- Thiết bị chạy pin 1 năm
- Mạng yếu, hay mất kết nối
- Nhà máy với 1000 máy móc

**WebSocket - Khi bạn cần:**

- Game online cần phản hồi nhanh
- Chat app như Messenger
- Biểu đồ chứng khoán real-time
- Chỉ cần web browser
- Giao tiếp 1-1 đơn giản

## Code mẫu siêu đơn giản

### MQTT - Sensor gửi nhiệt độ

```python
# Sensor gửi nhiệt độ (3 dòng code!)
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("broker.hivemq.com", 1883)  # Kết nối broker miễn phí
client.publish("home/temperature", "25.5")  # Gửi nhiệt độ

# App nhận nhiệt độ
def on_message(client, userdata, message):
    print(f"Nhiệt độ: {message.payload.decode()}°C")

client.on_message = on_message
client.subscribe("home/+/temperature")  # + = mọi phòng
client.loop_forever()  # Chờ tin nhắn
```

### WebSocket - Chat 1-1

```python
# Client chat đơn giản
import websocket

def on_message(ws, message):
    print(f"Bạn: {message}")

def on_open(ws):
    ws.send("Xin chào!")  # Gửi tin nhắn

# Kết nối và chat
ws = websocket.WebSocketApp("ws://localhost:8080",
                          on_open=on_open,
                          on_message=on_message)
ws.run_forever()  # Giữ kết nối
```

💡 **Chú ý**: WebSocket cần bạn tự code server, MQTT có sẵn broker miễn phí!

## Tóm lại trong 30 giây

**MQTT**

- Sinh ra cho IoT: nhẹ, tiết kiệm pin, mạng yếu OK
- Pub/Sub: 1 gửi, 100 nhận
- Có sẵn broker miễn phí
- Perfect cho: Smart home, sensor, monitoring

**WebSocket**

- Sinh ra cho web: nhanh, real-time
- 1-1 connection: Chat, game
- Tự code server
- Perfect cho: Web app, game online

**Nguyên tắc vàng**:

- Nhiều thiết bị + ít dữ liệu = MQTT
- Ít thiết bị + nhiều tương tác = WebSocket
