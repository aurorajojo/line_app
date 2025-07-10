import json

# 定義置換對照表：你可以根據需求修改
strategy_map = {
    "Question": "Greeting",
    "Questions": "OpenQuestion",
    "Information": "InfoGiving",
    # 可加上更多需要轉換的策略
}

# 讀取 input_dialogues.json
with open("input_dialogues.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 替換 strategy 欄位
for convo in data:
    for utterance in convo.get("dialog", []):
        if "strategy" in utterance:
            old = utterance["strategy"]
            if old in strategy_map:
                utterance["strategy"] = strategy_map[old]

# 儲存到新的 JSON 檔案
with open("output_dialogues.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✔️ Strategy 置換完成，結果儲存為 output_dialogues.json")
