import os
from datetime import datetime, timedelta
import re
from linebot.models import FlexSendMessage, TextSendMessage
from handlers.schedule_parser import parse_schedule
from handlers.schedule_adjuster import parse_schedule_text, adjust_schedule, format_schedule

# Path to store previous schedule
SCHEDULE_FILE = "previous_schedule.txt"

def build_schedule_message(user_text: str) -> FlexSendMessage | TextSendMessage:
    try:
        # Check if the message is an adjustment command like "勉強プラス10分"
        match = re.match(r'(.+?)プラス(\d+)分', user_text.strip())
        if match and os.path.exists(SCHEDULE_FILE):
            task_name = match.group(1).strip()
            extra_minutes = int(match.group(2))
            # Load previous schedule
            with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
                previous_text = f.read()
            schedule = parse_schedule_text(previous_text)
            adjusted_schedule = adjust_schedule(schedule, task_name, extra_minutes)
            updated_text = format_schedule(adjusted_schedule)


            # Save updated schedule
            with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
                f.write(updated_text)
            return build_flex_message(adjusted_schedule)
        else:
            # Generate new schedule
            schedule_items = parse_schedule(user_text)
            # Save schedule to file
            schedule_text = "\n".join([f"{item['time']} {item['task']}" for item in schedule_items])
            with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
                f.write(schedule_text)
            return build_flex_message(schedule_items)
    except Exception:
        return TextSendMessage(text="予定表の形式が正しくありません。例：9時\n勉強2時間\n料理1時間\nお出かけ3時間")

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
