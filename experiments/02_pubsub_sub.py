
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
print("Chờ messages... (Ctrl+C để dừng)\n")

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
    print("\nSubscriber stopped.")
    pubsub.unsubscribe()
