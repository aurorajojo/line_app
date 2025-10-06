# line_handlers.py
# ===== 處理所有來自 LINE 的訊息事件（目前只處理文字訊息） =====

from linebot.v3.webhooks import MessageEvent, TextMessageContent, PostbackEvent
from linebot.v3.messaging import MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import ApiClient, Configuration, ShowLoadingAnimationRequest, FlexMessage,TextMessage, QuickReply, QuickReplyItem, DatetimePickerAction

from config import CHANNEL_SECRET, CHANNEL_ACCESS_TOKEN
from mongo import history_collection, summary_collection
from resources import base_prompt, cycu_resources
from llm import call_groq_llm
from depression_scale import start_depression_test, handle_depression_response, user_state
from emotion_strategy_utils import extract_emotion_from_reply, extract_strategies, extract_intentions
from emotion_dashboard import generate_text_dashboard
from gaming_disorder_scale import start_gaming_test, handle_gaming_response
from gaming_disorder_scale import user_state as user_state1, get_history
from extract_topic import extract_topic
from vector_search import query_vectorstore
from topic_manager import (
    check_and_set_topic,
    has_topic,
    get_json,
    VALID_TOPICS
)
from weekly_summary import generate_weekly_summary, get_summary_by_date,get_daily_conversation_bubbles
from daily_summary import summarize, generate_summary
from event_utils import load_upcoming_events, events_to_flex

