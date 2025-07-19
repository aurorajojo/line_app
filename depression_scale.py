# depression_scale.py

from linebot.v3.messaging import FlexMessage

# 憂鬱量表題目
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

# 紀錄使用者進度（可改用 MongoDB 等儲存）
user_state = {}

# 建立 bubble flex message
def create_question_bubble(user_id: str, index: int) -> FlexMessage:
    q = questions[index]
    contents = {
        "type": "bubble",
        "direction": "ltr",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [{
                "type": "text",
                "text": "台灣人憂鬱症量表",
                "weight": "bold",
                "size": "lg",
                "align": "center",
                "color": "#262222FF"
            }]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"Q : {q}",
                    "weight": "bold",
                    "size": "lg",
                    "align": "center"
                }
            ] + [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#8D8684FF",
                    "action": {
                        "type": "message",
                        "label": label,
                        "text": str(score)
                    }
                } for label, score in [
                    ("沒有或極少 每周: 1天以下", 0),
                    ("有時侯 每周: 1～2天", 1),
                    ("時常 每周: 3～4天", 2),
                    ("常常或總是 每周: 5～7天", 3)
                ]
            ] + [
                {
                    "type": "separator",
                    "margin": "xxl",
                    "color": "#000000FF"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "結束測驗",
                        "text": "結束測驗"
                    }
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [{
                "type": "text",
                "text": f"第 {index+1} 題 / 共 18 題"
            }]
        }
    }

    return FlexMessage(alt_text="台灣人憂鬱症量表", contents=contents)

# 根據使用者輸入更新進度
def handle_depression_response(user_id: str, message_text: str):
    if user_id not in user_state:
        return None, None

    state = user_state[user_id]

    if message_text == "結束測驗":
        total = state["score"]
        user_state.pop(user_id)
        return total, "您已中止測驗。總分為：" + str(total)

    if message_text not in ["0", "1", "2", "3"]:
        return None, "請使用按鈕選擇數值來作答唷～"

    state["score"] += int(message_text)
    state["current"] += 1

    if state["current"] >= len(questions):
        total = state["score"]
        user_state.pop(user_id)

        # 評估結果
        if total <= 8:
            result = (
                "真令人羨慕！你目前的情緒狀態很穩定，是個懂得適時調整情緒及紓解壓力的人，繼續保持下去。"
            )
        elif total <= 14:
            result = (
                "最近的情緒是否起伏不定？給自己多點關心，多注意情緒的變化，做適時的處理，比較不會陷入憂鬱情緒。"
            )
        elif total <= 18:
            result = (
                "你是不是有許多事壓在心上，肩上總覺得很沉重？千萬別再「撐」了！"
                "趕快找個有相同經驗的朋友聊聊，給心找個出口。"
            )
        elif total <= 28:
            result = (
                "現在的你必定無法展露笑容，一肚子苦惱及煩悶，趕緊找專業機構或醫療單位協助。"
            )
        else:
            result = (
                "你是不是會不由自主地沮喪、難過，無法掙脫？"
                "因為你的心已「感冒」，心病需要心藥醫，"
                "請儘早到醫院找專業且可信賴的醫師檢查，"
                "透過他們的診療，你將不再覺得孤單、無助。"
            )


        return total, f"測驗完成，您的總分為 {total} 分。\n結果：{result}"

    return "next", create_question_bubble(user_id, state["current"])

# 啟動測驗
def start_depression_test(user_id: str):
    user_state[user_id] = {"score": 0, "current": 0}
    return create_question_bubble(user_id, 0)
