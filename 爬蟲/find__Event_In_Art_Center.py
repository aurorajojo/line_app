import requests
from bs4 import BeautifulSoup
import json

url = "https://artcenter.cycu.edu.tw/"
headers = {"User-Agent": "Mozilla/5.0"}

res = requests.get(url, headers=headers)
res.raise_for_status()
soup = BeautifulSoup(res.text, "html.parser")

events = []

# 嘗試抓取所有 <a> 標籤，且 href 中包含 /uploads/ 圖片連結，並用 aria-label 或 title 取得活動名稱
for a in soup.find_all("a", href=True):
    href = a["href"]
    title = a.get("aria-label") or a.get("title") or a.get_text(strip=True)
    if "/uploads/" in href and title:
        events.append({
            "title": title,
            "url": href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/")
        })

# 去重、取前 10 筆
unique = []
seen = set()
for e in events:
    if e["title"] not in seen:
        unique.append(e)
        seen.add(e["title"])
    if len(unique) >= 10:
        break

# 儲存 JSON
with open("artcenter_events.json", "w", encoding="utf-8") as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)

print(f"✅ 成功抓取 {len(unique)} 筆項目，存成 artcenter_events.json")
