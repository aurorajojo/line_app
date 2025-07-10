# resources.py
# ===== 載入系統提示詞與中原大學資源索引 =====

import json
import os
from config import PROMPT_FILE, RESOURCE_FILE

# 載入 system prompt 檔案內容
base_prompt = open(PROMPT_FILE, "r", encoding="utf-8").read() if os.path.exists(PROMPT_FILE) else "請設定你的 system_prompt.txt！"

# 載入中原大學的資源檔案（地點索引等）
cycu_resources = json.load(open(RESOURCE_FILE, "r", encoding="utf-8")) if os.path.exists(RESOURCE_FILE) else {}
