# -*- coding: utf-8 -*-
import subprocess
import sys
import time
import os

def main():
    port = 8002
    print("=" * 60)
    print("🚀 KHỞI ĐỘNG DASHBOARD HÀNG ĐỢI PHÂN TÁN (TASK QUEUE)")
    print("=" * 60)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    env = os.environ.copy()
    env["PORT"] = str(port)
    env["PYTHONIOENCODING"] = "utf-8"
    
    cmd = [
        sys.executable, "-m", "uvicorn", "app:app", 
        "--host", "0.0.0.0", 
        "--port", str(port),
        "--log-level", "warning"
    ]
    
    print(f"  → Khởi động Dashboard Server tại port {port}...")
    p = subprocess.Popen(
        cmd, 
        cwd=current_dir, 
        env=env
    )
    
    time.sleep(1.0)
    print("\n✅ Dashboard đã sẵn sàng!")
    print(f"🔗 Địa chỉ Dashboard UI: http://localhost:{port}")
    print("\n💡 Cách chạy các Worker để nhận job và xử lý:")
    print("   Mở các Terminal mới và chạy:")
    print("   → Terminal 1: python feature2_task_queue/worker.py worker-A")
    print("   → Terminal 2: python feature2_task_queue/worker.py worker-B")
    print("   → Terminal 3: python feature2_task_queue/worker.py worker-C")
    print("\n🛑 Bấm Ctrl+C tại đây để tắt Dashboard Server.")
    print("=" * 60)

    try:
        while True:
            if p.poll() is not None:
                print("⚠️  Dashboard Server đã dừng!")
                break
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n   Đang dừng Dashboard Server...")
        p.terminate()
        p.wait()
        print("✅ Đã tắt. Hẹn gặp lại!")

if __name__ == "__main__":
    main()
