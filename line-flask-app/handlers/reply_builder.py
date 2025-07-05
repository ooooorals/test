import os
import re
from datetime import datetime
from linebot.models import FlexSendMessage, TextSendMessage
from handlers.schedule_parser import parse_schedule
from handlers.schedule_adjuster import parse_schedule_text, adjust_schedule, format_schedule

# Path to store previous schedule
SCHEDULE_FILE = "previous_schedule.txt"

def extract_date_and_body(text: str):
    lines = text.strip().split("\n")
    first_line = lines[0].strip()

    # Match formats like 7/5 or 7月5日
    match = re.match(r'(\d{1,2})月/日?', first_line)
    if match:
        month, day = match.groups()
        title = f"{int(month)}月{int(day)}日の予定"
        body = "\n".join(lines[1:])
    else:
        title = "今日の予定"
        body = text

    return title, body

def build_schedule_message(user_text: str) -> FlexSendMessage | TextSendMessage:
    try:
        # Handle adjustment command
        if user_text.startswith("変更\n"):
            lines = user_text.strip().split("\n")
            if len(lines) < 2:
                return TextSendMessage(text="変更内容が見つかりません。例：変更\n勉強プラス10分")
            adjustment_text = lines[1]

            if not os.path.exists(SCHEDULE_FILE):
                return TextSendMessage(text="前回の予定が見つかりません。")

            with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
                previous_text = f.read()

            schedule = parse_schedule_text(previous_text)
            adjusted = adjust_schedule(schedule, adjustment_text)
            formatted = format_schedule(adjusted)

            with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
                f.write(formatted)

            return build_flex_message(adjusted)

        # Handle direct adjustment like "勉強プラス10分"
        match = re.match(r'(.+?)プラス(\d+)分', user_text.strip())
        if match and os.path.exists(SCHEDULE_FILE):
            adjustment_text = user_text.strip()

            with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
                previous_text = f.read()

            schedule = parse_schedule_text(previous_text)
            adjusted_schedule = adjust_schedule(schedule, adjustment_text)
            updated_text = format_schedule(adjusted_schedule)

            with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
                f.write(updated_text)

            return build_flex_message(adjusted_schedule)

        else:
            # New schedule creation
            title, body_text = extract_date_and_body(user_text)
            schedule_items = parse_schedule(body_text)

            # Save to file
            schedule_text = format_schedule(schedule_items)
            with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
                f.write(schedule_text)

            return build_flex_message(schedule_items, title=title)

    except Exception:
        return TextSendMessage(text="予定表の形式が正しくありません。例：9時\n勉強2時間\n料理1時間\nお出かけ3時間")

def build_flex_message(schedule_items: list, title: str = "今日の予定") -> FlexSendMessage:
    contents = [
        {
            "type": "text",
            "text": f"🗓️ {title}",
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
        start_str = item["start"].strftime("%H:%M")
        end_str = item["end"].strftime("%H:%M")
        time_str = f"{start_str}~{end_str}"

        contents.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": time_str,
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
        alt_text=title,
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents
            }
        }
    )
