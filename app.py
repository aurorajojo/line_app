# app.py
# ===== Flask 主程式入口點，負責啟動伺服器與接收 LINE Webhook =====

from flask import Flask, request, abort
from linebot.v3.exceptions import InvalidSignatureError
from line_handlers import handler  # 自訂的事件處理模組
from wake_up_render import wake_up_render

app = Flask(__name__)

# 測試是否運作正常的路由
@app.route("/", methods=["GET"])
def home():
    return {"message": "LINE Bot is running."}

# 接收 LINE Webhook 訊息的路由
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")  # 驗證用簽章
    body = request.get_data(as_text=True)  # 傳入的 JSON 文字內容

    try:
        handler.handle(body, signature)  # 使用 LINE SDK 驗證與處理事件
    except InvalidSignatureError:
        abort(400)  # 驗證失敗，回傳錯誤

    return "OK"


wake_up_render()  # 啟動定時喚醒

if __name__ == "__main__":
    app.run(port=5000)  # 啟動 Flask 本地伺服器

