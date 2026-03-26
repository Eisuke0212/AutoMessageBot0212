from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import random
import time
import threading
import re

app = Flask(__name__)

# --- LINE の設定 ---
line_bot_api = LineBotApi('12KxOgaND+TgymWNCPFLtzuRrvYeNw0wwAbzFX/RkBXX4fSExSyIzI4p67OwW1kA2NrZZvP3pip/FPQ3ElEVHl3Zt/J5JgaU1HLKdeIFNWwDoP8AbbD/iHnAkKurmR3Ilj7IJOiGLcUPmlI+qSRIqAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('3b76ee35c0b4028d72c000d646bd87ea')

# データを保存する場所
user_data = {}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# --- タイマー通知用の関数 ---
def send_timer_notification(user_id, minutes):
    time.sleep(minutes * 60)
    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=f"⏰ {minutes}分経ったよ！時間です！"))
    except Exception as e:
        print(f"Push Message Error: {e}")

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text
    profile = line_bot_api.get_profile(user_id)
    
    if user_id not in user_data:
        user_data[user_id] = []

    # --- 1. 使い方ガイド (「使い方」または「ヘルプ」) ---
    if user_message in ["使い方", "ヘルプ", "help"]:
        reply_text = (
            f"🌟 {profile.display_name}さん、使い方の説明だよ！\n\n"
            "📝【宿題管理】\n"
            "・「追加 漢字」→ 宿題を入れる\n"
            "・「削除 漢字」→ 宿題を消す\n"
            "・「宿題」→ リストを見る\n"
            "・「どれ」→ ランダムに選ぶ\n\n"
            "⏳【タイマー】\n"
            "・「10分」→ 10分後に通知\n\n"
            "🔢【計算】\n"
            "・「10+20」→ 計算結果を返す\n\n"
            "✨【その他】\n"
            "・「おみくじ」→ 運勢を占う\n"
            "・それ以外 → オウム返しするよ！"
        )

    # 2. 宿題の追加
    elif user_message.startswith("追加 "):
        item = user_message.replace("追加 ", "")
        user_data[user_id].append(item)
        reply_text = f"✅「{item}」をリストに入れたよ！"

    # 3. 宿題の削除
    elif user_message.startswith("削除 "):
        item = user_message.replace("削除 ", "")
        if item in user_data[user_id]:
            user_data[user_id].remove(item)
            reply_text = f"🗑️「{item}」を消したよ。"
        else:
            reply_text = "その宿題はリストにないよ。"

    # 4. 宿題リストの確認
    elif user_message == "宿題":
        if not user_data[user_id]:
            reply_text = "今のところ宿題はないよ！「追加 〇〇」で教えてね。"
        else:
            reply_text = "📝 今の宿題リスト：\n・" + "\n・".join(user_data[user_id])

    # 5. ランダム選出
    elif user_message == "どれ":
        if not user_data[user_id]:
            reply_text = "宿題リストが空っぽだよ。「追加 宿題名」で教えて！"
        else:
            choice = random.choice(user_data[user_id])
            reply_text = f"🎯 次は「{choice}」をやってみよう！"

    # 6. タイマー設定
    elif "分" in user_message and any(c.isdigit() for c in user_message):
        try:
            m_text = "".join(filter(str.isdigit, user_message))
            minutes = int(m_text)
            threading.Thread(target=send_timer_notification, args=(user_id, minutes)).start()
            reply_text = f"⏳ {minutes}分後に教えるね。ファイト！"
        except:
            reply_text = "タイマー設定に失敗したよ。「10分」のように送ってね。"

    # 7. 計算機能
    elif any(op in user_message for op in ["+", "-", "*", "/"]):
        try:
            calc_query = re.sub(r'[^0-9+\-*/(). ]', '', user_message)
            answer = eval(calc_query)
            reply_text = f"計算結果： {answer} だよ！"
        except:
            reply_text = "計算できなかったよ。半角で送ってみてね。"

    # 8. おみくじ
    elif user_message == "おみくじ":
        result = random.choice(["大吉🌟", "中吉👍", "小吉😊", "末吉🙂", "凶💀"])
        reply_text = f"【おみくじ結果】\n{result} でした！"

    # 9. オウム返し
    else:
        reply_text = f"「{user_message}」だね！\n使い方が知りたい時は「使い方」って送ってね。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.run()
