from datetime import datetime, timedelta
import re
from utils.time_utils import parse_japanese_time

def normalize_numbers(text: str) -> str:
    # 全角数字を半角に変換
    zenkaku_nums = "０１２３４５６７８９"
    hankaku_nums = "0123456789"
    trans_table = str.maketrans(zenkaku_nums, hankaku_nums)
    return text.translate(trans_table)

def parse_schedule(text: str, break_minutes: int = 10) -> list:
    text = normalize_numbers(text)  # 全角数字を半角に変換
    parts = text.split('・')
    start_time = parse_japanese_time(parts[0])
    current_time = start_time

    schedule = []
    for i, item in enumerate(parts[1:]):
        item = item.strip()
        match = re.match(r'(.+?)(?:(\d+)時間)?(?:(\d+)分)?$', item)
        if match:
            task = match.group(1).strip()
            hours = int(match.group(2)) if match.group(2) else 0
            minutes = int(match.group(3)) if match.group(3) else 0
            duration = timedelta(hours=hours, minutes=minutes)
            end_time = current_time + duration

            schedule.append({
                "time": f"{current_time.strftime('%H:%M')}~{end_time.strftime('%H:%M')}",
                "task": task
            })
            current_time = end_time

            # 次のタスクがある場合は休憩を挟む
            if i < len(parts[1:]) - 1:
                break_end = current_time + timedelta(minutes=break_minutes)
                schedule.append({
                    "time": f"{current_time.strftime('%H:%M')}~{break_end.strftime('%H:%M')}",
                    "task": "休憩"
                })
                current_time = break_end
        else:
            raise ValueError("形式が正しくありません")
    return schedule
