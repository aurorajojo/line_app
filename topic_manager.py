# topic_manager.py
# ==================================================
# 管理每天使用者的聊天主題
# - 使用者必須先輸入「我想聊聊XXX」才算選主題
# - 主題必須在 VALID_TOPICS 裡
# - 每天午夜自動清空，隔天重新要求主題
# ==================================================

from datetime import datetime, timedelta
from linebot.v3.messaging import FlexMessage, FlexContainer
import threading

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

# === 存放今天已經選主題的使用者 ===
# 結構：{ user_id: topic }
# 範例：{ "U12345": "情緒困擾" }
users_with_topic_today = {}

def reset_users_with_topic():
    """
    功能：每天午夜清空使用者的主題紀錄
    流程：
      1. 把 users_with_topic_today 清空
      2. 計算下一次午夜的時間
      3. 安排自己在下次午夜再執行
    """
    global users_with_topic_today
    users_with_topic_today.clear()
    print("✅ 已清空今日主題使用者列表")

    # 計算下一次午夜的時間（明天 00:00）
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    next_midnight = datetime.combine(tomorrow.date(), datetime.min.time())
    seconds_until_midnight = (next_midnight - now).total_seconds()

    # 設定排程，等到午夜再執行
    threading.Timer(seconds_until_midnight, reset_users_with_topic).start()

def init_topic_manager():
    """
    功能：在程式啟動時，安排第一次的「午夜清空」
    """
    now = datetime.now()
    next_midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
    seconds_until_midnight = (next_midnight - now).total_seconds()

    # 等到午夜再執行 reset
    threading.Timer(seconds_until_midnight, reset_users_with_topic).start()
    print("✅ 主題管理器已啟動，將在午夜自動清空")

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
    if not user_input.startswith("我想聊聊"):
        return "invalid_format", None

    topic_candidate = user_input.replace("我想聊聊", "").strip()
    if topic_candidate in VALID_TOPICS:
        users_with_topic_today[user_id] = topic_candidate
        return "success", topic_candidate
    else:
        return "invalid_topic", None

def has_topic(user_id):
    """
    檢查使用者今天是否已經設定過主題
    回傳：True / False
    """
    return user_id in users_with_topic_today

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
                    "text": "我們可以開始聊天囉 ✨",
                    "wrap": True,
                    "margin": "md",
                    "color": "#212121"
                }
            ]
        }
    }
    return FlexMessage(alt_text="主題已設定", contents=bubble_json)

