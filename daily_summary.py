# daily_summary.py
# 幫上次諮商那天做摘要，存到資料庫

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pymongo import DESCENDING
from mongo import history_collection, summary_collection
from llm import generate_summary_with_llm  

def now_taiwan() -> datetime:
    """取得現在的台灣時間（直接 +8 小時，不帶 tzinfo）"""
    return datetime.now() + timedelta(hours=8)

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
            # 檢查該日期是否已有摘要
            summary_doc = summary_collection.find_one({
                "user_id": user_id,
                "date": last_date
            })

            if not summary_doc:
                # 撈出那天的所有對話
                day_start = datetime.combine(last_date, datetime.min.time(), tzinfo=TAIPEI_TZ)
                day_end = datetime.combine(last_date, datetime.max.time(), tzinfo=TAIPEI_TZ)

                chats = list(history_collection.find({
                    "user_id": user_id,
                    "timestamp": {"$gte": day_start, "$lte": day_end}
                }))

                if chats:
                    # 產生摘要（呼叫 LLM）
                    summary_text = generate_summary_with_llm(chats)

                    # 存進資料庫
                    summary_collection.insert_one({
                        "user_id": user_id,
                        "date": last_date,
                        "summary": summary_text,
                        "created_at": now_taiwan()
                    })
    else:
        print("尚無對話紀錄")
