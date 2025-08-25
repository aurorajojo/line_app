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

# === 情緒對應角色（增加親和力用） ===
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

# === 不同情緒的顏色（背景色 / 長條顏色） ===
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
    """
    依據使用者的歷史紀錄，生成情緒儀表板 FlexMessage
    """

    # 取得使用者的歷史對話紀錄
    user_data = list(history_collection.find({"user_id": user_id}))

    # === 如果沒有對話紀錄，回傳提示訊息 ===
    if not user_data:
        return FlexMessage(
            alt_text="情緒儀表板",
            contents=FlexContainer.from_json(json.dumps({
                "type": "bubble",
                "body": {"type": "box", "layout": "vertical", "contents":[
                    {"type": "text", "text": "查無對話紀錄，無法產生儀表板。", "wrap": True}
                ]}
            }))
        )

    # === 統計情緒出現次數 ===
    emotion_counter = Counter()
    for doc in user_data:
        emo = doc.get("emotion", "").strip()  # 取出紀錄中的情緒標籤
        if emo and emo != "無法判斷":  # 過濾掉「無法判斷」
            emotion_counter[emo] += 1   # 累計情緒次數

    # === 如果沒有情緒標記，回傳提示訊息 ===
    if not emotion_counter:
        return FlexMessage(
            alt_text="情緒儀表板",
            contents=FlexContainer.from_json(json.dumps({
                "type": "bubble",
                "body": {"type": "box", "layout": "vertical", "contents":[
                    {"type": "text", "text": "沒有明確的情緒標記，無法產生儀表板。", "wrap": True}
                ]}
            }))
        )

    # === 只取出現次數前七大的情緒 ===
    sorted_emotions = emotion_counter.most_common(7)
    total = sum(emotion_counter.values())  # 總情緒數量（計算比例用）

    bubbles = []  # 儲存每個情緒的 bubble
    for emo, count in sorted_emotions:
        percent = round(count / total * 100)  # 計算該情緒的百分比
        character = EMOTION_CHARACTERS.get(emo, "❓")  # 找對應角色
        bg_color, bar_color = EMOTION_COLORS.get(emo, ("#27ACB2", "#0D8186"))  # 找顏色

        # === 建立單一情緒的 bubble 卡片 ===
        bubble = {
            "type": "bubble",
            "size": "nano",  # 使用 nano 大小，適合多張卡片並列
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    # 顯示角色
                    {"type": "text", "text": character, "color": "#ffffff", "align": "start", "size": "md","wrap": True},
                    # 顯示比例 %
                    {"type": "text", "text": f"{percent}%", "color": "#ffffff", "align": "start", "size": "xs", "margin": "lg"},
                    # 進度條（長條圖）
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [{"type": "filler"}],  # 內部填充
                                "width": f"{percent}%",  # 進度條長度
                                "backgroundColor": bar_color,  # 進度條顏色
                                "height": "6px"
                            }
                        ],
                        "backgroundColor": "#FFFFFF4D",  # 外框背景
                        "height": "6px",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": bg_color,  # 卡片上方背景色
                "paddingAll": "12px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    # 顯示情緒名稱
                    {"type": "text", "text": emo, "color": "#8C8C8C", "size": "sm", "wrap": True}
                ],
                "spacing": "md",
                "paddingAll": "12px"
            },
            "styles": {"footer": {"separator": False}}
        }
        bubbles.append(bubble)

    # === 建立 carousel（多張情緒卡片組成） ===
    flex_json = {"type": "carousel", "contents": bubbles}

    # === 回傳 FlexMessage ===
    return FlexMessage(
        alt_text="情緒儀表板",
        contents=FlexContainer.from_json(json.dumps(flex_json))
    )
