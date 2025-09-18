import json
from datetime import datetime, timedelta
import json
from linebot.v3.messaging import FlexMessage, FlexContainer
from config import EVENTS_FILE

def load_upcoming_events():

    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        try:
            events = json.load(f)
        except Exception as e:
            print(f"讀取 events.json 失敗: {e}")
            return []

    now = datetime.now() + timedelta(hours=8)  # 台灣時間
    upcoming = []
    for e in events:
        try:
            dt = datetime.strptime(e["date"], "%Y-%m-%d")
            if dt > now:  # 還沒過期
                upcoming.append(e)
        except Exception as ex:
            print(f"日期格式錯誤 {e}: {ex}")
            continue

    # 依日期排序 & 取最近五個
    upcoming.sort(key=lambda x: x["date"])
    return upcoming[:5]


def events_to_flex(events):
    bubbles = []
    # === 第一個 bubble：介紹===
    intro_bubble = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "即將到來的藝文活動", "weight": "bold", "size": "xl", "wrap": True},
                {"type": "separator", "margin": "md"},
                {"type": "text",
                 "text": "參加藝文活動可以：\n"
                         "1. 舒緩壓力與焦慮\n"
                         "2. 提升正向情緒與幸福感\n"
                         "3. 增進社交互動與人際連結\n"
                         "4. 培養專注力與創造力\n"
                         "趕快來參加一個活動看看吧～\n",
                 "size": "sm",
                 "wrap": True,
                 "color": "#555555",
                 "margin": "sm"}
            ]
        }
    }
    bubbles.append(intro_bubble)

    for e in events:
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": e.get("title", "未命名活動"), "weight": "bold", "size": "xl", "wrap": True},
                    {"type": "separator","margin": "md"},
                    {"type": "text", "text": f"📅 日期：{e.get('date', '')}", "size": "sm", "color": "#555555", "wrap": True, "margin": "sm"},
                    {"type": "text", "text": f"⏰ 時間：{e.get('time', '')}", "size": "sm", "color": "#555555", "wrap": True, "margin": "sm"},
                    {"type": "text", "text": f"🏫 地點：{e.get('location', '未提供')}", "size": "sm", "color": "#555555", "wrap": True,"margin": "sm"}
                ]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "詳細資訊",
                            "uri": e.get("url", "https://cycu.edu.tw")
                        },
                        "style": "primary",
                        "color": "#8D8684"
                    }
                ]
            }
        }
        bubbles.append(bubble)

    bubbles =  {
        "type": "carousel",
        "contents": bubbles
    }
    return FlexMessage(
        altText="活動列表",
        contents=FlexContainer.from_json(json.dumps(bubbles))
    )