import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

base_url = "https://artcenter.cycu.edu.tw/"
headers = {"User-Agent": "Mozilla/5.0"}

res = requests.get(base_url, headers=headers)
res.raise_for_status()
soup = BeautifulSoup(res.text, "html.parser")

events = []
timestamp = datetime.now().isoformat()

# 尋找文章連結（/2025/xxx/ 格式）
for a in soup.find_all("a", href=True):
    href = a["href"]
    if re.search(r"/2025/\d+/?$", href):  # 符合活動頁格式
        full_url = href if href.startswith("http") else base_url.rstrip("/") + "/" + href.lstrip("/")

        # 預設欄位
        title = ""
        start_date = ""
        end_date = ""
        event_location = ""
        tour_date = ""
        tour_time = ""
        opening_hours = {}
        url_register = ""

        try:
            sub_res = requests.get(full_url, headers=headers)
            sub_res.raise_for_status()
            sub_soup = BeautifulSoup(sub_res.text, "html.parser")

            # 取得文章標題
            h1_tag = sub_soup.find("h1")
            title = h1_tag.get_text(strip=True) if h1_tag else ""

            # 掃描頁面所有文字區塊
            for tag in sub_soup.find_all(["p", "div", "span", "li"]):
                text = tag.get_text(strip=True)

                # 展覽日期
                if "展覽日期" in text:
                    date_match = re.search(r"(\d{4}/\d{2}/\d{2})\s*[–-~~－]\s*(\d{2}/\d{2})", text)
                    if date_match:
                        start_date = date_match.group(1)
                        year = start_date.split("/")[0]
                        end_date = f"{year}/{date_match.group(2)}"

                # 地點
                if not event_location and "展覽地點" in text:
                    loc_match = re.search(r"展覽地點[:：]?\s*(.+)", text)
                    if loc_match:
                        event_location = loc_match.group(1).strip()

                # 導覽、茶會資訊
                if "茶會" in text or "導覽" in text:
                    date_match = re.search(r"(\d{4})\s*/\s*(\d{2})\s*/\s*(\d{2})", text)
                    time_match = re.search(r"(\d{1,2}:\d{2})[-–~~－](\d{1,2}:\d{2})", text)
                    if date_match:
                        tour_date = f"{date_match.group(1)}/{date_match.group(2)}/{date_match.group(3)}"
                    if time_match:
                        tour_time = f"{time_match.group(1)}-{time_match.group(2)}"

                # 開放時間
                if "開放時間" in text or "Opening Hours" in text:
                    lines = text.split("\n")
                    for line in lines:
                        if "週一" in line or "Mon" in line:
                            opening_hours["mon_fri"] = re.sub(r"^.*?(\d{1,2}:\d{2}[–-]\d{1,2}:\d{2}).*", r"\1", line)
                        elif "週六" in line or "Sat" in line:
                            opening_hours["sat"] = re.sub(r"^.*?(\d{1,2}:\d{2}[–-]\d{1,2}:\d{2}).*", r"\1", line)
                        elif "週日" in line or "Sun" in line:
                            opening_hours["sun"] = "Closed"

                # 報名連結
                if "itouch.cycu.edu.tw/go/" in text:
                    url_match = re.search(r"https?://itouch\.cycu\.edu\.tw/go/\S+", text)
                    if url_match:
                        url_register = url_match.group(0)

        except Exception as e:
            print(f"⚠️ 無法解析 {full_url}：{e}")

        events.append({
            "title": title,
            "url": full_url,
            "start_date": start_date,
            "end_date": end_date,
            "location": event_location,
            "tour_date": tour_date,
            "tour_time": tour_time,
            "opening_hours": opening_hours,
            "url_register": url_register,
            "timestamp": timestamp
        })

        if len(events) >= 10:
            break

# 存成 JSON
with open("artcenter_events_detailed.json", "w", encoding="utf-8") as f:
    json.dump(events, f, ensure_ascii=False, indent=2)

print(f"✅ 已成功抓取 {len(events)} 筆活動，儲存至 artcenter_events_detailed.json")
