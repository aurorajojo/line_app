# emotion_dashboard.py
# ===== 情緒儀表板的生成 ===== 

from datetime import datetime
from collections import Counter
from mongo import history_collection

"""
根據使用者的歷史對話紀錄，產生情緒儀表板，分析使用者的情緒組成
為了讓情緒分析結果更有親和力，我們替每一種情緒設計了一個對應角色
範例如下:

🧠 情緒儀表板
──────────
📅 日期：2025-07-30
🎯 主要情緒：悲傷（43%）→ 🐟 小魚淚淚
📊 情緒血條：
🐟 小魚淚淚  ■■■■□□□□□□ (43%)
🐇 小兔子焦焦  ■□□□□□□□□□ (14%)
🦊 小狐狸羞羞  ■□□□□□□□□□ (14%)
🦔 小刺蝟皮皮  ■□□□□□□□□□ (14%)
☁️ 神秘雲雲  ■□□□□□□□□□ (14%)

"""

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
        emo = doc.get("emotion_tag", "").strip()   # 統計情緒
        if emo and emo != "無法判斷":
            emotion_counter[emo] += 1

    if not emotion_counter:  # 情緒都是無法判斷，不生成情緒儀表板
        return "沒有明確的情緒標記，無法產生儀表板。"

    sorted_emotions = emotion_counter.most_common()       # 找最常出現的情緒
    total = sum(emotion_counter.values())                 # 計算對話次數
    main_emotion, main_count = sorted_emotions[0]          # 紀錄最常出現的情緒
    character = EMOTION_CHARACTERS.get(main_emotion, "❓") # 最常出現的情緒對應的角色
    percent = round(main_count / total * 100)               # 計算最常出現情緒的占比

    # 取最新一筆資料的日期
    latest = sorted(user_data, key=lambda d: d.get("timestamp", datetime.min))[-1]
    latest_date = latest["timestamp"].strftime("%Y-%m-%d") if "timestamp" in latest else "未知"

    lines = [
        "🧠 情緒儀表板",
        "─" * 10,                                                 # 分隔線
        f"📅 日期：{latest_date}",                                # 最新一筆資料的日期
        f"🎯 主要情緒：{main_emotion}（{percent}%）→ {character}", # 最常出現的情緒與其占比(以數字顯示)
        "📊 情緒血條："                                            # 顯示各個曾經出現的情緒其占比(以血條顯示)
    ]
    for emo, count in sorted_emotions:
        p = round(count / total * 100)
        lines.append(f"{EMOTION_CHARACTERS.get(emo, '?')}\t {bar(p)} ({p}%)")

    return "\n".join(lines)

def bar(percent):     # 情緒血條
    length = int(percent / 10)
    return "■" * length + "□" * (10 - length)
