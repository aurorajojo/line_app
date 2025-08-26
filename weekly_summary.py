# weekly_summary.py
from datetime import datetime, timedelta
from mongo import summary_collection
import json
from linebot.v3.messaging import FlexMessage, FlexContainer

def generate_weekly_summary(user_id: str) -> FlexMessage:
    """
    產生一個 FlexMessage，包含過去七天的摘要
    """
    today = datetime.now() + timedelta(hours=8)  # 台灣時區
    bubbles = []

    for i in range(7):
        day = today - timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d")

        # 從 MongoDB 找該日期的摘要
        summary_doc = summary_collection.find_one(
            {
                "user_id": user_id,
                "date": {"$gte": day.replace(hour=0, minute=0, second=0, microsecond=0),
                         "$lt": (day + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)}
            }
        )
        if summary_doc and "summary" in summary_doc:
            summary_text = summary_doc["summary"]
            date_color = "#000000"  # 黑色（有資料）
        else:
            summary_text = "尚無摘要"
            date_color = "#888888"  # 灰色（沒資料）

        # 每一天做成一個 bubble
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
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
        bubbles.append(bubble)

    # Carousel 裝七個 bubble
    flex_content = {
        "type": "carousel",
        "contents": bubbles  # 往前七天，顯示時由舊到新
    }

    return FlexMessage(
        altText="過去七天摘要",
        contents=FlexContainer.from_json(json.dumps(flex_content))  # 🚀 dict 轉成 FlexContainer
    )
