# -*- coding: utf-8 -*-
import subprocess
import sys
import time
import os

def main():
    processes = []
    ports = [8001, 8002, 8003]
    
    print("=" * 60)
    print("🚀 KHỞI ĐỘNG 3 SERVER FASTAPI (PHÂN TÁN) CHO RATE LIMITER")
    print("=" * 60)
    
    # Lấy thư mục hiện tại của file run_servers.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    for port in ports:
        env = os.environ.copy()
        env["PORT"] = str(port)
        env["PYTHONIOENCODING"] = "utf-8"
        
        # Chạy uvicorn app:app --port <port>
        cmd = [
            sys.executable, "-m", "uvicorn", "app:app", 
            "--host", "0.0.0.0", 
            "--port", str(port),
            "--log-level", "warning"
        ]
        
        print(f"  → Khởi động Server tại port {port}...")
        p = subprocess.Popen(
            cmd, 
            cwd=current_dir, 
            env=env,
            stdout=subprocess.DEVNULL, # Giảm thiểu rác log ở console
            stderr=subprocess.DEVNULL
        )
        processes.append((port, p))
        time.sleep(0.5)
        
    print("\n✅ Cả 3 server đã được khởi động thành công!")
    print("🔗 Địa chỉ Dashboard UI: http://localhost:8001")
    print("💡 Mẹo: Bạn có thể mở port 8001, 8002, hoặc 8003 đều thấy giao diện giống nhau.")
    print("   Khi bấm gửi request, hệ thống sẽ tự động luân phiên (round-robin) qua cả 3 server.")
    print("🛑 Bấm Ctrl+C để tắt tất cả các server.")
    print("=" * 60)

    try:
        # Giữ script chạy để quản lý các tiến trình con
        while True:
            # Kiểm tra xem có tiến trình nào bị chết đột ngột không
            for port, p in processes:
                if p.poll() is not None:
                    print(f"⚠️  Cảnh báo: Server tại port {port} đã dừng hoạt động!")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n   Đang dừng tất cả các server...")
        for port, p in processes:
            p.terminate()
            p.wait()
        print("✅ Tất cả các server đã được tắt. Hẹn gặp lại!")

if __name__ == "__main__":
    main()
