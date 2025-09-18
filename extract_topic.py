# extract_topic.py
# ===== 聊天主題的設定 ===== 

from mongo import history_collection

"""
使用者聊天前會在圖文選單選擇聊天主題(有10種)
所以後面所有的對話都會記錄為該主題並且儲存至資料庫
故每次使用者輸入文字，都要判斷一次他是否更換主題
若沒有更換，則沿用上一句話的主題
如果資料庫為空，沒有歷史對話，就將主題先記錄為"其他"
"""

def extract_topic(user_input: str, user_id: str) -> str:
    VALID_TOPICS = [
        "人際關係",
        "家庭關係",
        "情愛關係",
        "生涯",
        "課業學習",
        "自我探索與認識",
        "情緒困擾調適",
        "精神疾病",
        "性議題",
        "其他"
    ]

    # 1. 若是「我想聊聊xxx」且 xxx 是主題之一
    if user_input.startswith("我想聊聊"):
        topic_candidate = user_input.replace("我想聊聊", "").strip()
        if topic_candidate in VALID_TOPICS:
            return topic_candidate

    # 2. 從資料庫找 user_id 的最近有 topic 的紀錄
    recent_history = history_collection.find(
        {"user_id": user_id, "topic": {"$in": VALID_TOPICS}}
    ).sort("timestamp", -1).limit(1)

    for h in recent_history:
        return h.get("topic", "其他")

    # 3. 找不到任何符合的紀錄時
    return "其他"

