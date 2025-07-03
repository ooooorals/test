from linebot.models import MessageEvent, TextMessage
from handlers.reply_builder import build_schedule_message

def handle_message(event, line_bot_api):
    user_text = event.message.text

    # ユーザーの入力を解析して予定表をFlex Messageで返信
    flex_msg = build_schedule_message(user_text)
    line_bot_api.reply_message(event.reply_token, flex_msg)
