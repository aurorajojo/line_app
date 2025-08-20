# emotion_dashboard.py
# ===== 情緒儀表板的生成 ===== 

from datetime import datetime
from collections import Counter
from linebot.v3.messaging import FlexMessage, FlexContainer
import json
from mongo import history_collection

"""
根據使用者的歷史對話紀錄，產生情緒儀表板，分析使用者的情緒組成
為了讓情緒分析結果更有親和力，我們替每一種情緒設計了一個對應角色
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

# 不同情緒對應顏色（背景 / 長條）
EMOTION_COLORS = {
    "焦慮": ("#27ACB2", "#0D8186"),
    "悲傷": ("#FF6B6E", "#DE5658"),
    "憤怒": ("#F5A623", "#D97B00"),
    "恐懼": ("#A17DF5", "#7D51E4"),
    "厭惡": ("#9FD8E3", "#0D8186"),
    "羞愧": ("#FAD2A7", "#DE5658"),
    "其他": ("#B0BEC5", "#455A64"),
}

def generate_text_dashboard(user_id):
    user_data = list(history_collection.find({"user_id": user_id}))
    if not user_data:
        return FlexMessage(alt_text="情緒儀表板", contents=FlexContainer.from_json(json.dumps({
            "type": "bubble",
            "body": {"type": "box", "layout": "vertical", "contents":[
                {"type": "text", "text": "查無對話紀錄，無法產生儀表板。", "wrap": True}
            ]}
        })))

    # 統計情緒
    emotion_counter = Counter()
    for doc in user_data:
        emo = doc.get("emotion_tag", "").strip()
        if emo and emo != "無法判斷":
            emotion_counter[emo] += 1

    if not emotion_counter:
        return FlexMessage(alt_text="情緒儀表板", contents=FlexContainer.from_json(json.dumps({
            "type": "bubble",
            "body": {"type": "box", "layout": "vertical", "contents":[
                {"type": "text", "text": "沒有明確的情緒標記，無法產生儀表板。", "wrap": True}
            ]}
        })))

    sorted_emotions = emotion_counter.most_common(3)  # 只取前三大情緒
    total = sum(emotion_counter.values())

    bubbles = []
    for emo, count in sorted_emotions:
        percent = round(count / total * 100)
        character = EMOTION_CHARACTERS.get(emo, "❓")
        bg_color, bar_color = EMOTION_COLORS.get(emo, ("#27ACB2", "#0D8186"))

        bubble = {
            "type": "bubble",
            "size": "nano",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": character, "color": "#ffffff", "align": "start", "size": "md"},
                    {"type": "text", "text": f"{percent}%", "color": "#ffffff", "align": "start", "size": "xs", "margin": "lg"},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [{"type": "filler"}],
                                "width": f"{percent}%",
                                "backgroundColor": bar_color,
                                "height": "6px"
                            }
                        ],
                        "backgroundColor": "#FFFFFF4D",
                        "height": "6px",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": bg_color,
                "paddingAll": "12px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": emo, "color": "#8C8C8C", "size": "sm", "wrap": True}
                ],
                "spacing": "md",
                "paddingAll": "12px"
            },
            "styles": {"footer": {"separator": False}}
        }
        bubbles.append(bubble)

    flex_json = {"type": "carousel", "contents": bubbles}
    return FlexMessage(alt_text="情緒儀表板", contents=FlexContainer.from_json(json.dumps(flex_json)))
