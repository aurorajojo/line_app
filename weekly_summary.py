# weekly_summary.py
from datetime import datetime, timedelta
from daily_summary import check_and_summarize
from mongo import summary_collection
import json
from linebot.v3.messaging import FlexMessage, FlexContainer

# 定義七個柔和七彩背景
colors = [
    "#FFEAEA",  # 超淺粉
    "#FFF9E5",  # 超淺黃
    "#F0FFE5",  # 超淺綠
    "#E5F9FF",  # 超淺藍
    "#F4E5FF",  # 超淺紫
    "#FFE5F2",  # 超淺桃
    "#FFF3E5"   # 超淺橙
]
def get_weekday_chinese(date: datetime) -> str:
    weekdays = ["(一)", "(二)", "(三)", "(四)", "(五)", "(六)", "(日)"]
    return weekdays[date.weekday()]  # weekday() 0=Monday

def generate_weekly_summary(user_id: str) -> FlexMessage:
    """
    產生一個 FlexMessage，包含過去七天的摘要
    """
    check_and_summarize(user_id)          # 幫上次諮商那天做摘要
    
    today = datetime.now() + timedelta(hours=8)  # 台灣時區
    yesterday = today - timedelta(days=1)
    bubbles = []

    # 額外增加一個 bubble：查詢摘要
    query_bubble ={
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
            {
                "type": "text",
                "text": "以下是您過去七天的個別每日摘要，希望您能藉此回顧自己的心情與思緒，了解自己的狀態，也別忘了給自己一些關心或尋求協助。",
                "wrap": True,
                "weight": "bold",
                "size": "lg",
                "color": "#333333"
            },
            {
                "type": "separator",
                "margin": "md"
            },
            {
                "type": "text",
                "text": "如果想看更多摘要，點擊下方'查詢摘要'選擇要查詢摘要的日期",
                "wrap": True,
                "size": "sm",
                "color": "#555555"
            }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
            {
                "type": "button",
                "style": "primary",
                "action": {
                "type": "message",
                "label": "查詢摘要",
                "text": "查詢摘要"
                },
                "color": "#8D8684FF"
            }
            ]
        }
    }
    
    bubbles.append(query_bubble)  

    for i in range(7):
        day = yesterday - timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d") + " " + get_weekday_chinese(day)

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
            bg_color = colors[i % len(colors)]  # 循環使用七彩顏色
        else:
            summary_text = "尚無摘要"
            date_color = "#888888"  # 灰色（沒資料）
            bg_color = "#FFFFFF"  

        # 每一天做成一個 bubble
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": bg_color ,
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

def get_summary_by_date(user_id: str, chosen_date: str) -> FlexMessage:
    """
    查詢指定日期的摘要並回傳 FlexMessage
    chosen_date 格式: "YYYY-MM-DD"
    """
    try:
        # 將字串轉 datetime
        date_obj = datetime.strptime(chosen_date, "%Y-%m-%d")

    except ValueError:
        # 格式錯誤
        return FlexMessage(
            altText="日期格式錯誤",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "日期格式錯誤，請選擇正確日期", "wrap": True, "color": "#FF0000"}
                    ]
                }
            }
        )

    # 查詢 MongoDB
    summary_doc = summary_collection.find_one(
        {
            "user_id": user_id,
            "date": {
                "$gte": date_obj.replace(hour=0, minute=0, second=0, microsecond=0),
                "$lt": (date_obj + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            }
        }
    )

    if summary_doc and "summary" in summary_doc:
        summary_text = summary_doc["summary"]
        date_color = "#000000"
    else:
        summary_text = "尚無摘要"
        date_color = "#888888"

    date_str = date_obj.strftime("%Y-%m-%d") + " " + get_weekday_chinese(date_obj)
    
    # 建立 FlexMessage
    bubble = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": date_str, "weight": "bold", "size": "lg", "color": date_color},
                {"type": "text", "text": summary_text, "wrap": True, "size": "sm", "margin": "md", "color": "#555555"}
            ]
        }
    }

    return FlexMessage(
        altText=f"{chosen_date} 摘要",
        contents=FlexContainer.from_json(json.dumps(bubble))
    )

