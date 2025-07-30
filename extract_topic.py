# extract_topic.py

from mongo import history_collection

def extract_topic(user_input: str, user_id: str) -> str:
    VALID_TOPICS = [
        "情緒困擾",
        "人際關係",
        "課業壓力",
        "生涯迷茫",
        "校園適應",
        "自我價值",
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

