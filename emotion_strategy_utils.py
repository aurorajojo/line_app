# emotion_strategy_utils.py
# ===== 情緒和策略的紀錄 ===== 

import re

"""
為了避免讓使用者察覺我們正在進行情緒分析與心理策略紀錄
我們設計了隱藏式的標記機制
當 LLM 回傳分析結果時，不會直接以文字顯示情緒名稱或策略內容
而是透過編碼形式（如 [1]～[8] 表示情緒、(1)～(8) 表示策略、{1}~{12} 表示意圖）進行標註
這個檔案就是在進行上述的標記轉換處理
"""
NUMBER_TO_EMOTION = {
    "1": "焦慮",
    "2": "悲傷",
    "3": "憤怒",
    "4": "恐懼",
    "5": "厭惡",
    "6": "羞愧",
    "7": "快樂",
    "8": "滿足",
    "9": "驚訝",
    "10": "興奮",
    "11": "冷靜",
    "12": "無法判斷"
}

strategy_map = {
    "1": "問句引導",
    "2": "轉述或改寫",
    "3": "情緒反映",
    "4": "自我揭露",
    "5": "肯定與安慰",
    "6": "提出建議",
    "7": "提供資訊",
    "8": "其他"
}

# ===== 意圖對應 =====
intention_map = {
    "1": "聚焦",
    "2": "澄清",
    "3": "情緒宣洩",
    "4": "認知覺察",
    "5": "情緒理解",
    "6": "洞察理解",
    "7": "支持陪伴",
    "8": "希望鼓勵",
    "9": "自我控制",
    "10": "改變行動",
    "11": "提供資訊",
    "12": "蒐集資訊"
}

def extract_emotion_from_reply(reply_text):
    """
    從 reply 文字中擷取第一個被 [] 包住的情緒關鍵字或編號
    可辨識的情緒有：焦慮、悲傷、憤怒、恐懼、厭惡、羞愧、其他、無法判斷
    以及數字代號1-8
    找不到則回傳 '無法判斷'
    """
    pattern = r"\[([12345678]|焦慮|悲傷|憤怒|恐懼|厭惡|羞愧|快樂|滿足|驚訝|興奮|冷靜|無法判斷)\]"
    match = re.search(pattern, reply_text)
    if match:
        val = match.group(1)
        # 如果是數字，轉成中文情緒
        if val in NUMBER_TO_EMOTION:
            return NUMBER_TO_EMOTION[val]
        else:
            return val  # 已經是中文情緒
    else:
        return "無法判斷"

def extract_strategies(reply_text):
    """
    從 reply 文字中找出所有 (數字) 標註，並轉成中文策略名稱，回傳去重後的 list
    若找不到策略編號，回傳空 list
    """
    nums = re.findall(r"\((\d+)", reply_text)
    strategies = [strategy_map.get(n, "未知策略") for n in nums]
    return list(set(strategies))

# ===== 意圖擷取函式 =====
def extract_intentions(reply_text):
    """
    從 reply 文字中找出所有 {數字} 標註，並轉成中文意圖名稱，回傳去重後的 list
    若找不到意圖編號，回傳空 list
    """
    nums = re.findall(r"\{(\d+)\}", reply_text)
    intentions = [intention_map.get(n, "未知意圖") for n in nums]
    return list(set(intentions))