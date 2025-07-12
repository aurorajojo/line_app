# config.py
# ===== 儲存各種設定值與金鑰 =====

import os

# LINE Bot 設定
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")

# Groq API 設定
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")

# MongoDB 連線字串
MONGODB_URI = os.getenv("MONGODB_URI", "")

# 資源檔案路徑
PROMPT_FILE = os.path.join(BASE_DIR, 'data', 'system_prompt.txt')
RESOURCE_FILE = os.path.join(BASE_DIR, 'data', 'cycu_resources.json')
