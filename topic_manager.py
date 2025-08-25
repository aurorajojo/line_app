# topic_manager.py
# ==================================================
# 管理每天使用者的聊天主題
# - 使用者必須先輸入「我想聊聊XXX」才算選主題
# - 主題必須在 VALID_TOPICS 裡
# - 每天午夜自動清空，隔天重新要求主題
# ==================================================

from daily_summary import check_and_summarize
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from mongo import summary_collection
from linebot.v3.messaging import FlexMessage, FlexContainer
import json


# === 可選主題清單 ===
VALID_TOPICS = [
    "情緒困擾",
    "人際關係",
    "課業壓力",
    "生涯迷茫",
    "校園適應",
    "自我價值",
    "其他"
]


def check_and_set_topic(user_id, user_input):
    """
    功能：檢查使用者輸入是否為合法的主題，若合法則存起來
    規則：
      1. 格式必須是「我想聊聊XXX」
      2. XXX 必須在 VALID_TOPICS 內
    回傳：
      - ("success", topic)         -> 主題設定成功
      - ("invalid_format", None)   -> 格式錯誤（不是以「我想聊聊」開頭）
      - ("invalid_topic", None)    -> 主題不在選項內
    """

    check_and_summarize(user_id)          # 幫上次諮商那天做摘要

    if not user_input.startswith("我想聊聊"):
        return "invalid_format", None

    topic_candidate = user_input.replace("我想聊聊", "").strip()
    if topic_candidate in VALID_TOPICS:
        return "success", topic_candidate
    else:
        return "invalid_topic", None

def has_topic(user_id):
    """
    檢查使用者今天是否已經設定過主題（以 '我想聊聊' 開頭）
    回傳：True / False
    """
    # 取得台灣時間今天的起始與結束
    now = datetime.now() + timedelta(hours=8)
    today = now.date()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    # 查詢今天該 user 是否有輸入 "我想聊聊..." 開頭的內容
    exists = summary_collection.find_one({
        "user_id": user_id,
        "timestamp": {"$gte": start_of_day, "$lte": end_of_day},
        "user_input": {"$regex": "^我想聊聊(" + "|".join(VALID_TOPICS) + ")$"}
    })

    return exists is not None

def get_json(topic: str):
    bubble_json = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "💬 主題已設定！",
                    "weight": "bold",
                    "size": "xl",
                    "color": "#424242"
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "spacing": "sm",
                    "margin": "md",
                    "contents": [
                        {
                            "type": "icon",
                            "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                        },
                        {
                            "type": "text",
                            "text": topic,
                            "size": "lg",
                            "color": "#616161"
                        }
                    ]
                },
                {
                    "type": "text",
                    "text": "我們可以開始聊天囉 ✨\n很高興能陪你聊聊，放輕鬆，想說什麼都可以\n點擊左下角打開鍵盤開始輸入吧～",
                    "wrap": True,
                    "margin": "md",
                    "color": "#212121"
                }
            ]
        }
    }
    return FlexMessage(alt_text="主題已設定", contents=FlexContainer.from_json(json.dumps(bubble_json)))

