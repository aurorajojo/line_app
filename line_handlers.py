# line_handlers.py
# ===== 處理所有來自 LINE 的訊息事件（目前只處理文字訊息） =====

from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import ApiClient, Configuration, ShowLoadingAnimationRequest

from config import CHANNEL_SECRET, CHANNEL_ACCESS_TOKEN
from mongo import history_collection
from resources import base_prompt, cycu_resources
from llm import call_groq_llm


from datetime import datetime
import json
import time

# 設定 LINE Handler 與 Configuration
handler = WebhookHandler(CHANNEL_SECRET)
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

# 註冊 LINE 訊息處理器
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text(event):
    user_input = event.message.text.strip()  # 使用者輸入文字
    user_id = event.source.user_id           # 使用者的 LINE ID

    # === 查詢資源地點（比對關鍵字）===
    found_location = None
    for category, items in cycu_resources.get("中原大學資源", {}).items():
        for name, info in items.items():
            if name in user_input and "地點" in info:
                found_location = f"{name}的地點是：{info['地點']}" if info["地點"] else f"{name}沒有地點資料喔！"
                break

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.show_loading_animation(  #延遲動畫
            ShowLoadingAnimationRequest(
                chatId = user_id,
                loadingSeconds=5
            )
        )

        # 回覆地點查詢
        if found_location:
            line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=found_location)])
            )
            return

        # === 查詢歷史對話，建立上下文 ===
        history = list(history_collection.find({"user_id": user_id}).sort("timestamp", -1).limit(10))
        history.reverse()  # 由舊至新

        # 建立對話上下文（system + 歷史）
        messages = [
            {"role": "system", "content": base_prompt + f"可參考用途索引：{json.dumps(cycu_resources.get('用途索引', {}), ensure_ascii=False)}"}
        ]
        for h in history:
            if "user_input" in h:
                messages.append({"role": "user", "content": h["user_input"]})
            if "reply" in h:
                messages.append({"role": "assistant", "content": h["reply"]})
        messages.append({"role": "user", "content": user_input})

        # === 呼叫 LLM 產生回覆 ===
        reply = call_groq_llm(messages)


        # === 儲存對話紀錄進 MongoDB ===
        history_collection.insert_one({
            "user_id": user_id,
            "user_input": user_input,
            "reply": reply,
            "timestamp": datetime.now()
        })
        
        # === 回覆使用者 ===
        line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=reply)])
        )
