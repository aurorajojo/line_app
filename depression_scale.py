# depression_scale.py
# ===== 處理憂鬱症量表的執行 ===== 

from linebot.v3.messaging import FlexMessage, FlexContainer
import json

# 台灣人憂鬱症量表題目，共18題
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

# 建立每一題的 Flex Bubble 結構
def make_question_bubble(question_text, q_number):
    bubble_json = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {"type": "text", "text": "台灣人憂鬱症量表", "wrap": True, "weight": "bold", "size": "xl"},
                {"type": "text", "text": f"Q:{question_text}", "margin": "none", "size": "lg", "wrap": True}
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
                {"type": "button", "action": {"type": "message", "label": "結束測驗", "text": "結束測驗"}, "color": "#000000FF"},
                {"type": "text", "text": f"第{q_number}題，共18題", "align": "end"}
            ]
        }
    }
    return FlexMessage(alt_text=f"台灣人憂鬱症量表 - 第{q_number}題",
                       contents=FlexContainer.from_json(json.dumps(bubble_json)))

# 開始測驗，初始化使用者狀態
def start_depression_test(user_id):
    user_state[user_id] = {
        "current_q": 0,   # 當前題號索引
        "scores": []      # 存放使用者各題得分
    }
    return make_question_bubble(questions[0], 1)

# 處理使用者每一題的回答
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
        return "invalid", "請點選上方選項按鈕作答或結束測驗。"

    # 紀錄分數
    score = int(user_input)
    user_state[user_id]["scores"].append(score)
    user_state[user_id]["current_q"] += 1
    idx = user_state[user_id]["current_q"]

    if idx >= len(questions):   # 量表結束，計算分數
        total_score = sum(user_state[user_id]["scores"])
        del user_state[user_id]

        if total_score <= 8:
            feedback = "真令人羨慕/你目前的情緒狀態很穩定，是個懂得適時調整情緒及紓解壓力的人，繼續保持下去。"
        elif total_score <= 14:
            feedback = "最近的情緒是否起伏下定?給自已多點關心，多注意情緒的變化，做適時的處理，比較不會陷入憂鬱情緒。"
        elif total_score <= 18:
            feedback = "你是不是有許多事壓在心上，肩上總覺得很沉重?千萬別再「撐」了!趕快找個有相同經驗的朋友聊聊，給心找個出口。"
        elif total_score <= 28:
            feedback = "現在的你必定無法展露笑容，一肚子苦惱及煩悶，趕緊找專業機構或醫療單位協助。"
        else:
            feedback = "你是不是會不由自主的沮喪、難過，無法掙脫?因為你的心已「感冒」，心病需要心藥醫，緊到醫院找專業及可信賴的醫檢查，透過他們的診療，你將不再覺得孤單、無助!"

        return "end", make_feedback_bubble(total_score, feedback)
    
    else:
        # 回下一題 FlexMessage
        return "next", make_question_bubble(questions[idx], idx + 1)
    

# 建立回饋用的 Bubble
def make_feedback_bubble(total_score, feedback):
    bubble_json = {
        "type": "bubble", "size": "mega",
        "body": {
            "type": "box", "layout": "vertical", "spacing": "md",
            "contents": [
                {"type": "text", "text": "憂鬱症量表結果", "weight": "bold", "size": "xl", "color": "#333333"},
                {"type": "text", "text": f"你的總分是 {total_score} 分", "size": "lg", "color": "#000000"},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": feedback, "wrap": True, "size": "md", "color": "#555555", "margin": "md"}
            ]
        },
        "footer": {
            "type": "box", "layout": "vertical",
            "contents": [
                {"type": "button", "style": "primary", "action": {"type": "message", "label": "重新測驗", "text": "我要做憂鬱症量表"}, "color": "#8D8684FF"}
            ]
        }
    }

    return FlexMessage(
        alt_text="憂鬱症量表結果",
        contents=FlexContainer.from_json(json.dumps(bubble_json))
    )
