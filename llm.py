# llm.py
# ===== 呼叫 Groq API（ llama-3.3-70b-versatile 模型）回應使用者輸入 =====

import re
import requests
from config import GROQ_API_KEY, GROQ_API_URL, SUMMARY_API_KEY

# 設定請求標頭
headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

# 封裝 API 呼叫函式
def call_groq_llm(messages, model="llama-3.3-70b-versatile"):
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,      # 創造力
        "max_tokens": 256        # 最大token數量
    }

    # 發送 POST 請求至 Groq API
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)

    if response.status_code == 200:                                  # 成功收到回應
        return response.json()["choices"][0]["message"]["content"]
    elif response.status_code == 429:                                # token 超過上限，需要稍等
        return "目前請求量較高，請稍等約 1 分鐘後再試一次，謝謝您的耐心等待！"
    else:                                                            # 其他的報錯
        return f"⚠️ Groq API 錯誤：{response.status_code}"# 封裝摘要 API
    
def call_summary_llm(messages, model="llama-3.3-70b-versatile"):
    headers = {
        "Authorization": f"Bearer {SUMMARY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,   # 摘要偏精準
        "max_tokens": 512      # 摘要長度
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    elif response.status_code == 429:
        return "目前請求量較高，請稍後再試。"
    else:
        return f"⚠️ 摘要 API 錯誤：{response.status_code}"
    
def generate_summary_with_llm(chats):
    """
    將對話整理成 messages，呼叫 Groq API 生成摘要
    """
    messages = [
        {
            "role": "system",
            "content": 
            """你是一位溫柔、支持性的中原大學線上輔導心理諮商師
                請依照以下規範，將整天的對話整理成摘要，提供給使用者回顧：

                摘要要求：
                1. 使用第二人稱（例如「你感到…」、「你希望…」）
                2. 聚焦於使用者表達的 **主要情緒、想法、需求與關注的主題**
                3. 不需要逐句重述對話，而是要條列式統整與歸納，每條以 `* ` 開頭
                4. 請用溫柔、簡潔的方式歸納
                5. 使用繁體中文，台灣用語
                6. 在摘要最上方加標題:今日摘要
                7. 僅輸出摘要，不要進行對話、不要回答問題
                8. 不要編造未出現在對話中的情緒或事件
                以下是要摘要的整天對話，請輸出一份當日摘要："""
        }
    ]

    # 將使用者與 LLM 對話加入 messages
    for c in chats:
        if "user_input" in c:
            messages.append({"role": "user", "content": f"{c['user_input']}"})
        if "reply" in c:
            cleaned_reply = re.sub(r"[\(\[\{]\d+[\)\]\}]", "", c["reply"]).strip()
            messages.append({"role": "assistant", "content": cleaned_reply })

    # 呼叫 Groq API
    summary = call_summary_llm(messages)
    return summary, messages