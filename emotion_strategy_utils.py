# emotion_strategy_utils.py

import re

NUMBER_TO_EMOTION = {
    "1": "焦慮",
    "2": "悲傷",
    "3": "憤怒",
    "4": "恐懼",
    "5": "厭惡",
    "6": "羞愧",
    "7": "無法判斷",
    "8": "其他"
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

def extract_emotion_from_reply(reply_text):
    """
    從 reply 文字中擷取第一個被 [] 包住的情緒關鍵字或編號
    可辨識的情緒有：焦慮、悲傷、憤怒、恐懼、厭惡、羞愧、其他、無法判斷
    以及數字代號1-8
    找不到則回傳 '無法判斷'
    """
    pattern = r"\[([12345678]|焦慮|悲傷|憤怒|恐懼|厭惡|羞愧|其他|無法判斷)\]"
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
