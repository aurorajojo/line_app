# emotion_dashboard.py

from collections import Counter
from mongo import history_collection

EMOTION_CHARACTERS = {
    "焦慮": "🐇 小兔子焦焦",
    "悲傷": "🐟 小魚淚淚",
    "憤怒": "🔥 火爆熊熊",
    "恐懼": "🦔 小刺蝟皮皮",
    "厭惡": "🐸 青蛙嘔嘔",
    "羞愧": "🦊 小狐狸羞羞",
    "無法判斷": "🧊 空殼寶寶",
    "其他": "☁️ 神秘雲雲"
}

def generate_text_dashboard(user_id):
    # 從 MongoDB 撈該使用者的紀錄
    user_data = list(history_collection.find({"user_id": user_id}))

    if not user_data:   # 沒對話
        return f"查無對話紀錄，無法產生儀表板。"

    emotion_counter = Counter()
    for doc in user_data:
        emo = doc.get("emotion_tag", "").strip()
        if emo and emo != "無法判斷":
            emotion_counter[emo] += 1

    if not emotion_counter:  # 沒情緒
        return "沒有明確的情緒標記，無法產生儀表板。"

    sorted_emotions = emotion_counter.most_common()
    total = sum(emotion_counter.values())
    main_emotion, main_count = sorted_emotions[0]
    character = EMOTION_CHARACTERS.get(main_emotion, "❓")
    percent = round(main_count / total * 100)

    # 取最新一筆資料的日期
    latest = sorted(user_data, key=lambda d: d.get("timestamp", datetime.min))[-1]
    latest_date = latest["timestamp"].strftime("%Y-%m-%d") if "timestamp" in latest else "未知"

    lines = [
        "🧠 情緒儀表板",
        "─" * 40,
        f"📅 日期：{latest_date}",
        f"🎯 主要情緒：{main_emotion}（{percent}%）→ {character}",
        "📊 情緒血條："
    ]
    for emo, count in sorted_emotions:
        p = round(count / total * 100)
        lines.append(f"{EMOTION_CHARACTERS.get(emo, '?')}\t {bar(p)} ({p}%)")

    return "\n".join(lines)

def bar(percent):
    length = int(percent / 5)
    return "■" * length + "□" * (20 - length)
