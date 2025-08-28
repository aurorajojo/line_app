# mongo.py
# ===== 管理 MongoDB 資料庫連線與資料存取 =====

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from config import MONGODB_URI
import certifi  # 安全連線憑證

# 建立 MongoDB 客戶端連線
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'), tlsCAFile=certifi.where())

# 指定使用的資料庫與集合（chat_history）
db = client["line_groq_bot"]

# ===== 對話歷史集合 =====
history_collection = db["chat_history"]  # 儲存使用者對話歷史

# ===== 每日摘要集合 =====
summary_collection = db["daily_summary"]  # 儲存每日摘要

# ===== 量表集合 =====
scale_collection = db["scale_result"]  # 儲存量表結果