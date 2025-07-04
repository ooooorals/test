from linebot.models import FlexSendMessage
from handlers.schedule_parser import parse_schedule
from linebot.models import TextSendMessage

def build_schedule_message(user_text: str) -> FlexSendMessage | TextSendMessage:
    try:
        schedule_items = parse_schedule(user_text)
        return build_flex_message(schedule_items)
    except Exception:
        return TextSendMessage(text="形式が正しくありません。\n例：9時\n勉強2時間\n料理1時間\nお出かけ3時間")

def build_flex_message(schedule_items):
    contents = [
        {
            "type": "text",
            "text": "🗓️ 今日の予定",
            "weight": "bold",
            "size": "xl",
            "margin": "md"
        },
        {
            "type": "separator",
            "margin": "md"
        }
    ]

    for item in schedule_items:
        contents.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": item['time'],
                    "color": "#555555",
                    "flex": 5,
                    "size": "sm",
                    "wrap": True,
                    "maxLines": 1
                },
                {
                    "type": "text",
                    "text": item['task'],
                    "size": "sm",
                    "color": "#111111",
                    "flex": 5,
                    "wrap": True,
                    "maxLines": 1
                }
            ],
            "margin": "md"
        })

    return FlexSendMessage(
        alt_text="今日の予定",
        contents={
        "type": "bubble",
        "body": {
        "type": "box",
        "layout": "vertical",
        "contents": contents
        }
      }
    )
