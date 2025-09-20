# depression_scale.py
# ===== 處理董氏憂鬱量表-大專生版的執行 ===== 

from linebot.v3.messaging import FlexMessage, FlexContainer
import json
from mongo import scale_collection
from datetime import datetime, timedelta

# 憂鬱情緒量表題目，共32題
questions = [
    "我覺得心裡很難過。",
    "碰到事情，我只想逃避。",
    "我最近有自殺的念頭。",
    "我心裡覺得很空虛。",
    "沒有人瞭解我。",
    "我感到絕望。",
    "我覺得人生是灰暗的。",
    "我對原本喜歡的事，變得沒興趣了。",
    "我的胸口會緊緊、悶悶的。",
    "我在掩飾心裡的痛苦。",
    "我變得討厭自己。",
    "我是別人的負擔。",
    "我覺得很煩。",
    "我上課唸書不能專心。",
    "我感到昏昏沈沈的。",
    "我覺得自己沒有未來。",
    "我認為自己做人失敗。",
    "我會莫名地想哭。",
    "我覺得日子痛苦難熬。",
    "我不想出門。",
    "我覺得生活沒有意義。",
    "我感到很寂寞。",
    "我對任何事都提不起勁。",
    "我覺得記憶力變差了。",
    "我會猶豫不決，很難做決定。",
    "我覺得自己是沒有價值的人。",
    "沒有人關心我。",
    "我不快樂。",
    "我會想要傷害自己。",
    "我會一直發呆。",
    "我不想和別人交談。",
    "我想自己躲起來。"
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
                {"type": "text", "text": "董氏憂鬱量表-大專生版", "wrap": True, "weight": "bold", "size": "xl"},
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
                {"type": "button","action": {"type": "uri","label": "🔗題目出處：董氏基金會","uri": "https://www.etmh.org/Online_tool/detection2_form"},"color": "#000000FF"},
                {"type": "text", "text": f"第{q_number}題，共32題", "align": "end"}
            ]
        }
    }
    return FlexMessage(alt_text=f"董氏憂鬱量表-大專生版 - 第{q_number}題",
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
        return "end", FlexMessage(
                            alt_text="結束測驗",
                            contents=FlexContainer.from_json(json.dumps({
                                "type": "bubble",
                                "body": {"type": "box", "layout": "vertical", "contents":[
                                    {"type": "text", "text": "測驗結束", "wrap": True}
                                ]},
                                "footer": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {"type": "button", "style": "primary", "action": {"type": "message", "label": "重新測驗", "text": "我要做憂鬱症量表"}, "color": "#8D8684FF"},
                                        {"type": "separator", "margin": "sm" },
                                        {"type": "button", "style": "primary", "action": {"type": "message", "label": "查看歷史", "text": "我要看憂鬱症量表歷史"}, "color": "#8D8684FF"}
                                    ]
                                }
                            }))
                        )

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
        # 存到 MongoDB
        scale_collection.insert_one({
            "user_id": user_id,
            "total_score": total_score,
            "type": "depression",
            "timestamp": datetime.now()  + timedelta(hours=8)
        })

        del user_state[user_id]

        if total_score <= 28:
            feedback = "你現在的情緒大致穩定，沒有明顯的憂鬱情緒，通常可以處理生活上的壓力，建議你繼續保持良好的心情。"
        elif total_score <= 35:
            feedback = "最近是否經歷了一些挫折或有不愉快的經驗？仔細回想，情緒的變化及變化的緣由，試著把問題及感受向自己信任的人(例如朋友、父母或師長)說出來，一起討論處理的方法。他們的經驗和支持會帶給你不同的想法！保持良好的生活習慣，讓自己有活力！或是和朋友一起做些愉快放鬆的事。"
        elif total_score <= 51:
            feedback = "是不是已經持續一陣子(超過二星期)情緒低落、悶悶的、不想和別人交談？你的憂鬱程度已經蠻高了，一肚子苦惱與煩悶，連朋友也不知該如何幫你，可以與輔導老師、心理師或醫師聊聊，進一步瞭解自己是否需要專業的協助。"
        else:
            feedback = "你的心情持續低落？愁眉不展？只想一個人獨處？變得什麼都不想做？甚至對未來覺得無助或絕望？你的心已經感冒，心病需要心藥醫，趕緊到醫院找專業及可信賴的醫生檢查，透過他們的診斷與治療，你將不再覺得孤單、無助！"

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
                {"type": "text", "text": "董氏憂鬱量表-大專生版結果", "wrap": True, "weight": "bold", "size": "xl", "color": "#333333"},
                {"type": "text", "text": f"你的總分是 {total_score} 分", "size": "lg", "color": "#000000"},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": feedback, "wrap": True, "size": "md", "color": "#555555", "margin": "md"}
            ]
        },
        "footer": {
            "type": "box", "layout": "vertical",
            "contents": [
                {"type": "button", "style": "primary", "action": {"type": "message", "label": "重新測驗", "text": "我要做憂鬱症量表"}, "color": "#8D8684FF"},
                {"type": "separator", "margin": "sm" },
                {"type": "button", "style": "primary", "action": {"type": "message", "label": "查看歷史", "text": "我要看憂鬱症量表歷史"}, "color": "#8D8684FF"}

            ]
        }
    }

    return FlexMessage(
        alt_text="董氏憂鬱量表-大專生版結果",
        contents=FlexContainer.from_json(json.dumps(bubble_json))
    )
