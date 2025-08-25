# gaming_disorder_scale.py
# ===== 處理網路遊戲成癮量表的執行 ===== 

from linebot.v3.messaging import FlexMessage, FlexContainer
import json

# IGDT-10 中文題目（共 10 題）
questions = [
    "當你沒有玩線上遊戲時，你多常幻想自己在玩線上遊戲、想著前幾次玩遊戲的事；或期待下一次的遊戲？",
    "當你不能玩線上遊戲或是玩得比平常少的時候，你多常感到靜不下心、煩躁、焦慮、或悲傷？",
    "你感覺需要更常玩線上遊戲，或打更久的時間才覺得你玩夠了？",
    "你曾經試著減少花在線上遊戲的時間，但沒有成功？",
    "你曾經會玩線上遊戲而沒和朋友見面，或不再從事你以前常參加的嗜好活動？",
    "即使線上遊戲有負面影響（如減少睡眠、無法把學業或工作做好、與他人爭吵），你還是玩很多？",
    "你曾試著不讓家人、朋友或其他重要的人知道你玩線上遊戲的時間，或曾對他們謊稱？",
    "你曾玩線上遊戲來舒解負面情緒（如感到無助、內疚或焦慮）？",
    "你曾因為玩線上遊戲而可能危害或失去重要的人際關係？",
    "你曾經因為玩線上遊戲而使你在學校或工作的表現陷入重大危機？"
]

# 使用者作答狀態暫存
user_state = {}

# 題目的框架及按鈕的json
def make_question_bubble(question_text, q_number):
    bubble_json = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {"type": "text", "text": "網路遊戲成癮量表 IGDT-10", "wrap": True, "weight": "bold", "size": "xl"},
                {"type": "text", "text": f"Q:{question_text}", "margin": "none", "size": "lg", "wrap": True}
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {"type": "button", "style": "primary", "action": {"type": "message", "label": "從來沒有", "text": "0"}, "color": "#8D8684FF"},
                {"type": "button", "style": "primary", "action": {"type": "message", "label": "有時候", "text": "1"}, "color": "#8D8684FF"},
                {"type": "button", "style": "primary", "action": {"type": "message", "label": "經常", "text": "2"}, "color": "#8D8684FF"},
                {"type": "separator"},
                {"type": "button", "action": {"type": "message", "label": "結束測驗", "text": "結束測驗"}, "color": "#000000FF"},
                {"type": "text", "text": f"第{q_number}題，共10題", "align": "end"}
            ]
        }
    }
    return FlexMessage(
        alt_text=f"網路遊戲成癮量表 - 第{q_number}題",
        contents=FlexContainer.from_json(json.dumps(bubble_json))
    )


# 結果 bubble
def make_result_bubble(total_score, result_text):
    
    bubble_json = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {"type": "text", "text": "遊戲成癮量表結果", "wrap": True, "weight": "bold", "size": "xl", "align": "start"},
                {"type": "text", "text": f"你的總分是 {total_score} 分", "size": "lg", "margin": "md", "align": "start"},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": result_text, "wrap": True, "margin": "md"}
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "button", "style": "primary", "action": {"type": "message", "label": "重新測驗", "text": "我要做遊戲成癮量表"}, "color": "#8D8684FF"}
            ]
        }
    }

    return FlexMessage(
        alt_text="網路遊戲成癮量表結果",
        contents=FlexContainer.from_json(json.dumps(bubble_json))
    )

def start_gaming_test(user_id):  # 開始作答
    user_state[user_id] = {
        "current_q": 0,         # 目前作答來到的題數
        "scores": []            # 分數
    }
    return make_question_bubble(questions[0], 1)  # 呼叫函式，回傳題目的框架及按鈕的json


def handle_gaming_response(user_id, user_input):
    if user_id not in user_state:
        return None, None  # 尚未開始

    if user_input == "結束測驗":                  # 使用者提前終止測驗
        del user_state[user_id]
        return "end",   FlexMessage(
                          alt_text="結束測驗",
                          contents=FlexContainer.from_json(json.dumps({
                              "type": "bubble",
                              "body": {"type": "box", "layout": "vertical", "contents":[
                                  {"type": "text", "text": "測驗結束", "wrap": True}
                              ]}
                          }))
                        )

    if user_input not in ["0", "1", "2"]:         # 非預期輸入，回覆提醒文字
        return "invalid", "請點選上方題目下的按鈕作答，或選擇「結束測驗」。"

    # 紀錄分數
    score = int(user_input)
    user_state[user_id]["scores"].append(score)  # 計分數
    user_state[user_id]["current_q"] += 1        # 記題號
    idx = user_state[user_id]["current_q"]

    if idx >= len(questions):     # 判斷是否完成量表
        total_score = sum(user_state[user_id]["scores"])
        result_text = get_final_result(user_state[user_id]["scores"])  # 呼叫函式，判斷量表結果
        del user_state[user_id]
        return "end", make_result_bubble(total_score, result_text) # 回傳結果
    
    else:                         # 尚未完成量表，繼續作答
        return "next", make_question_bubble(questions[idx], idx + 1)

def check_gaming_disorder(scores): # 遊戲結束，計算成績
    criteria_met = 0
    for i, score in enumerate(scores):
        if i <= 7:  # 題目 1-8
            if score == 2:
                criteria_met += 1
        elif i == 8 or i == 9:  # 題目 9 或 10 任一為 2，即符合負面後果準則
            if scores[8] == 2 or scores[9] == 2:
                criteria_met += 1
                break
    return criteria_met >= 5  # 符合 5 項即為遊戲成癮

def get_final_result(scores):
    is_disordered = check_gaming_disorder(scores)
    if is_disordered:          # 有網路遊戲成癮
        return "你可能有網路遊戲成癮的傾向，建議與專業人員進一步討論。"
    else:                      # 沒有網路遊戲成癮
        return "你目前無明顯的網路遊戲成癮傾向，請持續保持良好的使用習慣。"
