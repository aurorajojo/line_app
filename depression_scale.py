from linebot.v3.messaging import FlexMessage, FlexContainer
import json

questions = [
    "我常常覺得想哭", "我覺得心情不好", "我覺得比以前容易發脾氣", "我睡不好",
    "我覺得不想吃東西", "我覺得胸口悶悶的 (心肝頭或胸坎綁綁)",
    "我覺得不輕鬆、不舒服 (不爽快)", "我覺得身體疲勞虛弱、無力 (身體很虛、沒力氣、元氣及體力)",
    "我覺得很煩", "我覺得記憶力不好", "我覺得做事時無法專心",
    "我覺得想事情或做事時，比平常要緩慢", "我覺得比以前較沒信心",
    "我覺得比較會往壞處想", "我覺得想不開、甚至想死",
    "我覺得對什麼事都失去興趣", "我覺得身體不舒服 (如頭痛、頭暈、心悸或肚子不舒服…等)",
    "我覺得自己很沒用"
]

# 用戶答題暫存
user_state = {}

def make_question_bubble(question_text, q_number):
    bubble_json = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {"type": "text", "text": "台灣人憂鬱症量表", "wrap": True, "weight": "bold", "size": "xl"},
                {"type": "text", "text": f"Q{q_number}: {question_text}", "margin": "none", "size": "xl"}
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {"type": "button", "style": "primary", "action": {"type": "message", "label": "沒有或極少 每周: 1天以下", "text": "0"}, "color": "#8D8684FF"},
                {"type": "button", "style": "primary", "action": {"type": "message", "label": "有時侯 每周: 1～2天", "text": "1"}, "color": "#8D8684FF"},
                {"type": "button", "style": "primary", "action": {"type": "message", "label": "時常 每周: 3～4天", "text": "2"}, "color": "#8D8684FF"},
                {"type": "button", "style": "primary", "action": {"type": "message", "label": "常常或總是 每周: 5～7天", "text": "3"}, "color": "#8D8684FF"},
                {"type": "separator"},
                {"type": "button", "action": {"type": "message", "label": "結束測驗", "text": "結束測驗"}, "color": "#000000FF"}
            ]
        }
    }
    return FlexMessage(alt_text=f"台灣人憂鬱症量表 - 第{q_number}題",
                       contents=FlexContainer.from_json(json.dumps(bubble_json)))

def start_depression_test(user_id):
    user_state[user_id] = {
        "current_q": 0,
        "scores": []
    }
    return make_question_bubble(questions[0], 1)

def handle_depression_response(user_id, user_input):
    if user_id not in user_state:
        # 尚未開始測驗，或重新開始
        return None, None

    if user_input == "結束測驗":
        total_score = sum(user_state[user_id]["scores"])
        del user_state[user_id]
        return "end", f"測驗結束"

    # 期望輸入 0~3 的字串
    if user_input not in ["0", "1", "2", "3", "結束測驗"]:
        # 非預期輸入，回覆提醒文字
        return "invalid", "請點選下方選項按鈕作答或結束測驗。"

    # 紀錄分數
    score = int(user_input)
    user_state[user_id]["scores"].append(score)
    user_state[user_id]["current_q"] += 1
    idx = user_state[user_id]["current_q"]

    if idx >= len(questions):
        total_score = sum(user_state[user_id]["scores"])
        del user_state[user_id]
        return "end", f"恭喜完成量表！你的總分是 {total_score} 分。建議適時尋求專業協助。"
    else:
        # 回下一題 FlexMessage
        return "next", make_question_bubble(questions[idx], idx + 1)
