from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# LINEのチャネル情報
LINE_CHANNEL_ACCESS_TOKEN = 'IP8ouEpLxtf95tc+xOoFSnFf3B8tK7f3dkPIlcpcHI3WDUYaHIMQQhrBfiw7NDCtTOIqQv3yd9aAt0j15PH/dsmSBRSyuVUWRyK2xQ1RUfhxQMsXIa3HESCqa/3wT+0Q0bPSNFJa9ZZGfewVnc6Y3QdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '79a82ecfc0d4e146c2d9846eaf2b6b81'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # リクエストヘッダーから署名を取得
    signature = request.headers['X-Line-Signature']

    # リクエストボディを取得
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    print(f"受信メッセージ: {user_message}")
    # 応答メッセージを送信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"あなたのメッセージ: {user_message}")
    )

if __name__ == "__main__":
    app.run()