from datetime import datetime
import re
from datetime import datetime, timedelta

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
                loadingSeconds=10     # 動畫持續秒數
            )
        )

        # === 查詢活動 ===
        if user_input == "我要找活動":
            events = load_upcoming_events()
            if not events:
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="目前沒有即將到來的活動喔～")]
                    )
                )
            else:
                flex = events_to_flex(events)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[flex]
                    )
                )
            return
        
        # === 查看指定日期的完整對話 ===
        match = re.match(r"我要看(\d{4}-\d{2}-\d{2})\s*\(.+\)\s*對話", user_input)
        if match:
            chosen_date = match.group(1)
            bubbles = get_daily_conversation_bubbles(user_id, chosen_date)

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token, messages=[bubbles]
                )
            )
            return          
          
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
                ReplyMessageRequest(reply_token=event.reply_token, messages=[dashboard_text] )
            )
            return
        
        # === 憂鬱量表 ===
        elif user_input == "我要做憂鬱症量表":
            if user_id in user_state or user_id in user_state1:  # 防呆機制，避免一次施測多重量表
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token, messages=[TextMessage(text="請先完成當前量表才能開始施測其他量表喔！")]
                    )
                )
                return
            bubble = start_depression_test(user_id)
            line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=event.reply_token, messages=[bubble])   # 顯示量表 FlexMessage 按鈕
            )
            return

        # === 遊戲成癮量表 ===
        elif user_input == "我要做遊戲成癮量表":
            if user_id in user_state or user_id in user_state1:  # 防呆機制，避免一次施測多重量表
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token, messages=[TextMessage(text="請先完成當前量表才能開始施測其他量表喔！")]
                    )
                )
                return
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
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[response])
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
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[response])
                )
            elif result == "invalid": # 非預期輸入，回覆提醒文字
                line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=response)])
                )
            return
        
        if user_input == "我要看遊戲成癮量表歷史":
            bubble =  get_history(user_id, "gaming_disorder")

            line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=event.reply_token, messages=[bubble])   # 顯示遊戲成癮量表歷史
            )
            return 
        
        if user_input == "我要看憂鬱症量表歷史":
            bubble =  get_history(user_id, "depression")
        
            line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=event.reply_token, messages=[bubble])   # 顯示憂鬱症量表歷史
            )
            return 
        
        # === 查看最近摘要 ===
        if user_input == "我要看摘要":
            flex = generate_weekly_summary(user_id)
            line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=event.reply_token, messages=[flex])
            )            

            return
        
        # === 查詢摘要 ===
        if user_input == "查詢摘要":
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(
                            text="請選擇日期",
                            quick_reply=QuickReply(
                                items=[
                                    QuickReplyItem(
                                        action=DatetimePickerAction(
                                            label="選擇日期",
                                            data="chosen_date",
                                            mode="date"  #  e.g. 2025-08-28
                                        )
                                    )
                                ]
                            )
                        )
                    ]
                )
            )
            return

        # === 每日訊息限制 ===
        start_of_day = (datetime.now()+ timedelta(hours=8)).replace(hour=0, minute=0, second=0, microsecond=0)
        msg_count = history_collection.count_documents({
            "user_id": user_id,
            "timestamp": {"$gte": start_of_day},
            "prompt": {"$ne": ""}   # 過濾掉選主題的紀錄
        })

        if msg_count >= 10:                       # 達到 10 則訊息的上限，輸出結束提醒 + 今日摘要
            bubble = generate_summary(user_id)

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,messages=[bubble]
                )
            )
            return    

        if len(user_input) > 128:   # 限制字數在128字，以免使用token太多

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="抱歉，輸入文字不能超過 125 個字，請縮短文字再試一次喔～")]
                )
            )
            return  # 超過限制就不繼續後面的流程
        
        # === 檢查是否要設定主題 === 
        status, topic = check_and_set_topic(user_id, user_input)

        if status == "success":    # 要設定

            line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=event.reply_token, messages=[get_json(topic)])  # 回覆一個 FlexMessage
            )

            # === 儲存對話紀錄進 MongoDB ===
            history_collection.insert_one({
                "user_id": user_id,                                      # 使用者的 LINE ID
                "user_input": user_input,                                # 使用者實際輸入的文字（例：我想聊聊情緒困擾）
                "reply": f"已設定主題：{topic}，我們可以開始聊天囉！",      # 系統回覆的訊息，確認主題已設定
                "topic": topic,                                          # 存入使用者選擇的主題（例：情緒困擾）
                "timestamp": datetime.now()   + timedelta(hours=8)       # 記錄當下時間，方便之後查詢
            })

            return 

        # === 沒有主題 ===
        if not has_topic(user_id):

            if status == "invalid_format":   # 格式錯誤
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="開始聊天之前，請先選擇聊天主題。\n打開主選單點擊開始聊天即可進入選擇聊天主題頁面")]
                    )
                )
            elif status == "invalid_topic":  # 主題錯誤
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="這個主題不在選項內喔！可選主題：" + "、".join(VALID_TOPICS))]
                    )
                )
            return
        
        # === 可供參考的(資源+摘要+指令) or (索引+摘要+指令) ===
        content = query_vectorstore(user_input, user_id )
        content = base_prompt + content
        messages = [{"role": "system", "content": content}]

   
        # === 查詢歷史對話，建立上下文 ===
        history = list(history_collection.find({"user_id": user_id}).sort("timestamp", -1).limit(5))  # 5筆
        history.reverse()  # 由舊至新
        if history:
            history_text = "【歷史】\n"
            for h in history:
                if "user_input" in h:
                    history_text += f"user: {h['user_input']}\n"
                if "reply" in h:
                    history_text += f"system: {h['reply']}\n"
            messages.append({"role": "user", "content": history_text.strip()})

        # === 最新使用者輸入也加入上下文末端 === 
        messages.append({"role": "user", "content": f"【本次】{user_input}"})

        # === 呼叫 LLM 產生回覆 ===
        reply = call_groq_llm(messages)


        # === 儲存對話紀錄進 MongoDB ===
        emotion_tag = extract_emotion_from_reply(reply)           # 找情緒
        strategy_tags = extract_strategies(reply)                 # 找策略
        intention_tag = extract_intentions(reply)                 # 找意圖
        topic_tags = extract_topic(user_input, user_id)           # 找主題
        reply = reply.replace("【本次】", "").strip()              # 有時模型會亂加【本次】這個在最前面，要刪掉
        reply = reply.replace("【歷史】", "").strip()              # 有時模型會亂加【歷史】這個在最前面，要刪掉
        
        history_collection.insert_one({
            "user_id": user_id,                                 # 使用者id
            "prompt": messages,                                 # prompt
            "user_input": user_input,                           # 使用者輸入
            "reply": reply,                                     # llm回覆
            "emotion": emotion_tag,                             # 情緒
            "strategy": strategy_tags,                          # 策略
            "intention": intention_tag,                         # 意圖
            "topic": topic_tags,                                # 主題
            "timestamp": datetime.now()  + timedelta(hours=8)   # 台灣時間  
        })

        # === 把(數字) [數字] {數字} ... 刪掉 === 
        reply = re.sub(r"[\(\[\{]\d+[\)\]\}]", "", reply).strip()
        
        # === 回覆使用者 ===
        line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=reply)])
        )

        # 計算呼叫幾次llm，如果對話滿十筆，就做摘要
        start_of_day = (datetime.now()+ timedelta(hours=8)).replace(hour=0, minute=0, second=0, microsecond=0)
        msg_count = history_collection.count_documents({
            "user_id": user_id,
            "timestamp": {"$gte": start_of_day},
            "prompt": {"$exists": True, "$ne": ""}  # 過濾掉選主題的紀錄
        })      
        
        if msg_count == 10: 
            summarize(user_id)  

@handler.add(PostbackEvent)
def handle_postback(event):     # 使用者用日期選擇器，查詢特定日子摘要
    user_id = event.source.user_id

    # 判斷是不是選日期的 postback
    if event.postback.data == "chosen_date":
        chosen_date = event.postback.params.get("date")
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.show_loading_animation(  #延遲動畫
                ShowLoadingAnimationRequest(
                    chatId = user_id,
                    loadingSeconds=10     # 動畫持續秒數
                )
            )
            flex = get_summary_by_date(user_id, chosen_date)   # 查詢特定日子摘要

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[flex]
                )
            )