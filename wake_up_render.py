import threading
import time
import requests
import os

# 定時喚醒 Render 用的函式
def wake_up_render():
    def ping():
        while True:
            try:
                url = os.environ.get("RENDER_PING_URL", "https://你的-render-url.onrender.com")  # 替換為你自己的 URL
                res = requests.get(url)
                if res.status_code == 200:
                    print("[Render 喚醒成功]")
                else:
                    print(f"[Render 喚醒失敗] 狀態碼: {res.status_code}")
            except Exception as e:
                print(f"[Render 喚醒錯誤] {e}")
            time.sleep(14 * 60)  # 每 14 分鐘喚醒一次

    threading.Thread(target=ping, daemon=True).start()