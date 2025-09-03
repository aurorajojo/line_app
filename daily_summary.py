# daily_summary.py
# 幫上次諮商那天做摘要，存到資料庫

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pymongo import DESCENDING
from mongo import history_collection, summary_collection
from llm import generate_summary_with_llm  
import json
from linebot.v3.messaging import FlexMessage, FlexContainer

def get_weekday_chinese(date: datetime) -> str:
    weekdays = ["(一)", "(二)", "(三)", "(四)", "(五)", "(六)", "(日)"]
    return weekdays[date.weekday()]  # weekday() 0=Monday
    
def now_taiwan() -> datetime:
    """取得現在的台灣時間（直接 +8 小時，不帶 tzinfo）"""
    return datetime.now() + timedelta(hours=8)

# 檢查上次對話是否需要做摘要
def check_and_summarize(user_id):

    # 取得該使用者最後一筆對話
    last_doc = history_collection.find_one(
        {"user_id": user_id},
        sort=[("timestamp", DESCENDING)]
    )

    today = now_taiwan().date()

    if last_doc:
        # 最後一筆對話的日期（台灣時間）
        last_date = last_doc["timestamp"].date()

        # 如果最後一次對話不是今天
        if last_date < today:

            # 將日期轉成完整 datetime 範圍
            day_start = datetime.combine(last_date, datetime.min.time())
            day_end = datetime.combine(last_date, datetime.max.time())

            # 檢查該日期是否已有摘要
            doc = list(summary_collection.find({
                "user_id": user_id,
                "date": {"$gte": day_start, "$lte": day_end}   # 用範圍查詢
            }))

            if not doc:

                # 統整要摘要的對話
                summary_doc = list(history_collection.find({
                    "user_id": user_id,
                    "timestamp": {"$gte": day_start, "$lte": day_end}   # 用範圍查詢
                }))

                # 產生摘要（呼叫 LLM）
                summary_text, messages = generate_summary_with_llm(summary_doc)

                # 存進資料庫
                summary_collection.insert_one({
                    "user_id": user_id,
                    "date":day_start,
                    "messages":messages,
                    "summary": summary_text,
                    "created_at": now_taiwan()
                })

    else:
        print("尚無對話紀錄")

# 滿十筆對話會呼叫此函式，開始做摘要
def summarize(user_id):

    # 取得該使用者最後一筆對話
    last_doc = history_collection.find_one(
        {"user_id": user_id},
        sort=[("timestamp", DESCENDING)]
    )

    if last_doc:
        # 最後一筆對話的日期（台灣時間）
        last_date = last_doc["timestamp"].date()

        # 當日範圍
        day_start = datetime.combine(last_date, datetime.min.time())
        day_end = datetime.combine(last_date, datetime.max.time())

        # 檢查當天對話數量
        msg_count = history_collection.count_documents({
            "user_id": user_id,
            "timestamp": {"$gte": day_start, "$lte": day_end},
            "prompt": {"$ne": ""}   # 過濾掉選主題的紀錄
        })

        # 只有等於 10 筆才做摘要
        if msg_count == 10:
            # 檢查該日期是否已有摘要
            doc = list(summary_collection.find({
                "user_id": user_id,
                "date": {"$gte": day_start, "$lte": day_end}
            }))

            if not doc:
                # 統整要摘要的對話
                summary_doc = list(history_collection.find({
                    "user_id": user_id,
                    "timestamp": {"$gte": day_start, "$lte": day_end}
                }))

                # 產生摘要（呼叫 LLM）
                summary_text, messages = generate_summary_with_llm(summary_doc)

                # 存進資料庫
                summary_collection.insert_one({
                    "user_id": user_id,
                    "date": day_start,
                    "messages": messages,
                    "summary": summary_text,
                    "created_at": now_taiwan()
                })
    else:
        print("尚無對話紀錄")

def generate_summary(user_id: str) -> FlexMessage:
    """
    產生一個 FlexMessage，包含本日的摘要
    """
    summarize(user_id)          # 其實理論上已經有摘要，確保一下再呼叫一次，如果已經有摘要不會再重複做
    
    bubbles = []

    # 從 MongoDB 找該日期的摘要
    summary_doc = summary_collection.find_one(
        {"user_id": user_id},
        sort=[("date", -1)]  # 按照日期排序，取最新
    )

    day = summary_doc["date"].date()
    date_str = day.strftime("%Y-%m-%d") + " " + get_weekday_chinese(day)

    if summary_doc and "summary" in summary_doc:
        summary_text = summary_doc["summary"]
        date_color = "#000000"  # 黑色（有資料）
    else:
        summary_text = "尚無摘要"
        date_color = "#888888"  # 灰色（沒資料）
    # 先加上「結束提醒」的 bubble
    intro_bubble = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "今天先聊到這裡，我們先花一點時間整理剛剛的想法。\n明天再來聊聊喔！",
                    "weight": "bold",
                    "size": "lg",
                    "color": "#333333",
                    "wrap": True
                },
                {
                    "type": "separator",
                    "margin": "md"
                },
                {
                    "type": "image",
                    "url": "https://img.icons8.com/?size=100&id=g2lLuoxKnKbA&format=png&color=000000"
                },
                {
                    "type": "text",
                    "text": "以下是今日談話的摘要",
                    "size": "md",
                    "color": "#000000",
                    "wrap": True
                }
            ]
        }
    }
    bubbles.append(intro_bubble)

    # 每一天做成一個 bubble
    summary_bubble  = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#E5F9FF" ,
            "contents": [
                {
                    "type": "text",
                    "text": f"{date_str}",
                    "weight": "bold",
                    "size": "lg",
                    "color": date_color
                },
                {
                    "type": "text",
                    "text": summary_text,
                    "wrap": True,
                    "size": "sm",
                    "margin": "md",
                    "color": "#555555"
                }
            ]
        }
    }
    bubbles.append(summary_bubble )
  

    # Carousel 裝一個 bubble
    flex_content = {
        "type": "carousel",
        "contents": bubbles  
    }

    return FlexMessage(
        altText="最新摘要",
        contents=FlexContainer.from_json(json.dumps(flex_content))  # 🚀 dict 轉成 FlexContainer
    )