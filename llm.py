# llm.py
# ===== 呼叫 Groq API（例如 llama-3.3 模型）回應使用者輸入 =====
import requests
from config import GROQ_API_KEY, GROQ_API_URL

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
        "temperature": 0.7,
        "max_tokens": 1024
    }

    # 發送 POST 請求至 Groq API
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"⚠️ Groq API 錯誤：{response.status_code}"
