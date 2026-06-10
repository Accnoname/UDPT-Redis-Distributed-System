"""
Ngày 2 - Pub/Sub: Giao tiếp phân tán không đồng bộ
=====================================================
Mục tiêu: Hiểu pattern Publish/Subscribe — cách các service
          giao tiếp mà không cần biết nhau.

Cách chạy:
  Terminal 1: python experiments/02_pubsub_sub.py
  Terminal 2: python experiments/02_pubsub_pub.py
  (Chạy subscriber TRƯỚC, sau đó mới chạy publisher)
"""

# ─── FILE NÀY LÀ PUBLISHER ───────────────────────────────────────
# Lưu file subscriber riêng bên dưới (copy thủ công)

import redis
import time
import random
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

print("=" * 50)
print("  PUBLISHER — Đang gửi tin nhắn...")
print("=" * 50)
print("(Subscriber phải chạy trước ở terminal khác)\n")

# Mô phỏng hệ thống microservices
# Service A (order-service) thông báo cho các service khác

events = [
    {"channel": "orders",    "event": "ORDER_CREATED",   "data": {"id": "ORD-001", "amount": 500000}},
    {"channel": "inventory", "event": "STOCK_UPDATED",   "data": {"product": "iPhone", "qty": -1}},
    {"channel": "orders",    "event": "ORDER_PAID",      "data": {"id": "ORD-001", "method": "VNPay"}},
    {"channel": "notifications", "event": "EMAIL_SEND", "data": {"to": "user@email.com", "template": "order_confirmed"}},
    {"channel": "analytics", "event": "PURCHASE_EVENT", "data": {"user": "user123", "revenue": 500000}},
    {"channel": "orders",    "event": "ORDER_SHIPPED",   "data": {"id": "ORD-001", "tracking": "VN123456"}},
]

for event in events:
    message = json.dumps({
        "event": event["event"],
        "data": event["data"],
        "timestamp": time.time(),
        "service": "order-service"  # Người gửi
    })
    
    # Publish và đếm số subscriber nhận được
    num_subscribers = r.publish(event["channel"], message)
    print(f"📤 [{event['channel']}] {event['event']}")
    print(f"   Data: {event['data']}")
    print(f"   Đã gửi đến {num_subscribers} subscriber(s)\n")
    
    time.sleep(1.5)

print("✅ Publisher done!")


# ─────────────────────────────────────────────────────────────────
# SUBSCRIBER CODE (lưu thành file riêng: 02_pubsub_sub.py)
# ─────────────────────────────────────────────────────────────────
SUBSCRIBER_CODE = '''
"""
Ngày 2 - Pub/Sub Subscriber
Chạy file này TRƯỚC ở một terminal riêng!
  python experiments/02_pubsub_sub.py
"""
import redis
import json
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
pubsub = r.pubsub()

# Subscribe vào nhiều channel — giả lập notification-service
channels = ["orders", "notifications"]
pubsub.subscribe(*channels)

print("=" * 50)
print("  SUBSCRIBER (notification-service)")
print(f"  Listening on: {channels}")
print("=" * 50)
print("Chờ messages... (Ctrl+C để dừng)\\n")

try:
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            channel = message['channel']
            
            print(f"📥 [{channel}] {data['event']}")
            print(f"   From: {data['service']}")
            print(f"   Data: {data['data']}")
            print()
            
            # Xử lý theo loại event
            if data['event'] == 'ORDER_CREATED':
                print("   → Gửi email xác nhận đơn hàng...")
            elif data['event'] == 'ORDER_PAID':
                print("   → Gửi SMS thanh toán thành công...")
            elif data['event'] == 'EMAIL_SEND':
                print(f"   → Sending email to {data['data']['to']}...")
            print()
            
except KeyboardInterrupt:
    print("\\nSubscriber stopped.")
    pubsub.unsubscribe()
'''

# Ghi file subscriber
import os
sub_path = os.path.join(os.path.dirname(__file__), '02_pubsub_sub.py')
with open(sub_path, 'w', encoding='utf-8') as f:
    f.write(SUBSCRIBER_CODE)
print(f"\n📄 Đã tạo file subscriber: {sub_path}")
print("\n💡 Cách chạy:")
print("   Terminal 1: python experiments/02_pubsub_sub.py")
print("   Terminal 2: python experiments/02_pubsub_pub.py")
