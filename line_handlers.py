# line_handlers.py
# ===== 處理所有來自 LINE 的訊息事件（目前只處理文字訊息） =====

from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import ApiClient, Configuration, ShowLoadingAnimationRequest, FlexMessage

from config import CHANNEL_SECRET, CHANNEL_ACCESS_TOKEN
from mongo import history_collection
from resources import base_prompt, cycu_resources
from llm import call_groq_llm
from depression_scale import start_depression_test, handle_depression_response, user_state
from emotion_strategy_utils import extract_emotion_from_reply, extract_strategies
from emotion_dashboard import generate_text_dashboard
from gaming_disorder_scale import start_gaming_test, handle_gaming_response
from gaming_disorder_scale import user_state as user_state1
from extract_topic import extract_topic
from vector_search import query_vectorstore

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import torch
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

    # 使用 ApiClient 進行 API 呼叫，確保自動開關連線
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.show_loading_animation(  #延遲動畫
            ShowLoadingAnimationRequest(
                chatId = user_id,
                loadingSeconds=5     # 動畫持續秒數
            )
        )

        # === 防呆判斷：輸入 0,1,2,3 或 結束測驗，卻尚未開始量表 ===
        if user_input in ["0", "1", "2", "3", "結束測驗"]:
            if user_id not in user_state and user_id not in user_state1:
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token, messages=[TextMessage(text="看起來您想回答量表的問題喔～請先從圖文選單中選擇想進行的量表，才能開始施測喔！")]
                    )
                )
                return

        # === 情緒分析 ===
        if user_input == "我要看情緒分析":
            dashboard_text = generate_text_dashboard(user_id)
            line_bot_api.reply_message(       # 回傳情緒儀表板
                ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=dashboard_text)] )
            )
            return
        
        # === 憂鬱量表 ===
        elif user_input == "我要做憂鬱症量表":
            bubble = start_depression_test(user_id)
            line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=event.reply_token, messages=[bubble])   # 顯示量表 FlexMessage 按鈕
            )
            return

        # === 遊戲成癮量表 ===
        elif user_input == "我要做遊戲成癮量表":
            bubble = start_gaming_test(user_id)
            line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=event.reply_token, messages=[bubble])   # 顯示量表 FlexMessage 按鈕
            )
            return     
        
        # === 處理作答 ===
        result, response = handle_depression_response(user_id, user_input)
        if result is not None:
            if result == "next":      # 下一題 FlexMessage 按鈕
                line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[response])
                )
            elif result == "end":     # 結束測驗
                line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=response)])
                )
            elif result == "invalid": # 非預期輸入，回覆提醒文字
                line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=response)])
                )
            return 
        
        # === 處理遊戲量表作答 ===
        result, response = handle_gaming_response(user_id, user_input)
        if result is not None:
            if result == "next":      # 下一題 FlexMessage 按鈕
                line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[response])
                )
            elif result == "end":     # 結束測驗
                line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=response)])
                )
            elif result == "invalid": # 非預期輸入，回覆提醒文字
                line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=response)])
                )
            return

        is_similar, content, score = query_vectorstore(user_input)

        if is_similar:
            content = base_prompt + f"以下是與您問題最相關的資訊，供您參考：\n{content}"
        else:
            content = base_prompt + f"可參考用途索引：{content}"


        # === 查詢歷史對話，建立上下文 ===
        history = list(history_collection.find({"user_id": user_id}).sort("timestamp", -1).limit(5))
        history.reverse()  # 由舊至新
        messages = [{"role": "system", "content": content}]

   
        # 將歷史對話依序加入 messages，供 LLM 建立上下文
        for h in history:
            if "user_input" in h:
                messages.append({"role": "user", "content": h["user_input"]})
            if "reply" in h:
                messages.append({"role": "assistant", "content": h["reply"]})

        # 最新使用者輸入也加入上下文末端
        messages.append({"role": "user", "content": user_input})

        # === 呼叫 LLM 產生回覆 ===
        reply = call_groq_llm(messages)


        # === 儲存對話紀錄進 MongoDB ===
        emotion_tag = extract_emotion_from_reply(reply)  # 找情緒
        strategy_tags = extract_strategies(reply)        # 找策略
        topic_tags = extract_topic(user_input, user_id)  # 找主題

        history_collection.insert_one({
            "user_id": user_id,           # 使用者id
            "prompt": messages,           # token
            "user_input": user_input,     # 使用者輸入
            "reply": reply,               # llm回覆
            "emotion_tag": emotion_tag,   # 情緒
            "strategy": strategy_tags,    # 策略
            "topic": topic_tags,          # 主題
            "timestamp": datetime.now()   # 時間
        })
        
        # === 回覆使用者 ===
        line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=reply)])
        )
