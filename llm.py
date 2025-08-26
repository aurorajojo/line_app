# llm.py
# ===== 呼叫 Groq API（ llama-3.3-70b-versatile 模型）回應使用者輸入 =====

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
        "max_tokens": 1024      # 摘要長度
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
            "content": """你是一位心理諮商助理，任務是幫助總結用戶一天的聊天內容。  
                            請用 3～5 點的條列方式，整理出：
                            1. 使用者當天主要談到的主題或困擾  
                            2. 使用者的情緒狀態變化  
                            3. 諮商過程中的重要洞見或進展  
                            4. 建議後續可以關注的方向  

                            請保持語氣專業、中立，不要加入臆測或診斷。"""
        }
    ]

    # 將使用者與 LLM 對話加入 messages
    for c in chats:
        if "user_input" in c:
            messages.append({"role": "user", "content": f"{c['user_input']}"})
        if "reply" in c:
            messages.append({"role": "assistant", "content": f"{c['reply']}"})

    # 呼叫 Groq API
    summary = call_summary_llm(messages)
    return summary, messages