import requests
from bs4 import BeautifulSoup
import json
import re

base_url = "https://deptweb.cycu.edu.tw"

url = "https://deptweb.cycu.edu.tw/artssalon/"
headers = {"User-Agent": "Mozilla/5.0"}

res = requests.get(url, headers=headers)
res.raise_for_status()
soup = BeautifulSoup(res.text, "html.parser")

articles = soup.find_all("article")

events = []

for article in articles:
    a_tag = article.find("a")
    if a_tag and a_tag.get("href"):
        title = a_tag.get_text(strip=True)
        link = a_tag["href"]
        if not link.startswith("http"):
            link = base_url + link.lstrip("/")

        date = ""
        time_str = ""
        location = ""

        try:
            sub_res = requests.get(link, headers=headers)
            sub_res.raise_for_status()
            sub_soup = BeautifulSoup(sub_res.text, "html.parser")

            paragraphs = sub_soup.find_all(["p", "div"])

            for p in paragraphs:
                text = p.get_text(strip=True)
                if "時間" in text or "日期" in text:
                    # 改用更嚴謹的正則式
                    date_match = re.search(r"演出日期：([\d年月日]+[（\(][^）\)]+[）\)])", text)
                    time_match = re.search(r"演出時間：([\d：]+(?:（[^）]+）)?)", text)
                    place_match = re.search(r"演出場地：(.+?)(?:節目介紹|$)", text)

                    if date_match:
                        date = date_match.group(1)
                    if time_match:
                        time_str = time_match.group(1)
                    if place_match:
                        location = place_match.group(1).strip()
                    break

        except Exception as e:
            date = time_str = location = f"錯誤：{e}"

        events.append({
            "title": title,
            "url": link,
            "date": date,
            "time": time_str,
            "location": location
        })

    if len(events) >= 10:
        break

with open("artssalon_events.json", "w", encoding="utf-8") as f:
    json.dump(events, f, ensure_ascii=False, indent=2)

