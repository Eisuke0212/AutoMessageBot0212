from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import random

app = Flask(__name__)

# ここに LINE Developers の値を貼り付ける
line_bot_api = LineBotApi('12KxOgaND+TgymWNCPFLtzuRrvYeNw0wwAbzFX/RkBXX4fSExSyIzI4p67OwW1kA2NrZZvP3pip/FPQ3ElEVHl3Zt/J5JgaU1HLKdeIFNWwDoP8AbbD/iHnAkKurmR3Ilj7IJOiGLcUPmlI+qSRIqAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('3b76ee35c0b4028d72c000d646bd87ea')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 1. ユーザーが送ってきたメッセージを取得
    user_message = event.message.text
    
    # 2. 送ってきた人の名前を取得してパソコン画面に出す
    profile = line_bot_api.get_profile(event.source.user_id)
    print(f"【受信】 {profile.display_name}: {user_message}")

    # 3. 返信内容を決める（条件分岐）
    
    # --- おみくじ機能 ---
    if user_message == "おみくじ":
        result = random.choice(["大吉🌟", "中吉👍", "小吉😊", "末吉🙂", "凶💀"])
        reply_text = f"【おみくじ結果】\n{result} でした！"

    # --- あいさつ機能 ---
    elif user_message == "こんにちは" or user_message == "ハロー":
        reply_text = f"{profile.display_name}さん、こんにちは！何して遊ぶ？"

    # --- 計算機能 (+, -, *, / が含まれていたら計算) ---
    elif any(op in user_message for op in ["+", "-", "*", "/"]):
        try:
            # 安全に計算するための設定
            # ※半角数字と記号（10+20など）で送る必要があります
            answer = eval(user_message, {"__builtins__": None}, {})
            reply_text = f"計算したよ！\n{user_message} = {answer}"
        except:
            reply_text = "計算できなかったよ。半角で「5*5」みたいに送ってみてね！"

    # --- それ以外の言葉（オウム返し） ---
    else:
        reply_text = f"「{user_message}」って言ったね！\n計算もできるから、例えば「5+5」って送ってみてね\nおみくじって打ってみて！" 

    # 4. LINEに返信を送る
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run(port=5000)
