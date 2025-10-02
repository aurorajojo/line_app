# config.py
# ===== 儲存各種設定值與金鑰 =====

import os
from dotenv import load_dotenv

# 載入 .env
#load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# LINE Bot 設定
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")

# Groq API 設定
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
SUMMARY_API_KEY = os.getenv("SUMMARY_API_KEY", "")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")

# MongoDB 連線字串
MONGODB_URI = os.getenv("MONGODB_URI", "")

# 資源檔案路徑
PROMPT_FILE = os.path.join(BASE_DIR, 'data', 'system_prompt.txt')
SUM_PROMPT = os.path.join(BASE_DIR, 'data', 'summary_prompt.txt')
RESOURCE_FILE = os.path.join(BASE_DIR, 'data', 'cycu_resources.json')
EVENTS_FILE = os.path.join(BASE_DIR, "data", "events.json")

