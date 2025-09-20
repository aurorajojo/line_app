# resources.py
# ===== 載入系統提示詞與中原大學資源索引 =====

import json
import os
from config import PROMPT_FILE, RESOURCE_FILE, SUM_PROMPT, EVENTS_FILE

# 載入 system prompt 檔案內容
base_prompt = open(PROMPT_FILE, "r", encoding="utf-8").read() if os.path.exists(PROMPT_FILE) else "請設定你的 system_prompt.txt！"
summary_prompt = open(SUM_PROMPT, "r", encoding="utf-8").read() if os.path.exists(SUM_PROMPT) else "請設定你的 summary_prompt.txt！"

# 載入中原大學的資源檔案（地點索引等）
cycu_resources = json.load(open(RESOURCE_FILE, "r", encoding="utf-8")) if os.path.exists(RESOURCE_FILE) else {}
# 載入中原大學活動資訊
events = json.load(open(EVENTS_FILE, "r", encoding="utf-8")) if os.path.exists(EVENTS_FILE) else []
